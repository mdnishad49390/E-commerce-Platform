from django.conf import settings
from django.db import transaction
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .invoice import build_order_invoice_pdf
from .models import Order
from .payments.sslcommerz import SSLCommerzClient, SSLCommerzError


class ShippingQuoteAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        from .shipping import calculate_delivery_fee

        delivery_method = request.data.get('delivery_method', 'Home Delivery')
        district = request.data.get('district', '')
        upazila = request.data.get('upazila', '')
        fee = calculate_delivery_fee(delivery_method, district, upazila)
        return Response({'delivery_fee': str(fee)})


class InitiatePaymentAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        order_id = request.data.get('order_id')
        if not order_id:
            return Response({'error': 'order_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.filter(id=order_id, user=request.user).first()
        if not order:
            return Response({'error': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)
        if order.payment_method != 'Online Payment':
            return Response({'error': 'This order does not require online payment.'}, status=status.HTTP_400_BAD_REQUEST)
        if order.payment_status == Order.PAYMENT_STATUS_PAID:
            return Response({'error': 'Order is already paid.'}, status=status.HTTP_400_BAD_REQUEST)

        frontend = settings.FRONTEND_BASE_URL
        success_url = f'{frontend}/order-success?order={order.order_number}'
        fail_url = f'{frontend}/my-orders?payment=failed'
        cancel_url = f'{frontend}/checkout?payment=cancelled'
        ipn_url = request.build_absolute_uri('/api/orders/payments/sslcommerz/ipn/')

        try:
            client = SSLCommerzClient()
            session = client.create_session(order, success_url, fail_url, cancel_url, ipn_url)
        except SSLCommerzError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

        order.gateway_session_key = session.get('sessionkey', '')
        order.save(update_fields=['gateway_session_key', 'updated_at'])

        return Response(
            {
                'redirect_url': session.get('GatewayPageURL') or session.get('redirectGatewayURL'),
                'session_key': order.gateway_session_key,
                'order_number': order.order_number,
            },
            status=status.HTTP_200_OK,
        )


@csrf_exempt
def sslcommerz_ipn_view(request):
    if request.method != 'POST':
        return HttpResponse(status=405)

    post_data = request.POST.dict()
    if not SSLCommerzClient.verify_ipn_signature(post_data):
        return HttpResponse('INVALID', status=400)

    order_number = post_data.get('tran_id', '')
    status_text = (post_data.get('status') or '').upper()
    bank_tran_id = post_data.get('bank_tran_id', '')
    val_id = post_data.get('val_id', '')

    with transaction.atomic():
        order = Order.objects.select_for_update().filter(order_number=order_number).first()
        if not order:
            return HttpResponse('ORDER NOT FOUND', status=404)

        if status_text in {'VALID', 'VALIDATED'}:
            if val_id:
                try:
                    SSLCommerzClient().validate_transaction(val_id)
                except Exception:
                    return HttpResponse('VALIDATION FAILED', status=400)
            order.payment_status = Order.PAYMENT_STATUS_PAID
            order.gateway_transaction_id = bank_tran_id or val_id or order.gateway_transaction_id
            if order.status == 'Pending':
                order.status = 'Confirmed'
        elif status_text in {'FAILED', 'CANCELLED'}:
            order.payment_status = Order.PAYMENT_STATUS_FAILED
        else:
            return HttpResponse('IGNORED')

        order.save(update_fields=['payment_status', 'gateway_transaction_id', 'status', 'updated_at'])

    return HttpResponse('OK')


class OrderInvoicePDFAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, order_id):
        order = Order.objects.filter(id=order_id).prefetch_related('items').first()
        if not order:
            return Response({'error': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)

        is_owner = order.user_id == request.user.id
        from accounts.models import UserRoleProfile
        from accounts.roles import get_user_role

        role = get_user_role(request.user)
        is_staff = role in {UserRoleProfile.ROLE_ADMIN, UserRoleProfile.ROLE_EMPLOYEE}
        if not (is_owner or is_staff):
            return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        pdf_bytes = build_order_invoice_pdf(order)
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice-{order.order_number}.pdf"'
        return response
