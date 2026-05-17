from django.contrib import admin
from .models import Client

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'client_type', 'phone', 'email', 'agency', 'created_at']
    list_filter = ['client_type', 'agency']
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'company_name']
    ordering = ['-created_at']