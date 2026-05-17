from rest_framework import viewsets
from .models import Client
from .serializers import ClientSerializer
class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    search_fields = ['first_name','last_name','email','phone']
    filterset_fields = ['agency','client_type']
