import hashlib
from decimal import Decimal
from urllib.parse import urlencode

import requests
from django.conf import settings


class SSLCommerzError(Exception):
    pass


class SSLCommerzClient:
    """Minimal SSLCommerz session + validation client (sandbox or live)."""

    def __init__(self):
        self.store_id = settings.SSLCOMMERZ_STORE_ID
        self.store_pass = settings.SSLCOMMERZ_STORE_PASSWORD
        self.api_root = settings.SSLCOMMERZ_API_ROOT.rstrip('/')
        self.is_sandbox = settings.SSLCOMMERZ_SANDBOX

    def _post(self, path: str, payload: dict) -> dict:
        if not self.store_id or not self.store_pass:
            raise SSLCommerzError('SSLCommerz is not configured.')

        url = f'{self.api_root}{path}'
        data = {
            'store_id': self.store_id,
            'store_passwd': self.store_pass,
            **payload,
        }
        response = requests.post(url, data=data, timeout=30)
        response.raise_for_status()
        body = response.json()
        if body.get('status') != 'SUCCESS' and body.get('APIConnect') != 'DONE':
            raise SSLCommerzError(body.get('failedreason') or body.get('status') or 'Payment session failed.')
        return body

    def create_session(self, order, success_url: str, fail_url: str, cancel_url: str, ipn_url: str) -> dict:
        total = Decimal(str(order.total))
        payload = {
            'total_amount': str(total),
            'currency': 'BDT',
            'tran_id': order.order_number,
            'success_url': success_url,
            'fail_url': fail_url,
            'cancel_url': cancel_url,
            'ipn_url': ipn_url,
            'cus_name': f'{order.first_name} {order.last_name}'.strip(),
            'cus_email': order.email,
            'cus_phone': order.mobile,
            'cus_add1': order.address[:250],
            'cus_city': order.district,
            'cus_postcode': '1200',
            'cus_country': 'Bangladesh',
            'shipping_method': 'NO',
            'product_name': f'TechMart Order {order.order_number}',
            'product_category': 'E-Commerce',
            'product_profile': 'general',
        }
        return self._post('/gwprocess/v4/api.php', payload)

    @staticmethod
    def verify_ipn_signature(post_data: dict) -> bool:
        verify_key = post_data.get('verify_key', '')
        verify_sign = post_data.get('verify_sign', '')
        if not verify_key or not verify_sign:
            return False

        key_list = sorted(k.strip() for k in verify_key.split('#') if k.strip())
        lines = []
        for key in key_list:
            value = post_data.get(key, '')
            lines.append(f'{key}={value}&')
        sign_string = ''.join(lines) + settings.SSLCOMMERZ_STORE_PASSWORD
        expected = hashlib.md5(sign_string.encode('utf-8')).hexdigest().upper()
        return expected == str(verify_sign).upper()

    def validate_transaction(self, val_id: str) -> dict:
        return self._post('/validator/api/validationserverAPI.php', {'val_id': val_id})
