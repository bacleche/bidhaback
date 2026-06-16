from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Property, PropertyImage
from .serializers import PropertySerializer, PropertyImageSerializer

from agencies.views import get_user_agency

class PropertyViewSet(viewsets.ModelViewSet):
    serializer_class = PropertySerializer
    search_fields = ['title','city','district','description']
    filterset_fields = ['property_type','offer_type','status','city','is_featured','agency']
    ordering_fields = ['price','created_at','area','views_count']
    ordering = ['-created_at']

    def get_serializer_context(self):
        return {**super().get_serializer_context(), 'request': self.request}

    def get_queryset(self):
        user = self.request.user
        queryset = Property.objects.all()
        if not user.is_authenticated or user.role == 'client':
            return queryset.filter(status='available')
        if user.role == 'admin':
            return queryset
        agency = get_user_agency(user)
        if agency:
            return queryset.filter(agency=agency)
        return Property.objects.none()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.views_count += 1
        instance.save(update_fields=['views_count'])
        return super().retrieve(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        featured = Property.objects.filter(is_featured=True, status='available')[:8]
        return Response(PropertySerializer(featured, many=True, context={'request': request}).data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def request_acquisition(self, request, pk=None):
        import random
        from django.utils import timezone
        from clients.models import Client
        from transactions.models import Transaction, Contract
        
        property_obj = self.get_object()
        user = request.user
        
        if user.role != 'client':
            return Response({'detail': 'Seuls les clients connectés peuvent demander l\'acquisition d\'un bien.'}, status=400)
        
        client, created = Client.objects.get_or_create(
            user=user,
            defaults={
                'first_name': user.first_name or user.username,
                'last_name': user.last_name or '',
                'email': user.email or '',
                'phone': user.phone or '',
                'agency': property_obj.agency
            }
        )
        
        if not client.agency:
            client.agency = property_obj.agency
            client.save(update_fields=['agency'])

        txn_number = f"TXN-{random.randint(10000, 99999)}"
        txn_type = 'rent' if property_obj.offer_type == 'rent' else 'sale'
        
        amount = property_obj.price
        if txn_type == 'rent' and property_obj.rent_price:
            amount = property_obj.rent_price
            
        commission_rate = property_obj.agent.commission_rate if property_obj.agent else 5
        commission = amount * commission_rate / 100
        
        transaction = Transaction.objects.create(
            transaction_number=txn_number,
            transaction_type=txn_type,
            status='pending',
            property=property_obj,
            client=client,
            agent=property_obj.agent,
            amount=amount,
            commission=commission,
            transaction_date=timezone.now().date(),
            notes=f"Demande d'acquisition initiée par le client {user.get_full_name() or user.username}."
        )

        ctr_number = f"CTR-{random.randint(10000, 99999)}"
        ctr_type = 'lease_contract' if txn_type == 'rent' else 'sale_contract'
        
        contract = Contract.objects.create(
            transaction=transaction,
            contract_type=ctr_type,
            status='draft',
            contract_number=ctr_number,
            title=f"Contrat d'acquisition - {property_obj.title}",
            content=f"Contrat préliminaire pour le bien '{property_obj.title}' situé à {property_obj.address}, {property_obj.city}.\nType de transaction : {transaction.get_transaction_type_display()}.\nMontant : {transaction.amount} FCFA.\nCe contrat est au statut brouillon en attente de signature par l'agence.",
            start_date=timezone.now().date()
        )
        
        property_obj.status = 'reserved'
        property_obj.save(update_fields=['status'])

        from core.models import create_notification
        
        # Notifier l'agency owner
        create_notification(
            user=property_obj.agency.owner,
            title="Nouvelle demande d'acquisition",
            message=f"Le client {user.get_full_name() or user.username} a initié une demande d'acquisition pour le bien '{property_obj.title}'.",
            category="transaction",
            related_id=transaction.id
        )
        
        # Notifier le client
        create_notification(
            user=user,
            title="Demande d'acquisition enregistrée",
            message=f"Votre demande pour le bien '{property_obj.title}' a été enregistrée. Le contrat préliminaire {contract.contract_number} est en cours de préparation.",
            category="contract",
            related_id=contract.id
        )

        return Response({
            'message': 'Votre demande d\'acquisition a été enregistrée avec succès. La transaction et le contrat brouillon ont été générés.',
            'transaction_id': transaction.id,
            'contract_id': contract.id,
            'contract_number': contract.contract_number
        }, status=201)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        from django.db.models import Count
        return Response({
            'total': Property.objects.count(),
            'available': Property.objects.filter(status='available').count(),
            'sold': Property.objects.filter(status='sold').count(),
            'rented': Property.objects.filter(status='rented').count(),
            'by_type': list(Property.objects.values('property_type').annotate(count=Count('id'))),
        })


class PropertyImageViewSet(viewsets.ModelViewSet):
    queryset = PropertyImage.objects.all()
    serializer_class = PropertyImageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_context(self):
        return {**super().get_serializer_context(), 'request': self.request}