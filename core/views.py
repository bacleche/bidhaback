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
