from django.db import models
from django.contrib.auth.models import User
from offers_app.models import OfferDetail


# Create your models here.

class Order(models.Model):

    STATUS_CHOICES = [
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled")
    ]
    customer_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    business_user = models.ForeignKey(User, on_delete=models.CASCADE)
    offer_detail = models.ForeignKey(OfferDetail, on_delete=models.CASCADE)

    title = models.CharField(max_length=255)
    revisions = models.IntegerField()
    delivery_time_in_days = models.IntegerField()
    price = models.IntegerField()
    features = models.JSONField()
    offer_type = models.CharField(max_length=255)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='in_progress')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} - {self.title} by {self.customer_user.username} for {self.business_user.username}"