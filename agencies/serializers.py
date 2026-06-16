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
        try:
            request = self.context.get('request')
            user_data = validated_data.pop('user')
            
            # Création utilisateur
            from core.models import User
            user = User.objects.create_user(**user_data)
            
            # Récupération agence (On force l'agence du propriétaire connecté)
            agency = request.user.owned_agencies.first()
            if not agency:
                raise Exception("L'utilisateur connecté ne possède aucune agence.")

            # Création agent
            agent = Agent.objects.create(
                user=user,
                agency=agency,
                employee_id=f"AG-{uuid.uuid4().hex[:6].upper()}",
                **validated_data
            )
            return agent
            
        except Exception as e:
            # CECI VA VOUS DIRE EXACTEMENT CE QUI BLOQUE
            raise serializers.ValidationError({"detail": str(e)})

class AgencyReviewSerializer(serializers.ModelSerializer):
    client_name = serializers.SerializerMethodField()

    class Meta:
        model = AgencyReview
        fields = ['id', 'client', 'client_name', 'stars', 'comment', 'created_at']
        read_only_fields = ['client', 'created_at']

    def get_client_name(self, obj):
        return obj.client.get_full_name() or obj.client.username

