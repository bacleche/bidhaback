from django.db import models
from core.models import User
from properties.models import Property
from agencies.models import Agency, Agent


class ContactRequest(models.Model):
    """Client contacte l'agent assigné à un bien"""
    STATUS_CHOICES = [('pending','En attente'),('read','Lu'),('replied','Répondu'),('closed','Clôturé')]
    
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='contact_requests')
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contact_requests')
    agent = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, blank=True, related_name='contact_requests')
    message = models.TextField(default="J'aimerais en savoir un peu plus sur ce bien.")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Demande de contact"

    def __str__(self):
        return f"Contact {self.client} → {self.property}"


class Message(models.Model):
    """Messages dans le fil d'une demande de contact"""
    contact_request = models.ForeignKey(ContactRequest, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Msg de {self.sender} ({self.created_at:%d/%m %H:%M})"


class VisitRequest(models.Model):
    """Client demande une visite — agent accepte/reprogramme/rejette"""
    STATUS_CHOICES = [
        ('pending','En attente'),
        ('accepted','Acceptée'),
        ('rescheduled','Reprogrammée'),
        ('rejected','Rejetée'),
        ('done','Effectuée'),
    ]

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='visit_requests')
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='visit_requests')
    agent = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, blank=True, related_name='visit_requests')
    requested_date = models.DateTimeField()
    rescheduled_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    agent_notes = models.TextField(blank=True, help_text="Notes ou motif de rejet/reprogrammation")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Demande de visite"

    def __str__(self):
        return f"Visite {self.client} → {self.property} ({self.status})"


class Complaint(models.Model):
    """Client émet une plainte adressée à l'agency_owner"""
    STATUS_CHOICES = [('open','Ouverte'),('in_progress','En traitement'),('resolved','Résolue'),('closed','Clôturée')]
    CATEGORY_CHOICES = [
        ('service','Qualité de service'),
        ('agent','Comportement agent'),
        ('property','Information bien erronée'),
        ('transaction','Problème transaction'),
        ('other','Autre'),
    ]

    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='complaints')
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='complaints')
    property = models.ForeignKey(Property, on_delete=models.SET_NULL, null=True, blank=True, related_name='complaints')
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='other')
    subject = models.CharField(max_length=300)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    owner_response = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Plainte"

    def __str__(self):
        return f"Plainte #{self.id} — {self.subject[:40]}"