# Generated migration for eSewa payment integration

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0006_update_existing_booking_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='payment_status',
            field=models.CharField(
                choices=[
                    ('Initiated', 'Initiated'),
                    ('Success', 'Success'),
                    ('Failed', 'Failed')
                ],
                default='Initiated',
                max_length=20
            ),
        ),
        migrations.AlterField(
            model_name='payment',
            name='transaction_id',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='reference_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
