from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class VerifiedAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    verification_code = models.CharField(max_length=255)
    is_verified = models.BooleanField(default=False)
    date_verified = models.DateTimeField(default=timezone.now)


# Create your models here.
