# subscriptions/serializers.py

from rest_framework import serializers
# --- IMPORT THE MODELS WE NEED ---
from .models import Subscription, CustomUser

# (Optional but Recommended) A simple serializer for the user
class UserNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username']

# --- THIS IS THE CORRECTED SERIALIZER ---
class SubscriptionSerializer(serializers.ModelSerializer):
    """
    A robust serializer for the Subscription model.
    """
    # (Optional but Recommended) Include the nested user info
    user = UserNestedSerializer(read_only=True)
    
    # We will now serialize the 'status' field directly. 
    # Your Flutter app will receive 'ACTIVE', 'INACTIVE', etc., and can handle it.
    # This is much more reliable than using 'get_status_display'.

    class Meta:
        model = Subscription
        # The fields to include in the JSON response sent to Flutter.
        fields = [
            'user',         # The nested user object
            'status',       # The raw status, e.g., "ACTIVE"
            'start_date',   # The start date of the subscription
            'valid_until',  # The expiration date
        ]

