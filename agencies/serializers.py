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


class AgentSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=True)

    class Meta:
        model = Agent
        fields = '__all__'
        # Ces champs sont obligatoires en BDD mais générés ici, 
        # donc on les marque comme read_only pour le serializer
        read_only_fields = ['agency', 'employee_id']

    def create(self, validated_data):
        request = self.context.get('request')
        user_data = validated_data.pop('user')
        
        # 1. Créer l'utilisateur
        password = user_data.pop('password', 'Pass1234!')
        user = User.objects.create_user(**user_data)
        user.set_password(password)
        user.save()

        # 2. Récupérer l'agence du propriétaire connecté
        # On cherche l'agence dont l'utilisateur connecté est le propriétaire
        agency = Agency.objects.filter(owner=request.user).first()
        if not agency:
            raise serializers.ValidationError({"error": "Vous n'êtes associé à aucune agence."})

        # 3. Générer un employee_id unique
        employee_id = f"AGENT-{uuid.uuid4().hex[:8].upper()}"

        # 4. Créer l'agent
        agent = Agent.objects.create(
            user=user, 
            agency=agency, 
            employee_id=employee_id, 
            **validated_data
        )
        return agent



class AgencyReviewSerializer(serializers.ModelSerializer):
    client_name = serializers.SerializerMethodField()

    class Meta:
        model = AgencyReview
        fields = ['id', 'client', 'client_name', 'stars', 'comment', 'created_at']
        read_only_fields = ['client', 'created_at']

    def get_client_name(self, obj):
        return obj.client.get_full_name() or obj.client.username

