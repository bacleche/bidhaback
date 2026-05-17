from django.contrib import admin
from .models import Agency, Agent

@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'phone', 'email', 'is_active', 'created_at']
    list_filter = ['city', 'is_active']
    search_fields = ['name', 'email']

@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ['user', 'agency', 'employee_id', 'commission_rate', 'is_active']
    list_filter = ['agency', 'is_active']
    search_fields = ['user__first_name', 'user__last_name', 'employee_id']