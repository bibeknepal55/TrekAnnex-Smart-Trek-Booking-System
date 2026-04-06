from django.db import models
from ckeditor.fields import RichTextField

class Trek(models.Model):
    REGION_CHOICES = [
        ('Annapurna', 'Annapurna'),
        ('Everest', 'Everest'),
        ('Langtang', 'Langtang'),
        ('Mustang', 'Mustang'),
        ('Manaslu', 'Manaslu'),
        ('Dolpo', 'Dolpo'),
        ('Kanchenjunga', 'Kanchenjunga'),
        ('Makalu', 'Makalu'),
        ('Rolwaling', 'Rolwaling'),
        ('Api-Nampa', 'Api-Nampa'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'),
        ('Moderate', 'Moderate'),
        ('Difficult', 'Difficult'),
        ('Extreme', 'Extreme'),
    ]
    
    title = models.CharField(max_length=255)
    region = models.CharField(max_length=50, choices=REGION_CHOICES)
    min_duration = models.IntegerField()
    max_duration = models.IntegerField()
    max_altitude = models.IntegerField()
    season_spring = models.BooleanField(default=False)
    season_summer = models.BooleanField(default=False)
    season_autumn = models.BooleanField(default=False)
    season_winter = models.BooleanField(default=False)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    interest_scenic = models.BooleanField(default=False)
    interest_adventure = models.BooleanField(default=False)
    interest_photography = models.BooleanField(default=False)
    interest_wildlife = models.BooleanField(default=False)
    interest_cultural = models.BooleanField(default=False)
    interest_family = models.BooleanField(default=False)
    description = RichTextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    featured_image = models.ImageField(upload_to='treks/')
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']
