from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Client
from .serializers import ClientSerializer
from agencies.views import get_user_agency
from agencies.models import Agent

class ClientViewSet(viewsets.ModelViewSet):
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    filterset_fields = ['agency', 'client_type']

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Client.objects.none()
        if user.role == 'admin':
            return Client.objects.all()
        # Agency owner → clients de son agence
        agency = get_user_agency(user)
        if agency:
            return Client.objects.filter(agency=agency)
        # Agent → clients de l'agence où il travaille
        try:
            agent_obj = Agent.objects.get(user=user)
            if agent_obj.agency:
                return Client.objects.filter(agency=agent_obj.agency)
        except Agent.DoesNotExist:
            pass
        return Client.objects.none()
