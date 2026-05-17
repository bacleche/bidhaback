from django.contrib import admin
from .models import Property, PropertyImage

class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ['title', 'property_type', 'offer_type', 'status', 'price', 'city', 'is_featured']
    list_filter = ['property_type', 'offer_type', 'status', 'city', 'is_featured']
    search_fields = ['title', 'city', 'district']
    inlines = [PropertyImageInline]