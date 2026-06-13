from rest_framework import serializers
from .models import ContactRequest, Message, VisitRequest, Complaint
from core.serializers import UserSerializer


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'sender', 'sender_name', 'content', 'is_read', 'created_at']
        read_only_fields = ['sender', 'created_at']

    def get_sender_name(self, obj):
        return obj.sender.get_full_name() or obj.sender.username


class ContactRequestSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    client_name = serializers.SerializerMethodField()
    property_title = serializers.CharField(source='property.title', read_only=True)
    agent_name = serializers.SerializerMethodField()

    class Meta:
        model = ContactRequest
        fields = ['id', 'property', 'property_title', 'client', 'client_name',
                  'agent', 'agent_name', 'message', 'status', 'created_at', 'messages']
        read_only_fields = ['client', 'agent', 'created_at']

    def get_client_name(self, obj):
        return obj.client.get_full_name() or obj.client.username

    def get_agent_name(self, obj):
        return obj.agent.user.get_full_name() if obj.agent else None


class VisitRequestSerializer(serializers.ModelSerializer):
    client_name = serializers.SerializerMethodField()
    property_title = serializers.CharField(source='property.title', read_only=True)
    agent_name = serializers.SerializerMethodField()

    class Meta:
        model = VisitRequest
        fields = ['id', 'property', 'property_title', 'client', 'client_name',
                  'agent', 'agent_name', 'requested_date', 'rescheduled_date',
                  'status', 'notes', 'agent_notes', 'created_at']
        read_only_fields = ['client', 'agent', 'created_at']

    def get_client_name(self, obj):
        return obj.client.get_full_name() or obj.client.username

    def get_agent_name(self, obj):
        return obj.agent.user.get_full_name() if obj.agent else None


class ComplaintSerializer(serializers.ModelSerializer):
    client_name = serializers.SerializerMethodField()
    property_title = serializers.CharField(source='property.title', read_only=True)

    class Meta:
        model = Complaint
        fields = ['id', 'agency', 'client', 'client_name', 'property', 'property_title',
                  'category', 'subject', 'description', 'status', 'owner_response', 'created_at']
        read_only_fields = ['client', 'created_at', 'owner_response']

    def get_client_name(self, obj):
        return obj.client.get_full_name() or obj.client.username