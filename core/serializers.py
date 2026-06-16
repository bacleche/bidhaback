from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','email','first_name','last_name','role','phone','avatar']
        read_only_fields = ['id']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    class Meta:
        model = User
        fields = ['username','email','first_name','last_name','password','phone','role']
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


# from .models import Notification
from core.models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    target_url = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = '__all__'

    def get_target_url(self, obj):
        user = self.context['request'].user
        role = getattr(user, 'role', 'client') # Supposons que vous avez un champ 'role' sur le User ou Profile

        # Logique de redirection selon le rôle et la catégorie
        if role == 'agency_owner':
            routes = {
                'complaint': f'/dashboard/gestion_owner/plaintes/{obj.related_id}',
                'visit': f'/dashboard/gestion_owner/liste_visite/{obj.related_id}',
                'contract': f'/dashboard/gestion_owner/contracts/{obj.related_id}',
            }
        elif role == 'agent':
            routes = {
                'contract': f'/dashboard/contracts/{obj.related_id}',
                'visit': f'/dashboard/gestion/visiteplanning/{obj.related_id}',
            }
        else: # Client
            routes = {
                'contract': f'/dashboard/clients/zone/contrats/{obj.related_id}',
                'complaint': f'/dashboard/clients/zone/plaintes/{obj.related_id}',
            }
            
        return routes.get(obj.category, '/dashboard')



# accounts/serializers.py — ajoute ce serializer
class ClientUserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    client_type = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                  'phone', 'full_name', 'client_type']

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username

    def get_client_type(self, obj):
        return 'individual'  # ou adapte si tu as ce champ ailleurs