from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import UserSerializer, RegisterSerializer
from agencies.models import Agency
from properties.models import Property
from transactions.models import Contract
from properties.serializers import PropertySerializer
from .serializers import ClientUserSerializer
from rest_framework import generics, permissions, filters  # ← ajoute filters ici
from core import models

class ClientUserListView(generics.ListAPIView):
    serializer_class = ClientUserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'username']

    def get_queryset(self):
        return User.objects.filter(role='client').order_by('first_name', 'last_name')

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_object(self):
        return self.request.user

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        try:
            token = RefreshToken(request.data.get('refresh'))
            token.blacklist()
        except:
            pass
        return Response({'message': 'Déconnecté avec succès'})

class ClientStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        
        # 1. Nombre d'agences actives globalement
        active_agencies = Agency.objects.filter(is_active=True).count()
        
        # 2. Biens où le client a signé un contrat
        # On passe par la relation : Contract -> Transaction -> Client -> User
        signed_contracts = Contract.objects.filter(transaction__client__user=user, status='signed')
        # On passe par la relation inverse : Property -> Transaction -> Contract
        signed_properties = Property.objects.filter(transactions__contracts__in=signed_contracts).distinct()
        
        return Response({
            'active_agencies_count': active_agencies,
            'signed_contracts_count': signed_contracts.count(),
            'signed_properties': PropertySerializer(signed_properties, many=True).data
        })


from rest_framework import viewsets
from rest_framework.decorators import action
from .models import Notification
from .serializers import NotificationSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        self.get_queryset().filter(is_read=False).update(is_read=True)
        return Response({'status': 'ok'})

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notif = self.get_object()
        notif.is_read = True
        notif.save(update_fields=['is_read'])
        return Response({'status': 'ok'})

