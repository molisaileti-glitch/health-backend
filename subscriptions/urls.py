# subscriptions/urls.py

from django.urls import path
from .views import UssdMenuHandlerView, SubscriptionStatusView # <-- Add SubscriptionStatusView here

# --- Only import the one view that actually exists in your views.py file ---
from .views import UssdMenuHandlerView

urlpatterns = [
    # This is the only URL pattern we need right now for the backend.
    # It creates the endpoint for Africa's Talking to send USSD requests.
    path('ussd-menu/', UssdMenuHandlerView.as_view(), name='ussd-menu-handler'),
     # --- ADD THIS NEW URL FOR THE FLUTTER APP ---
    path('status/', SubscriptionStatusView.as_view(), name='subscription-status'),
]
