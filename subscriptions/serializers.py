from rest_framework import serializers
from .models import Subscription

class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Serializer for the Subscription model to be sent to the Flutter app.
    """
    # Use CharField with source to show the human-readable status like "Active"
    status = serializers.CharField(source='get_status_display')

    class Meta:
        model = Subscription
        fields = [
            'status',
            'start_date',
            'valid_until',
        ]
