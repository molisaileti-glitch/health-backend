from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.HealthCheckView.as_view(), name='health-check'),
    # For doctors to register their profile
    path('doctors/register/', views.DoctorRegistrationView.as_view(), name='doctor-register'),
    
    # For doctors to GET open requests, and for patients to POST a new request
    path('requests/', views.RequestListCreateView.as_view(), name='request-list-create'),
    
    # For a doctor to POST an offer on a specific request
    path('requests/<int:request_id>/offers/', views.OfferCreateView.as_view(), name='offer-create'),
    
    # For a patient to POST to accept an offer
    path('offers/<int:offer_id>/accept/', views.OfferAcceptView.as_view(), name='offer-accept'),
]
