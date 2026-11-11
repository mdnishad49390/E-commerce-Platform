from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_giftvoucher_discount_type_giftvoucher_discount_value_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='gateway_session_key',
            field=models.CharField(blank=True, default='', max_length=120),
        ),
        migrations.AddField(
            model_name='order',
            name='gateway_transaction_id',
            field=models.CharField(blank=True, default='', max_length=120),
        ),
        migrations.AddField(
            model_name='order',
            name='payment_status',
            field=models.CharField(
                choices=[
                    ('not_required', 'Not required'),
                    ('pending', 'Pending'),
                    ('paid', 'Paid'),
                    ('failed', 'Failed'),
                ],
                default='not_required',
                max_length=20,
            ),
        ),
    ]
