from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):

    USER_TYPES = [
        ('business', 'Business'),
        ('customer', 'Customer')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    file = models.FileField(upload_to='uploads/', blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, default='')
    tel = models.CharField(max_length=20, blank=True, default='')
    description = models.TextField(blank=True, default='')
    working_hours = models.CharField(max_length=50, blank=True, default='')
    type = models.CharField(max_length=50, choices=USER_TYPES, default='customer')
    created_at =  models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username}, {self.user.email}, ({self.type})'