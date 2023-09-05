from django.db import models
from misclientportal.models import Appointment

class ServiceRequest(models.Model):
    SERVICE_TYPE_CHOICES = (
        ('repair', 'Repair/Troubleshoot'),
        ('software', 'Software Installation'),
        ('formatting', 'Formatting'),
        ('network', 'Network Connectivity'),
        ('internet', 'Internet Service'),
        ('other', 'Others')
    )
    department = models.CharField(max_length=100)
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPE_CHOICES)
    scheduled_response_date = models.DateField()
    scheduled_response_time = models.TimeField()
    verified_by_client = models.BooleanField()
    problem_found = models.TextField()
    recommendation = models.TextField()
    service_completed_date = models.DateField()
    service_verified_by_client_date = models.DateField()
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)

# Create your models here.
