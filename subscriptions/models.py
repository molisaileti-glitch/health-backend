from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

# ====================================================================
# CUSTOM USER MODEL
# ====================================================================
class CustomUser(AbstractUser):
    """
    Custom user model to include additional fields like phone_number and fcm_token.
    """
    # Your existing phone_number field
    phone_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    
    # --- ADDED THIS NEW FIELD ---
    # This field will store the Firebase Cloud Messaging token for push notifications.
    fcm_token = models.TextField(blank=True, null=True)
    groups = models.ManyToManyField(
       'auth.Group',
       verbose_name
       ='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="customuser_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
         verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="customuser_set",
        related_query_name="user",
    )

    def __str__(self):
        return self.username

# ====================================================================
# SUBSCRIPTION MODEL
# ====================================================================
class Subscription(models.Model):
    """
    Manages the subscription status for each user of the AfyaPlus service.
    """
    class Status(models.TextChoices):
        INACTIVE = 'INACTIVE', 'Inactive'
        ACTIVE = 'ACTIVE', 'Active'
        PAUSED = 'PAUSED', 'Paused'
        CANCELED = 'CANCELED', 'Canceled'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='afya_plus_subscription'
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.INACTIVE
    )
    start_date = models.DateTimeField(null=True, blank=True)
    valid_until = models.DateTimeField(null=True, blank=True, help_text="The date the current paid-for period ends.")
    consecutive_payment_failures = models.PositiveIntegerField(default=0, help_text="Tracks failed weekly payments for the grace period.")
    
    # Store the Africa's Talking subscription ID for recurring payments
    africastalking_subscription_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Subscription ({self.get_status_display()})"
