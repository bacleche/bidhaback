from rest_framework import viewsets, permissions
from .models import Agency, Agent
from .serializers import AgencySerializer, AgentSerializer

class AgencyViewSet(viewsets.ModelViewSet):
    queryset = Agency.objects.filter(is_active=True)
    serializer_class = AgencySerializer
    search_fields = ['name','city']
    filterset_fields = ['city','is_active']

class AgentViewSet(viewsets.ModelViewSet):
    queryset = Agent.objects.filter(is_active=True)
    serializer_class = AgentSerializer
    filterset_fields = ['agency','is_active']
