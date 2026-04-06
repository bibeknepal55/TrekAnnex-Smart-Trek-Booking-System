from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('superadmin', 'SuperAdmin'),
        ('admin', 'Admin'),
        ('guide', 'Guide'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    full_name = models.CharField(max_length=255)
    
    def __str__(self):
        return f"{self.username} ({self.role})"
