from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """
    Custom user model for doctors & patients
    """
    is_doctor = models.BooleanField(default=False)
    is_patient = models.BooleanField(default=True)

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """
    Stores FCM tokens for push notifications
    """
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="subscriptions"
    )
    fcm_token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.fcm_token[:10]}"
