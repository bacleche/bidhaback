from django.db import models
from core.models import User

class Agency(models.Model):
    name = models.CharField(max_length=200)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_agencies')
    logo = models.ImageField(upload_to='agencies/logos/', blank=True, null=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)
    license_number = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Agence"
        verbose_name_plural = "Agences"
        ordering = ['-created_at']

class Agent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='agent_profile')
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='agents')
    employee_id = models.CharField(max_length=50, unique=True)
    specialization = models.CharField(max_length=200, blank=True)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=5.00)
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.agency.name}"

    class Meta:
        verbose_name = "Agent"
        ordering = ['-joined_at']
