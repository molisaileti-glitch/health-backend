# api/admin.py
from django.contrib import admin
from .models import FCMToken, DoctorRequest, Offer

@admin.register(FCMToken)
class FCMTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "token", "updated_at")

@admin.register(DoctorRequest)
class DoctorRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "status", "created_at")
    list_filter = ("status",)

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ("id", "request", "doctor", "price", "eta_minutes", "accepted", "created_at")
    list_filter = ("accepted",)
