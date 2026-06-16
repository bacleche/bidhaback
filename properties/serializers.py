from rest_framework import serializers
from .models import Property, PropertyImage


class PropertyImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = PropertyImage
        fields = '__all__'

    def get_image(self, obj):
        if obj.image:
            # Si c'est déjà une URL Cloudinary, on la retourne telle quelle
            if obj.image.url.startswith('http'):
                return obj.image.url
            
            # Sinon, on tente de construire l'URI
            request = self.context.get('request')
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None


class PropertySerializer(serializers.ModelSerializer):
    images = PropertyImageSerializer(many=True, read_only=True)
    agency_name = serializers.CharField(source='agency.name', read_only=True)
    agent_name = serializers.SerializerMethodField()
    is_contacted = serializers.SerializerMethodField()
    has_pending_visit = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = '__all__'

    def get_agent_name(self, obj):
        return obj.agent.user.get_full_name() if obj.agent else None

    def get_is_contacted(self, obj):
        user = self.context.get('request').user if self.context.get('request') else None
        if user and user.is_authenticated and user.role == 'client':
            from interactions.models import ContactRequest
            return ContactRequest.objects.filter(property=obj, client=user).exists()
        return False

    def get_has_pending_visit(self, obj):
        user = self.context.get('request').user if self.context.get('request') else None
        if user and user.is_authenticated and user.role == 'client':
            from interactions.models import VisitRequest
            return VisitRequest.objects.filter(property=obj, client=user, status='pending').exists()
        return False