from django.urls import path

from .payment_views import (
    InitiatePaymentAPIView,
    OrderInvoicePDFAPIView,
    ShippingQuoteAPIView,
    sslcommerz_ipn_view,
)
from .views import (
    CancelOrderAPIView,
    CreateOrderAPIView,
    MyOrdersAPIView,
    ValidateCouponAPIView,
    ValidateGiftVoucherAPIView,
)


urlpatterns = [
    path(
        'shipping-quote/',
        ShippingQuoteAPIView.as_view(),
        name='shipping-quote',
    ),
    path(
        'initiate-payment/',
        InitiatePaymentAPIView.as_view(),
        name='initiate-payment',
    ),
    path(
        'payments/sslcommerz/ipn/',
        sslcommerz_ipn_view,
        name='sslcommerz-ipn',
    ),
    path(
        '<int:order_id>/invoice/',
        OrderInvoicePDFAPIView.as_view(),
        name='order-invoice-pdf',
    ),
    path(
        'coupons/validate/',
        ValidateCouponAPIView.as_view(),
        name='validate-coupon'
    ),
    path(
        'vouchers/validate/',
        ValidateGiftVoucherAPIView.as_view(),
        name='validate-gift-voucher'
    ),
    path(
        'create/',
        CreateOrderAPIView.as_view(),
        name='create-order'
    ),

    path(
        '<int:order_id>/cancel/',
        CancelOrderAPIView.as_view(),
        name='cancel-order'
    ),

    path(
        'my-orders/',
        MyOrdersAPIView.as_view(),
        name='my-orders'
    ),
]