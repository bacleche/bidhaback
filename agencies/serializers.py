from rest_framework import serializers
from django.db.models import Avg
from .models import Agency, Agent, AgencyReview
from core.serializers import UserSerializer

class AgencySerializer(serializers.ModelSerializer):
    agents_count = serializers.SerializerMethodField()
    avg_stars = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()

    class Meta:
        model = Agency
        fields = '__all__'
        read_only_fields = ['owner']

    def get_agents_count(self, obj):
        return obj.agents.filter(is_active=True).count()

    def get_avg_stars(self, obj):
        val = obj.reviews.aggregate(Avg('stars'))['stars__avg']
        return round(val, 1) if val is not None else 0.0

    def get_reviews_count(self, obj):
        return obj.reviews.count()

# serializers.py
class AgentSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=True)

    class Meta:
        model = Agent
        fields = '__all__'

    def create(self, validated_data):
        # 1. Extraire les données
        user_data = validated_data.pop('user')
        
        # 2. Créer l'utilisateur manuellement pour éviter l'erreur de Serializer imbriqué
        from core.models import User
        password = user_data.pop('password', 'defaultpassword123')
        user = User.objects.create_user(**user_data)
        user.set_password(password)
        user.save()

        # 3. Récupérer l'agence via l'utilisateur qui fait la requête
        request = self.context.get('request')
        # On suppose que l'owner a une relation 'agency'
        agency = request.user.agency_owner_profile.agency 
        
        # 4. Créer l'agent
        agent = Agent.objects.create(user=user, agency=agency, **validated_data)
        return agent

        
class AgencyReviewSerializer(serializers.ModelSerializer):
    client_name = serializers.SerializerMethodField()

    class Meta:
        model = AgencyReview
        fields = ['id', 'client', 'client_name', 'stars', 'comment', 'created_at']
        read_only_fields = ['client', 'created_at']

    def get_client_name(self, obj):
        return obj.client.get_full_name() or obj.client.username

