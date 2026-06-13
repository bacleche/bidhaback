from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Agency, Agent
from .serializers import AgencySerializer, AgentSerializer
from django.contrib.auth import get_user_model

def get_user_agency(user):
    if not user or not user.is_authenticated:
        return None
    if user.role == 'agency_owner':
        return user.owned_agencies.filter(is_active=True).first()
    elif user.role == 'agent':
        return user.agent_profile.agency if hasattr(user, 'agent_profile') else None
    return None


User = get_user_model()

class IsAgencyOwnerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.role in ['admin', 'agency_owner']

class AgencyViewSet(viewsets.ModelViewSet):
    queryset = Agency.objects.filter(is_active=True)
    serializer_class = AgencySerializer
    search_fields = ['name','city']
    filterset_fields = ['city','is_active']

    @action(detail=False, methods=['get', 'post'], permission_classes=[permissions.IsAuthenticated])
    def mine(self, request):
        user = request.user
        if user.role != 'agency_owner':
            return Response({'detail': 'Seul le rôle Propriétaire d\'Agence peut accéder à cette ressource.'}, status=403)
        
        agency = Agency.objects.filter(owner=user).first()
        if request.method == 'GET':
            if not agency:
                return Response({'has_agency': False})
            return Response({
                'has_agency': True,
                'agency': AgencySerializer(agency).data
            })
        elif request.method == 'POST':
            if agency:
                return Response({'detail': 'Vous possédez déjà une agence.'}, status=400)
            
            serializer = AgencySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(owner=user)
                return Response({'has_agency': True, 'agency': serializer.data}, status=201)
            return Response(serializer.errors, status=400)

# class AgentViewSet(viewsets.ModelViewSet):
#     serializer_class = AgentSerializer
#     filterset_fields = ['agency','is_active']

#     def get_queryset(self):
#         user = self.request.user
#         queryset = Agent.objects.filter(is_active=True)
#         if not user.is_authenticated:
#             return Agent.objects.none()
#         if user.role == 'admin':
#             return queryset
#         agency = get_user_agency(user)
#         if agency:
#             return queryset.filter(agency=agency)
#         return Agent.objects.none()


class AgentViewSet(viewsets.ModelViewSet):
    serializer_class = AgentSerializer
    filterset_fields = ['agency', 'is_active']
    permission_classes = [IsAgencyOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Agent.objects.none()
        if user.role == 'admin':
            return Agent.objects.filter(is_active=True)
        agency = get_user_agency(user)
        if agency:
            return Agent.objects.filter(agency=agency, is_active=True)
        return Agent.objects.none()

    def create(self, request, *args, **kwargs):
        user = request.user

        # Déterminer l'agence cible
        if user.role == 'agency_owner':
            agency = Agency.objects.filter(owner=user, is_active=True).first()
            if not agency:
                return Response({'detail': 'Vous n\'avez pas d\'agence active.'}, status=400)
        elif user.role == 'admin':
            agency_id = request.data.get('agency')
            if not agency_id:
                return Response({'detail': 'agency requis pour admin.'}, status=400)
            agency = Agency.objects.filter(id=agency_id, is_active=True).first()
            if not agency:
                return Response({'detail': 'Agence introuvable.'}, status=404)
        else:
            return Response({'detail': 'Non autorisé.'}, status=403)

        data = request.data
        # Créer le User avec rôle agent
        agent_user = User.objects.create_user(
            username=data.get('username'),
            email=data.get('email', ''),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            password=data.get('password'),
            phone=data.get('phone', ''),
            role='agent',
        )

        agent = Agent.objects.create(
            user=agent_user,
            agency=agency,
            employee_id=data.get('employee_id', f'AGT-{agent_user.id}'),
            specialization=data.get('specialization', ''),
            commission_rate=data.get('commission_rate', 5.00),
        )

        return Response(AgentSerializer(agent).data, status=201)