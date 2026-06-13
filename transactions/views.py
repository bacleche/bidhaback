from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count
from .models import Transaction, Contract
from .serializers import TransactionSerializer, ContractSerializer
from agencies.views import get_user_agency

class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    filterset_fields = ['transaction_type','status','agent']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        queryset = Transaction.objects.all()
        if not user.is_authenticated:
            return Transaction.objects.none()
        if user.role == 'admin':
            return queryset
        if user.role == 'client':
            return queryset.filter(client__user=user)
        agency = get_user_agency(user)
        if agency:
            return queryset.filter(property__agency=agency)
        return Transaction.objects.none()

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total_revenue': qs.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0,
            'total_commission': qs.filter(status='completed').aggregate(Sum('commission'))['commission__sum'] or 0,
            'by_type': list(qs.values('transaction_type').annotate(count=Count('id'), total=Sum('amount'))),
            'by_status': list(qs.values('status').annotate(count=Count('id'))),
        })



class ContractViewSet(viewsets.ModelViewSet):
    serializer_class = ContractSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Utilisation du champ 'role' au lieu de 'is_owner'
        if user.role == 'admin' or user.role == 'agency_owner':
            return Contract.objects.all()
        if user.role == 'client':
            return Contract.objects.filter(transaction__client__user=user)
        # Pour l'agent
        return Contract.objects.filter(transaction__property__agency=user.agency)

    def perform_create(self, serializer):
        # Restriction : seul le propriétaire peut émettre
        if not (self.request.user.role == 'admin' or self.request.user.role == 'agency_owner'):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Seul le propriétaire de l'agence peut émettre des contrats.")
        serializer.save()

    @action(detail=True, methods=['post'])
    def sign(self, request, pk=None):
        contract = self.get_object()
        contract.status = 'signed'
        contract.signed_date = datetime.date.today()
        contract.save()
        return Response({"message": "Signé"})