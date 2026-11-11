from decimal import Decimal

from .models import Order

DHAKA_CITY_DISTRICT_KEYS = {
    'dhaka - city',
    'dhaka city',
    'dhaka',
}


def _normalize_district(district: str) -> str:
    return (district or '').strip().casefold()


def is_inside_dhaka(district: str) -> bool:
    key = _normalize_district(district)
    return key in DHAKA_CITY_DISTRICT_KEYS or key.startswith('dhaka')


def calculate_delivery_fee(delivery_method: str, district: str, upazila: str = '') -> Decimal:
    """Bangladesh-oriented shipping: Dhaka city vs outside + delivery tier."""
    _ = upazila  # reserved for future upazila-specific rules
    method = delivery_method or Order.DELIVERY_CHOICES[0][0]

    if method == 'Store Pickup':
        return Decimal('0')

    inside_dhaka = is_inside_dhaka(district)

    if method == 'Express Delivery':
        return Decimal('120') if inside_dhaka else Decimal('200')

    if method == 'Home Delivery':
        return Decimal('70') if inside_dhaka else Decimal('130')

    return Decimal('70') if inside_dhaka else Decimal('130')
