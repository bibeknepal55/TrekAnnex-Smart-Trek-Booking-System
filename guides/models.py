from django.db import models
from accounts.models import User

class GuideProfile(models.Model):
    AVAILABILITY_CHOICES = [
        ('Available', 'Available'),
        ('On a Trek', 'On a Trek'),
        ('Busy', 'Busy'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='guide_profile')
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    experience = models.IntegerField(help_text='Years of experience')
    languages = models.CharField(max_length=255, help_text='Comma-separated')
    bio = models.TextField()
    availability = models.CharField(max_length=20, choices=AVAILABILITY_CHOICES, default='Available')
    profile_picture = models.ImageField(upload_to='guides/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.full_name} - Guide Profile"
