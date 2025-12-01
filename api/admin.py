# api/admin.py

from django.contrib import admin
from .models import DoctorProfile, Request, Offer

# This allows you to see and edit Doctor Profiles in the admin dashboard
@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'region', 'phone_number')
    search_fields = ('full_name', 'region', 'user__username')

# This allows you to see and edit Requests in the admin dashboard
@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('patient__username', 'symptoms')

# This allows you to see and edit Offers in the admin dashboard
@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('id', 'doctor', 'request_id', 'price', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('doctor__username', 'request__patient__username')

    def request_id(self, obj):
        return obj.request.id
