from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('OPS', 'Operations User'),
        ('CLIENT', 'Client User'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)



class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)