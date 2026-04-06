# Generated migration for payment status workflow changes

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0004_booking_payment_status_payment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='status',
            field=models.CharField(
                choices=[
                    ('Pending', 'Pending'),
                    ('Approved', 'Approved'),
                    ('Confirmed', 'Confirmed'),
                    ('Cancelled', 'Cancelled')
                ],
                default='Pending',
                max_length=20
            ),
        ),
        migrations.AlterField(
            model_name='booking',
            name='payment_status',
            field=models.CharField(
                choices=[
                    ('Not Initiated', 'Not Initiated'),
                    ('Partial Paid', 'Partial Paid'),
                    ('Paid', 'Paid'),
                    ('Failed', 'Failed')
                ],
                default='Not Initiated',
                max_length=20
            ),
        ),
    ]
