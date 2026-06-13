from rest_framework import viewsets, permissions
from .models import Client
from .serializers import ClientSerializer
from agencies.views import get_user_agency

class ClientViewSet(viewsets.ModelViewSet):
    serializer_class = ClientSerializer
    search_fields = ['first_name','last_name','email','phone']
    filterset_fields = ['agency','client_type']

    def get_queryset(self):
        user = self.request.user
        queryset = Client.objects.all()
        if not user.is_authenticated:
            return Client.objects.none()
        if user.role == 'admin':
            return queryset
        agency = get_user_agency(user)
        if agency:
            return queryset.filter(agency=agency)
        return Client.objects.none()
