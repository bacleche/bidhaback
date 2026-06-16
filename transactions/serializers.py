from rest_framework import serializers
from .models import Transaction, Contract

class TransactionSerializer(serializers.ModelSerializer):
    property_title = serializers.CharField(source='property.title', read_only=True)
    property_city = serializers.CharField(source='property.city', read_only=True)
    client_name = serializers.SerializerMethodField()
    agent_name = serializers.SerializerMethodField()
    transaction_number = serializers.CharField(read_only=True)
    transaction_date = serializers.DateField(required=False)
    commission = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    contract_exists = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = '__all__'

    def get_client_name(self, obj):
        return obj.client.get_full_name() or obj.client.username  # ← User direct

    def get_agent_name(self, obj):
        if obj.agent:
            return obj.agent.user.get_full_name() or str(obj.agent.user)
        return None

    def get_contract_exists(self, obj):
        # Vérifie si un contrat existe pour cette transaction
        return Contract.objects.filter(transaction=obj).exists()

        
class ContractSerializer(serializers.ModelSerializer):
    client_name = serializers.SerializerMethodField()
    property_title = serializers.SerializerMethodField()
    agent_name = serializers.SerializerMethodField()

    # Auto-générés côté serveur
    contract_number = serializers.CharField(read_only=True)
    start_date = serializers.DateField(required=False)

    class Meta:
        model = Contract
        fields = '__all__'

    def get_client_name(self, obj):
        try:
            return f"{obj.transaction.client.first_name} {obj.transaction.client.last_name}".strip()
        except Exception:
            return None

    def get_property_title(self, obj):
        try:
            return obj.transaction.property.title
        except Exception:
            return None

    def get_agent_name(self, obj):
        try:
            return obj.transaction.agent.user.get_full_name()
        except Exception:
            return None
