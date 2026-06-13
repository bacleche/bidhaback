from rest_framework import serializers
from .models import Property, PropertyImage


class PropertyImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = PropertyImage
        fields = '__all__'

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None


class PropertySerializer(serializers.ModelSerializer):
    images = PropertyImageSerializer(many=True, read_only=True)
    agency_name = serializers.CharField(source='agency.name', read_only=True)
    agent_name = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = '__all__'

    def get_agent_name(self, obj):
        return obj.agent.user.get_full_name() if obj.agent else None