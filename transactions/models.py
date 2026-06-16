from django.db import models
from properties.models import Property
from clients.models import Client
from agencies.models import Agent

from django.db import models
from properties.models import Property
from core.models import User  # ← remplace clients.models
from agencies.models import Agent

class Transaction(models.Model):
    TYPE_CHOICES = [('sale','Vente'),('rent','Location'),('purchase','Achat')]
    STATUS_CHOICES = [('pending','En cours'),('completed','Complété'),('cancelled','Annulé')]

    transaction_number = models.CharField(max_length=50, unique=True)
    transaction_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    property = models.ForeignKey(Property, on_delete=models.PROTECT, related_name='transactions')
    client = models.ForeignKey(User, on_delete=models.PROTECT, related_name='transactions', limit_choices_to={'role': 'client'})
    agent = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, related_name='transactions')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    commission = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    transaction_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_number} - {self.get_transaction_type_display()}"

    class Meta:
        verbose_name = "Transaction"
        ordering = ['-created_at']

class Contract(models.Model):
    TYPE_CHOICES = [('sale_contract','Contrat de Vente'),('lease_contract','Contrat de Bail'),('purchase_contract','Contrat d\'Achat'),('preliminary','Avant-Contrat'),('mandate','Mandat')]
    STATUS_CHOICES = [
        ('draft','Brouillon'),
        ('sent','Envoyé'),
        ('signed_owner','Signé par l\'Agence'),
        ('signed','Confirmé (Signé)'),
        ('expired','Expiré'),
        ('cancelled','Annulé')
    ]

    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='contracts')
    contract_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    contract_number = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    signed_date = models.DateField(null=True, blank=True)
    
    owner_signed = models.BooleanField(default=False)
    client_signed = models.BooleanField(default=False)
    owner_signature_date = models.DateField(null=True, blank=True)
    client_signature_date = models.DateField(null=True, blank=True)
    
    document = models.FileField(upload_to='contracts/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.contract_number} - {self.title}"

    class Meta:
        verbose_name = "Contrat"
        ordering = ['-created_at']
