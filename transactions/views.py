from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count
from .models import Transaction, Contract
from .serializers import TransactionSerializer, ContractSerializer

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    filterset_fields = ['transaction_type','status','agent']
    ordering = ['-created_at']

    @action(detail=False, methods=['get'])
    def stats(self, request):
        return Response({
            'total_revenue': Transaction.objects.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0,
            'total_commission': Transaction.objects.filter(status='completed').aggregate(Sum('commission'))['commission__sum'] or 0,
            'by_type': list(Transaction.objects.values('transaction_type').annotate(count=Count('id'), total=Sum('amount'))),
            'by_status': list(Transaction.objects.values('status').annotate(count=Count('id'))),
        })

class ContractViewSet(viewsets.ModelViewSet):
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer
    filterset_fields = ['contract_type','status']
    ordering = ['-created_at']
