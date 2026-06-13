from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ContactRequest, Message, VisitRequest, Complaint
from .serializers import (ContactRequestSerializer, MessageSerializer,
                           VisitRequestSerializer, ComplaintSerializer)


class ContactRequestViewSet(viewsets.ModelViewSet):
    serializer_class = ContactRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'client':
            return ContactRequest.objects.filter(client=user)
        if user.role == 'agent':
            return ContactRequest.objects.filter(agent=user.agent_profile)
        if user.role == 'agency_owner':
            agencies = user.owned_agencies.values_list('id', flat=True)
            return ContactRequest.objects.filter(property__agency__in=agencies)
        if user.role == 'admin':
            return ContactRequest.objects.all()
        return ContactRequest.objects.none()

    def create(self, request, *args, **kwargs):
        from properties.models import Property
        property_id = request.data.get('property')
        try:
            prop = Property.objects.get(id=property_id)
        except Property.DoesNotExist:
            return Response({'detail': 'Bien introuvable.'}, status=404)

        contact = ContactRequest.objects.create(
            property=prop,
            client=request.user,
            agent=prop.agent,
            message=request.data.get('message', "J'aimerais en savoir un peu plus sur ce bien."),
        )
        # Premier message automatique
        Message.objects.create(
            contact_request=contact,
            sender=request.user,
            content=contact.message,
        )
        return Response(ContactRequestSerializer(contact).data, status=201)

    @action(detail=True, methods=['post'])
    def reply(self, request, pk=None):
        contact = self.get_object()
        content = request.data.get('content', '').strip()
        if not content:
            return Response({'detail': 'Message vide.'}, status=400)
        msg = Message.objects.create(
            contact_request=contact,
            sender=request.user,
            content=content,
        )
        contact.status = 'replied'
        contact.save(update_fields=['status'])
        return Response(MessageSerializer(msg).data, status=201)

    @action(detail=True, methods=['patch'])
    def mark_read(self, request, pk=None):
        contact = self.get_object()
        contact.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
        contact.status = 'read'
        contact.save(update_fields=['status'])
        return Response({'status': 'ok'})


class VisitRequestViewSet(viewsets.ModelViewSet):
    serializer_class = VisitRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'client':
            return VisitRequest.objects.filter(client=user)
        if user.role == 'agent':
            return VisitRequest.objects.filter(agent=user.agent_profile)
        if user.role == 'agency_owner':
            agencies = user.owned_agencies.values_list('id', flat=True)
            return VisitRequest.objects.filter(property__agency__in=agencies)
        if user.role == 'admin':
            return VisitRequest.objects.all()
        return VisitRequest.objects.none()

    def create(self, request, *args, **kwargs):
        from properties.models import Property
        property_id = request.data.get('property')
        try:
            prop = Property.objects.get(id=property_id)
        except Property.DoesNotExist:
            return Response({'detail': 'Bien introuvable.'}, status=404)

        visit = VisitRequest.objects.create(
            property=prop,
            client=request.user,
            agent=prop.agent,
            requested_date=request.data.get('requested_date'),
            notes=request.data.get('notes', ''),
        )
        return Response(VisitRequestSerializer(visit).data, status=201)

    @action(detail=True, methods=['patch'])
    def respond(self, request, pk=None):
        """Agent: accepter / reprogrammer / rejeter"""
        visit = self.get_object()
        user = request.user
        if user.role not in ['agent', 'agency_owner', 'admin']:
            return Response({'detail': 'Non autorisé.'}, status=403)

        new_status = request.data.get('status')
        if new_status not in ['accepted', 'rescheduled', 'rejected']:
            return Response({'detail': 'Statut invalide.'}, status=400)

        visit.status = new_status
        visit.agent_notes = request.data.get('agent_notes', '')
        if new_status == 'rescheduled':
            visit.rescheduled_date = request.data.get('rescheduled_date')
        visit.save()
        return Response(VisitRequestSerializer(visit).data)


class ComplaintViewSet(viewsets.ModelViewSet):
    serializer_class = ComplaintSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'client':
            return Complaint.objects.filter(client=user)
        if user.role == 'agency_owner':
            agencies = user.owned_agencies.values_list('id', flat=True)
            return Complaint.objects.filter(agency__in=agencies)
        if user.role == 'admin':
            return Complaint.objects.all()
        return Complaint.objects.none()

    def create(self, request, *args, **kwargs):
        from properties.models import Property
        property_id = request.data.get('property')
        prop = None
        agency_id = request.data.get('agency')

        if property_id:
            try:
                prop = Property.objects.get(id=property_id)
                agency_id = prop.agency_id
            except Property.DoesNotExist:
                pass

        complaint = Complaint.objects.create(
            agency_id=agency_id,
            client=request.user,
            property=prop,
            category=request.data.get('category', 'other'),
            subject=request.data.get('subject', ''),
            description=request.data.get('description', ''),
        )
        return Response(ComplaintSerializer(complaint).data, status=201)

    @action(detail=True, methods=['patch'])
    def respond(self, request, pk=None):
        """Agency owner répond à une plainte"""
        complaint = self.get_object()
        user = request.user
        if user.role not in ['agency_owner', 'admin']:
            return Response({'detail': 'Non autorisé.'}, status=403)
        complaint.owner_response = request.data.get('owner_response', '')
        complaint.status = request.data.get('status', complaint.status)
        complaint.save()
        return Response(ComplaintSerializer(complaint).data)