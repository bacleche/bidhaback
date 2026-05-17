from django.db import models
from agencies.models import Agency, Agent

class Property(models.Model):
    TYPE_CHOICES = [('apartment','Appartement'),('house','Maison'),('villa','Villa'),('land','Terrain'),('commercial','Local Commercial'),('office','Bureau'),('warehouse','Entrepôt')]
    STATUS_CHOICES = [('available','Disponible'),('reserved','Réservé'),('sold','Vendu'),('rented','Loué'),('unavailable','Indisponible')]
    OFFER_CHOICES = [('sale','Vente'),('rent','Location'),('both','Vente & Location')]

    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='properties')
    agent = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, blank=True, related_name='properties')
    title = models.CharField(max_length=300)
    description = models.TextField()
    property_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    offer_type = models.CharField(max_length=10, choices=OFFER_CHOICES, default='sale')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    
    price = models.DecimalField(max_digits=15, decimal_places=2)
    rent_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    address = models.TextField()
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    area = models.DecimalField(max_digits=10, decimal_places=2, help_text="Surface en m²")
    bedrooms = models.PositiveIntegerField(default=0)
    bathrooms = models.PositiveIntegerField(default=0)
    floors = models.PositiveIntegerField(default=1)
    parking = models.BooleanField(default=False)
    garden = models.BooleanField(default=False)
    pool = models.BooleanField(default=False)
    security = models.BooleanField(default=False)
    furnished = models.BooleanField(default=False)
    
    is_featured = models.BooleanField(default=False)
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Bien Immobilier"
        verbose_name_plural = "Biens Immobiliers"
        ordering = ['-created_at']

class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='properties/')
    caption = models.CharField(max_length=200, blank=True)
    is_cover = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
