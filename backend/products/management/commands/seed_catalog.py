from django.core.management.base import BaseCommand

from products.models import Brand, Category, Product


PRODUCTS = [
    {
        'category_slug': 'electronics',
        'category_name': 'Electronics',
        'category_description': 'Everyday electronics and accessories.',
        'brand_name': 'Logitech',
        'brand_slug': 'logitech',
        'name': 'Logitech MX Master 3S Wireless Mouse',
        'slug': 'logitech-mx-master-3s-wireless-mouse',
        'sku': 'LOGI-MX-MASTER-3S',
        'description': (
            'A productivity-focused wireless mouse with an 8,000 DPI sensor, '
            'Quiet Clicks, and a MagSpeed scroll wheel.'
        ),
        'price': '12500.00',
        'stock': 12,
    },
    {
        'category_slug': 'laptops',
        'category_name': 'Laptops',
        'category_description': 'Laptops for work, study, and play.',
        'brand_name': 'Lenovo',
        'brand_slug': 'lenovo',
        'name': 'Lenovo IdeaPad Slim 5 14IMH9',
        'slug': 'lenovo-ideapad-slim-5-14imh9',
        'sku': 'LEN-IPS5-14IMH9',
        'description': (
            'A slim 14-inch laptop powered by an Intel Core Ultra 5 processor, '
            'with 16 GB memory and a 512 GB SSD.'
        ),
        'price': '109000.00',
        'stock': 8,
    },
    {
        'category_slug': 'cameras',
        'category_name': 'Cameras',
        'category_description': 'Digital cameras and photography gear.',
        'brand_name': 'Sony',
        'brand_slug': 'sony',
        'name': 'Sony Alpha a6400 with 16-50mm Lens',
        'slug': 'sony-alpha-a6400-16-50mm-lens',
        'sku': 'SONY-ILCE6400L',
        'description': (
            'A mirrorless APS-C camera with a 24.2 MP sensor, fast autofocus, '
            'and 4K video recording, supplied with a 16-50mm kit lens.'
        ),
        'price': '92000.00',
        'stock': 6,
    },
    {
        'category_slug': 'smartphones',
        'category_name': 'SMARTPHONES',
        'category_description': 'Smartphones from leading brands.',
        'brand_name': 'OnePlus',
        'brand_slug': 'oneplus',
        'name': 'OnePlus 13 12GB/256GB',
        'slug': 'oneplus-13-12gb-256gb',
        'sku': 'ONEPLUS-13-12-256',
        'description': (
            'A flagship smartphone with a 6.82-inch QHD+ AMOLED display, '
            'Snapdragon 8 Elite processor, and 12 GB memory.'
        ),
        'price': '99900.00',
        'stock': 10,
    },
    {
        'category_slug': 'printers',
        'category_name': 'PRINTERS',
        'category_description': 'Printers and printing supplies.',
        'brand_name': 'Brother',
        'brand_slug': 'brother',
        'name': 'Brother DCP-T720DW Ink Tank Printer',
        'slug': 'brother-dcp-t720dw-ink-tank-printer',
        'sku': 'BRO-DCP-T720DW',
        'description': (
            'A refillable ink tank all-in-one printer with print, scan, and '
            'copy functions, wireless connectivity, and automatic duplex printing.'
        ),
        'price': '34500.00',
        'stock': 7,
    },
    {
        'category_slug': 'tv',
        'category_name': 'TV',
        'category_description': 'Smart televisions and home entertainment.',
        'brand_name': 'SAMSUNG',
        'brand_slug': 'samsung',
        'name': 'Samsung 55-inch Q80D QLED 4K Smart TV',
        'slug': 'samsung-55-inch-q80d-qled-4k-smart-tv',
        'sku': 'SAM-QE55Q80D',
        'description': (
            "A 55-inch 4K QLED smart television from Samsung's Q80D series, "
            'with Quantum HDR and built-in streaming apps.'
        ),
        'price': '169000.00',
        'stock': 5,
    },
]


class Command(BaseCommand):
    help = 'Add a set of real products across the store categories.'

    def handle(self, *args, **options):
        created_count = 0

        for item in PRODUCTS:
            category, _ = Category.objects.get_or_create(
                slug=item['category_slug'],
                defaults={
                    'name': item['category_name'],
                    'description': item['category_description'],
                    'is_active': True,
                },
            )
            brand, _ = Brand.objects.get_or_create(
                slug=item['brand_slug'],
                defaults={'name': item['brand_name'], 'is_active': True},
            )
            _, created = Product.objects.get_or_create(
                slug=item['slug'],
                defaults={
                    'category': category,
                    'brand': brand,
                    'name': item['name'],
                    'sku': item['sku'],
                    'description': item['description'],
                    'price': item['price'],
                    'stock': item['stock'],
                    'is_active': True,
                    'is_featured': False,
                },
            )
            created_count += int(created)

        self.stdout.write(
            self.style.SUCCESS(
                f'Catalog seed complete: added {created_count} products.'
            )
        )
