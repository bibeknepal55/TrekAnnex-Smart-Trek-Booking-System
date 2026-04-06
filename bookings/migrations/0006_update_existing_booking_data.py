# Data migration script to update existing bookings to new status values
# Run this after applying the model migration

from django.db import migrations


def update_existing_bookings(apps, schema_editor):
    Booking = apps.get_model('bookings', 'Booking')
    
    # Update payment_status from 'Unpaid' to 'Not Initiated'
    Booking.objects.filter(payment_status='Unpaid').update(payment_status='Not Initiated')
    
    # Update booking status from 'Payment Pending' to 'Approved'
    # These bookings were waiting for payment, so they should be 'Approved'
    Booking.objects.filter(status='Payment Pending').update(status='Approved')
    
    print("✓ Updated payment_status: 'Unpaid' → 'Not Initiated'")
    print("✓ Updated booking status: 'Payment Pending' → 'Approved'")


def reverse_migration(apps, schema_editor):
    Booking = apps.get_model('bookings', 'Booking')
    
    # Reverse the changes
    Booking.objects.filter(payment_status='Not Initiated').update(payment_status='Unpaid')
    Booking.objects.filter(status='Approved', payment_status='Not Initiated').update(status='Payment Pending')


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0005_update_payment_status_choices'),
    ]

    operations = [
        migrations.RunPython(update_existing_bookings, reverse_migration),
    ]
