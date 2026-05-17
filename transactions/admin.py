from django.contrib import admin
from .models import Transaction, Contract

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_number', 'transaction_type', 'status', 'amount', 'commission', 'transaction_date']
    list_filter = ['transaction_type', 'status']
    search_fields = ['transaction_number', 'property__title', 'client__last_name']

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ['contract_number', 'title', 'contract_type', 'status', 'start_date', 'signed_date']
    list_filter = ['contract_type', 'status']
    search_fields = ['contract_number', 'title']