from django.db import models
from django.conf import settings

# This model stores the doctor-specific information.
# It's linked one-to-one with the main User model.
class DoctorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='doctor_profile')
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    region = models.CharField(max_length=100)
    
    def __str__(self):
        return f"Dr. {self.full_name}"

# This model stores the patient's request for help.
class Request(models.Model):
    STATUS_CHOICES = [('open', 'Open'), ('closed', 'Closed')]

    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='requests')
    symptoms = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request by {self.patient.username} ({self.status})"

# This model stores a doctor's bid/offer on a specific request.
class Offer(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')]

    request = models.ForeignKey(Request, related_name='offers', on_delete=models.CASCADE)
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='offers')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    eta_minutes = models.IntegerField(help_text="Estimated time of arrival in minutes")
    message = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Offer by {self.doctor.username} for {self.price} on Request #{self.request.id}"
