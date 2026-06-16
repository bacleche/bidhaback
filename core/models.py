from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [('admin','Administrateur'),('agency_owner','Propriétaire Agence'),('agent','Agent'),('client','Client')]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.role})"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    category = models.CharField(max_length=50)
    related_id = models.IntegerField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

# LA FONCTION DOIT ÊTRE ICI, AU NIVEAU DU MODULE (PAS DANS LA CLASSE)
    def create_notification(user, title, message, category, related_id=None):
        return Notification.objects.create(
            user=user, 
            title=title, 
            message=message, 
            category=category, 
            related_id=related_id
        )