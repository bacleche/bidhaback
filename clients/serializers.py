from rest_framework import serializers
from .models import Client


class ClientSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    # Champ virtuel "username" pour compatibilité avec le composant ClientSearchSelect
    username = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = '__all__'

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

    def get_username(self, obj):
        """
        Renvoie l'email comme identifiant unique affichable,
        ou génère un identifiant depuis le nom si pas d'email.
        """
        if obj.email:
            return obj.email.split('@')[0]
        return f"{obj.first_name.lower()}.{obj.last_name.lower()}".replace(' ', '')
