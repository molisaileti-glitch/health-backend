# api/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("health/", views.health, name="health"),
    path("save-fcm-token/", views.save_fcm_token, name="save_fcm_token"),
    path("requests/create/", views.create_request, name="create_request"),
    path("requests/", views.list_patient_requests, name="list_patient_requests"),
    path("doctor/requests/", views.list_open_requests, name="list_open_requests"),  # doctors poll this
    path("requests/<int:request_id>/offer/", views.create_offer, name="create_offer"),
    path("offers/<int:offer_id>/accept/", views.accept_offer, name="accept_offer"),
]
