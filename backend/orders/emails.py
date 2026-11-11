import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def _send(recipient: str, subject: str, message: str) -> None:
    if not recipient:
        return
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient],
            fail_silently=False,
        )
    except Exception:
        logger.exception('Failed to send email to %s', recipient)


def send_order_confirmation(order) -> None:
    lines = [
        f'Hello {order.first_name},',
        '',
        f'Thank you for your order {order.order_number}.',
        f'Status: {order.status}',
        f'Payment: {order.payment_method}',
        f'Total: ৳{order.total}',
        '',
        'We will notify you when your order status changes.',
        '',
        f'— {settings.EMAIL_BRAND_NAME}',
    ]
    _send(order.email, f'Order {order.order_number} confirmed', '\n'.join(lines))


def send_order_status_update(order, previous_status: str) -> None:
    lines = [
        f'Hello {order.first_name},',
        '',
        f'Your order {order.order_number} status changed.',
        f'Previous: {previous_status}',
        f'Current: {order.status}',
        '',
        f'— {settings.EMAIL_BRAND_NAME}',
    ]
    _send(order.email, f'Order {order.order_number} — {order.status}', '\n'.join(lines))
