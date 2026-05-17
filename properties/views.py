from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Property, PropertyImage
from .serializers import PropertySerializer, PropertyImageSerializer

class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    search_fields = ['title','city','district','description']
    filterset_fields = ['property_type','offer_type','status','city','is_featured','agency']
    ordering_fields = ['price','created_at','area','views_count']
    ordering = ['-created_at']

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.views_count += 1
        instance.save(update_fields=['views_count'])
        return super().retrieve(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        featured = Property.objects.filter(is_featured=True, status='available')[:8]
        return Response(PropertySerializer(featured, many=True).data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        from django.db.models import Count, Sum
        return Response({
            'total': Property.objects.count(),
            'available': Property.objects.filter(status='available').count(),
            'sold': Property.objects.filter(status='sold').count(),
            'rented': Property.objects.filter(status='rented').count(),
            'by_type': list(Property.objects.values('property_type').annotate(count=Count('id'))),
        })
