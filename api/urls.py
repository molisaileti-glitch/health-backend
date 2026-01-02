# api/urls.py

from django.urls import path, include
from . import views

# --- IMPORT THE NEW VIEW FROM THE SUBSCRIPTIONS APP ---
from subscriptions.views import SaveFcmTokenView

urlpatterns = [
    path('health/', views.HealthCheckView.as_view(), name='health-check'),
    
    # Existing app paths
    path('doctors/register/', views.DoctorRegistrationView.as_view(), name='doctor-register'),
    path('requests/', views.RequestListCreateView.as_view(), name='request-list-create'),
    path('requests/<int:request_id>/offers/', views.OfferCreateView.as_view(), name='offer-create'),
    path('offers/<int:offer_id>/accept/', views.OfferAcceptView.as_view(), name='offer-accept'),
    
    # --- ADD THE CORRECT FCM TOKEN URL HERE ---
    # This now correctly handles calls to /api/save-fcm-token/
    path('save-fcm-token/', SaveFcmTokenView.as_view(), name='save-fcm-token'),

    # This path for subscriptions remains the same
    path('subscriptions/', include('subscriptions.urls')),
]
