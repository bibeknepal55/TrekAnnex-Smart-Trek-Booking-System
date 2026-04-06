from django.db import models
from accounts.models import User
from treks.models import Trek
from guides.models import GuideProfile
from django.utils import timezone
from datetime import timedelta
import uuid

class Booking(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('Not Initiated', 'Not Initiated'),
        ('Partial Paid', 'Partial Paid'),
        ('Paid', 'Paid'),
        ('Failed', 'Failed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    trek = models.ForeignKey(Trek, on_delete=models.CASCADE, related_name='bookings')
    guide = models.ForeignKey(GuideProfile, on_delete=models.SET_NULL, null=True, related_name='bookings')
    guide2 = models.ForeignKey(GuideProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings_backup1')
    guide3 = models.ForeignKey(GuideProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings_backup2')
    start_date = models.DateField()
    num_travellers = models.IntegerField(default=1)
    special_requests = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    payment_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Not Initiated')
    transaction_uuid = models.UUIDField(default=uuid.uuid4, editable=False, null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.trek.title}"
    
    def is_payment_expired(self):
        if self.approved_at and self.status == 'Approved':
            return timezone.now() > self.approved_at + timedelta(hours=48)
        return False
    
    class Meta:
        ordering = ['-created_at']

class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('Initiated', 'Initiated'),
        ('Success', 'Success'),
        ('Failed', 'Failed'),
    ]
    
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Initiated')
    transaction_id = models.CharField(max_length=255, unique=True)  # Our generated ID
    reference_id = models.CharField(max_length=255, blank=True, null=True)  # eSewa's refId
    payment_method = models.CharField(max_length=50, default='eSewa')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Payment #{self.id} - {self.booking.user.username} - NPR {self.amount_paid}"
    
    class Meta:
        ordering = ['-created_at']
