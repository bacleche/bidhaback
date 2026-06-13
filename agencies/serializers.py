from rest_framework import serializers
from .models import Agency, Agent
from core.serializers import UserSerializer

class AgencySerializer(serializers.ModelSerializer):
    agents_count = serializers.SerializerMethodField()
    class Meta:
        model = Agency
        fields = '__all__'
        read_only_fields = ['owner']
    def get_agents_count(self, obj):
        return obj.agents.filter(is_active=True).count()

class AgentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    agency_name = serializers.CharField(source='agency.name', read_only=True)
    class Meta:
        model = Agent
        fields = '__all__'
