# subscriptions/urls.py

from django.urls import path
# --- EDIT THIS LINE ---
from .views import UssdMenuHandlerView, SubscriptionStatusView, SaveFcmTokenView 

urlpatterns = [
    # This path remains unchanged
    path('ussd-menu/', UssdMenuHandlerView.as_view(), name='ussd-menu-handler'),
     
    # This path also remains unchanged. It handles /api/subscriptions/status/
    path('status/', SubscriptionStatusView.as_view(), name='subscription-status'),
    
    # --- ADD THIS NEW PATH ---
    # This will handle requests to /api/subscriptions/save-fcm-token/
    path('save-fcm-token/', SaveFcmTokenView.as_view(), name='save-fcm-token'),
]
