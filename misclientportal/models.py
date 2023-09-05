from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class Appointment(models.Model):
    FULL_NAME_MAX_LENGTH = 100
    EMAIL_MAX_LENGTH = 254
    PHONE_NUMBER_MAX_LENGTH = 15
    DEVICE_TYPE_MAX_LENGTH = 50
    DEVICE_MODEL_MAX_LENGTH = 50
    ISSUE_MAX_LENGTH = 500
    NOTES_MAX_LENGTH = 500

    full_name = models.CharField(_('Full Name'), max_length=FULL_NAME_MAX_LENGTH)
    email = models.EmailField(_('Email'), max_length=EMAIL_MAX_LENGTH)
    phone_number = models.CharField(_('Phone Number'), max_length=PHONE_NUMBER_MAX_LENGTH)
    device_type = models.CharField(_('Device Type'), max_length=DEVICE_TYPE_MAX_LENGTH)
    device_model = models.CharField(_('Device Model'), max_length=DEVICE_MODEL_MAX_LENGTH)
    issue_description = models.TextField(_('Issue Description'), max_length=ISSUE_MAX_LENGTH)
    notes = models.TextField(_('Notes'), max_length=NOTES_MAX_LENGTH, blank=True, null=True)

    appointment_date = models.DateField(_('Appointment Date'))
    appointment_time = models.TimeField(_('Appointment Time'))

    STATUS_CHOICES = (
        ('PENDING', _('Pending')),
        ('IN_PROGRESS', _('In Progress')),
        ('COMPLETED', _('Completed')),
        ('TO_FOLLOW_UP', _('TO_FOLLOW_UP')),
    )
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='PENDING')

    timestamp = models.DateTimeField(_('Timestamp'), auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = _('Appointment')
        verbose_name_plural = _('Appointments')

    def __str__(self):
        return f'{self.full_name} - {self.appointment_date} {self.appointment_time}'


# Create your models here.
