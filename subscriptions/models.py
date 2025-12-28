from django.db import models
from django.conf import settings

class Subscription(models.Model):
    """
    Manages the subscription status for each user of the AfyaPlus service.
    """
    class Status(models.TextChoices):
        INACTIVE = 'INACTIVE', 'Inactive'  # User has never subscribed or has canceled and can re-subscribe.
        ACTIVE = 'ACTIVE', 'Active'      # User is currently subscribed and paid up.
        PAUSED = 'PAUSED', 'Paused'      # Grace period ended due to payment failure; benefits suspended.
        CANCELED = 'CANCELED', 'Canceled'  # User actively chose to stop the service.

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
