from django.db import models
from core.models import User
from agencies.models import Agency

class Client(models.Model):
    TYPE_CHOICES = [('individual','Particulier'),('company','Entreprise')]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile', null=True, blank=True)
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='clients')
    client_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='individual')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    id_number = models.CharField(max_length=50, blank=True)
    company_name = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "Client"
        ordering = ['-created_at']
