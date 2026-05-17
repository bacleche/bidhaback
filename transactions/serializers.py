from rest_framework import serializers
from .models import Transaction, Contract
class TransactionSerializer(serializers.ModelSerializer):
    property_title = serializers.CharField(source='property.title', read_only=True)
    client_name = serializers.SerializerMethodField()
    class Meta:
        model = Transaction
        fields = '__all__'
    def get_client_name(self, obj):
        return f"{obj.client.first_name} {obj.client.last_name}"

class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = '__all__'
