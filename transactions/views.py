import uuid
import datetime
from decimal import Decimal
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.db.models import Sum, Count
from django.http import HttpResponse
from .models import Transaction, Contract
from .serializers import TransactionSerializer, ContractSerializer
from agencies.views import get_user_agency
from agencies.models import Agent


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['transaction_type', 'status', 'agent']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Transaction.objects.none()
        if user.role == 'admin':
            return Transaction.objects.all()
        if user.role == 'client':
            return Transaction.objects.filter(client=user)  # ← corrigé
        agency = get_user_agency(user)
        if agency:
            return Transaction.objects.filter(property__agency=agency)
        try:
            agent_obj = Agent.objects.get(user=user)
            return Transaction.objects.filter(property__agency=agent_obj.agency)
        except Agent.DoesNotExist:
            pass
        return Transaction.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        transaction_number = f"TXN-{uuid.uuid4().hex[:8].upper()}"
        transaction_date = self.request.data.get('transaction_date') or datetime.date.today()
        amount = Decimal(str(self.request.data.get('amount', 0)))
        commission_rate = Decimal(str(self.request.data.get('commission_rate', 5)))
        commission = (amount * commission_rate / 100).quantize(Decimal('0.01'))
        agent = None
        try:
            agent = Agent.objects.get(user=user)
        except Agent.DoesNotExist:
            pass
        serializer.save(
            transaction_number=transaction_number,
            transaction_date=transaction_date,
            commission=commission,
            agent=agent,
        )

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total_revenue': qs.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0,
            'total_commission': qs.filter(status='completed').aggregate(Sum('commission'))['commission__sum'] or 0,
            'by_type': list(qs.values('transaction_type').annotate(count=Count('id'), total=Sum('amount'))),
            'by_status': list(qs.values('status').annotate(count=Count('id'))),
        })


class ContractViewSet(viewsets.ModelViewSet):
    serializer_class = ContractSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'agency_owner']:
            return Contract.objects.all()
        if user.role == 'client':
            return Contract.objects.filter(transaction__client=user)  # ← corrigé
        agency = get_user_agency(user)
        if agency:
            return Contract.objects.filter(transaction__property__agency=agency)
        try:
            agent_obj = Agent.objects.get(user=user)
            return Contract.objects.filter(transaction__property__agency=agent_obj.agency)
        except Agent.DoesNotExist:
            pass
        return Contract.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role not in ['admin', 'agency_owner', 'agent']:  # agent peut aussi créer
            raise PermissionDenied("Non autorisé à émettre des contrats.")
        contract_number = self.request.data.get('contract_number') or f"CTR-{uuid.uuid4().hex[:8].upper()}"
        start_date = self.request.data.get('start_date') or datetime.date.today()
        serializer.save(contract_number=contract_number, start_date=start_date)

    @action(detail=True, methods=['post'])
    def sign_owner(self, request, pk=None):
        contract = self.get_object()
        user = request.user
        if user.role not in ['admin', 'agency_owner']:
            return Response({"detail": "Non autorisé."}, status=403)

        contract.owner_signed = True
        contract.owner_signature_date = datetime.date.today()
        txn = contract.transaction

        if contract.client_signed:
            contract.status = 'signed'
            contract.signed_date = datetime.date.today()
            txn.status = 'completed'
            txn.save(update_fields=['status'])
            prop = txn.property
            prop.status = 'sold' if txn.transaction_type in ['sale', 'purchase'] else 'rented'
            prop.save(update_fields=['status'])
        else:
            contract.status = 'signed_owner'

        contract.save()

        # Notif client — direct User
        create_notification(
            user=txn.client,  # ← corrigé
            title="Contrat signé par l'Agence",
            message=f"L'agence a signé le contrat {contract.contract_number}. Veuillez le signer à votre tour.",
            category="contract",
            related_id=contract.id
        )
        if txn.agent:
            create_notification(
                user=txn.agent.user,
                title="Contrat signé par l'Agence",
                message=f"Le contrat {contract.contract_number} a été signé par l'agence.",
                category="contract",
                related_id=contract.id
            )

        return Response(ContractSerializer(contract).data)

    @action(detail=True, methods=['post'])
    def sign_client(self, request, pk=None):
        contract = self.get_object()
        user = request.user

        if user.role != 'client' or contract.transaction.client != user:  # ← corrigé
            return Response({"detail": "Non autorisé."}, status=403)

        contract.client_signed = True
        contract.client_signature_date = datetime.date.today()
        txn = contract.transaction

        if contract.owner_signed:
            contract.status = 'signed'
            contract.signed_date = datetime.date.today()
            txn.status = 'completed'
            txn.save(update_fields=['status'])
            prop = txn.property
            prop.status = 'sold' if txn.transaction_type in ['sale', 'purchase'] else 'rented'
            prop.save(update_fields=['status'])

        contract.save()

        try:
            owner = txn.property.agency.owner
            create_notification(
                user=owner,
                title="Contrat signé par le Client",
                message=f"Le client {user.get_full_name() or user.username} a signé le contrat {contract.contract_number}.",
                category="contract",
                related_id=contract.id
            )
        except Exception:
            pass
        if txn.agent:
            create_notification(
                user=txn.agent.user,
                title="Contrat signé par le Client",
                message=f"Le client a signé le contrat {contract.contract_number}.",
                category="contract",
                related_id=contract.id
            )

        return Response(ContractSerializer(contract).data)

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        contract = self.get_object()
        user = request.user

        is_client = user.role == 'client' and contract.transaction.client == user
        is_agent  = user.role == 'agent' and hasattr(user, 'agent_profile') and contract.transaction.agent == user.agent_profile
        is_owner  = user.role == 'agency_owner' and contract.transaction.property.agency.owner == user
        is_admin  = user.role == 'admin'

        if not (is_client or is_agent or is_owner or is_admin):
            raise PermissionDenied("Vous n'êtes pas autorisé à télécharger ce contrat.")

        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
        from io import BytesIO

        client = contract.transaction.client
        agency = contract.transaction.property.agency
        txn    = contract.transaction

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                                rightMargin=2*cm, leftMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm)

        styles = getSampleStyleSheet()
        title_style  = ParagraphStyle('title',  fontSize=16, fontName='Helvetica-Bold', alignment=1, spaceAfter=6)
        ref_style    = ParagraphStyle('ref',    fontSize=10, fontName='Helvetica',      alignment=1, spaceAfter=20, textColor=colors.grey)
        heading_style= ParagraphStyle('heading',fontSize=11, fontName='Helvetica-Bold', spaceBefore=14, spaceAfter=6, textColor=colors.HexColor('#1e40af'))
        body_style   = ParagraphStyle('body',   fontSize=10, fontName='Helvetica',      spaceAfter=4, leading=16)

        story = []

        # En-tête
        story.append(Paragraph("CONTRAT IMMOBILIER", title_style))
        story.append(Paragraph("BIDHAA", ParagraphStyle('brand', fontSize=13, fontName='Helvetica-Bold', alignment=1, textColor=colors.HexColor('#1e40af'))))
        story.append(Paragraph(f"Référence : {contract.contract_number}", ref_style))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e5e7eb')))
        story.append(Spacer(1, 12))

        # Infos générales
        story.append(Paragraph("INFORMATIONS GÉNÉRALES", heading_style))
        infos = [
            ["Titre", contract.title],
            ["Type", contract.get_contract_type_display()],
            ["Statut", contract.get_status_display()],
            ["Date de création", contract.created_at.strftime('%d/%m/%Y')],
            ["Date de début", contract.start_date.strftime('%d/%m/%Y') if contract.start_date else '—'],
            ["Date de fin", contract.end_date.strftime('%d/%m/%Y') if contract.end_date else '—'],
        ]
        t = Table(infos, colWidths=[5*cm, 12*cm])
        t.setStyle(TableStyle([
            ('FONTNAME',  (0,0),(-1,-1), 'Helvetica'),
            ('FONTNAME',  (0,0),(0,-1),  'Helvetica-Bold'),
            ('FONTSIZE',  (0,0),(-1,-1), 10),
            ('ROWBACKGROUNDS', (0,0),(-1,-1), [colors.HexColor('#f9fafb'), colors.white]),
            ('GRID',      (0,0),(-1,-1), 0.5, colors.HexColor('#e5e7eb')),
            ('PADDING',   (0,0),(-1,-1), 6),
        ]))
        story.append(t)
        story.append(Spacer(1, 12))

        # Parties
        story.append(Paragraph("PARTIES CONTRACTANTES", heading_style))
        parties = [
            ["Agence",       agency.name],
            ["Représentant", agency.owner.get_full_name() or agency.owner.username],
            ["Adresse",      f"{agency.address}, {agency.city}"],
            ["",             ""],
            ["Client",       client.get_full_name() or client.username],
            ["Téléphone",    client.phone or '—'],
            ["Email",        client.email or '—'],
        ]
        t2 = Table(parties, colWidths=[5*cm, 12*cm])
        t2.setStyle(TableStyle([
            ('FONTNAME',  (0,0),(-1,-1), 'Helvetica'),
            ('FONTNAME',  (0,0),(0,-1),  'Helvetica-Bold'),
            ('FONTSIZE',  (0,0),(-1,-1), 10),
            ('ROWBACKGROUNDS', (0,0),(-1,-1), [colors.HexColor('#f9fafb'), colors.white]),
            ('GRID',      (0,0),(-1,-1), 0.5, colors.HexColor('#e5e7eb')),
            ('PADDING',   (0,0),(-1,-1), 6),
        ]))
        story.append(t2)
        story.append(Spacer(1, 12))

        # Bien
        story.append(Paragraph("OBJET DE LA TRANSACTION", heading_style))
        bien = [
            ["Bien",        txn.property.title],
            ["Adresse",     f"{txn.property.address}, {txn.property.city}"],
            ["Type",        txn.get_transaction_type_display()],
            ["Montant",     f"{txn.amount:,.0f} FCFA"],
            ["Commission",  f"{txn.commission:,.0f} FCFA"],
        ]
        t3 = Table(bien, colWidths=[5*cm, 12*cm])
        t3.setStyle(TableStyle([
            ('FONTNAME',  (0,0),(-1,-1), 'Helvetica'),
            ('FONTNAME',  (0,0),(0,-1),  'Helvetica-Bold'),
            ('FONTSIZE',  (0,0),(-1,-1), 10),
            ('ROWBACKGROUNDS', (0,0),(-1,-1), [colors.HexColor('#f9fafb'), colors.white]),
            ('GRID',      (0,0),(-1,-1), 0.5, colors.HexColor('#e5e7eb')),
            ('PADDING',   (0,0),(-1,-1), 6),
        ]))
        story.append(t3)
        story.append(Spacer(1, 12))

        # Contenu / clauses
        if contract.content:
            story.append(Paragraph("CONDITIONS ET TERMES", heading_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#e5e7eb')))
            story.append(Spacer(1, 6))
            for line in contract.content.split('\n'):
                story.append(Paragraph(line or '&nbsp;', body_style))
            story.append(Spacer(1, 12))

        # Signatures
        story.append(Paragraph("SIGNATURES", heading_style))
        sigs = [
            ["", "Agence", "Client"],
            ["Signé",    "✓ OUI" if contract.owner_signed else "✗ EN ATTENTE",
                        "✓ OUI" if contract.client_signed else "✗ EN ATTENTE"],
            ["Date",
            contract.owner_signature_date.strftime('%d/%m/%Y') if contract.owner_signature_date else '—',
            contract.client_signature_date.strftime('%d/%m/%Y') if contract.client_signature_date else '—'],
        ]
        t4 = Table(sigs, colWidths=[5*cm, 6*cm, 6*cm])
        t4.setStyle(TableStyle([
            ('FONTNAME',   (0,0),(-1,-1), 'Helvetica'),
            ('FONTNAME',   (0,0),(-1,0),  'Helvetica-Bold'),
            ('FONTNAME',   (0,0),(0,-1),  'Helvetica-Bold'),
            ('FONTSIZE',   (0,0),(-1,-1), 10),
            ('ALIGN',      (1,0),(-1,-1), 'CENTER'),
            ('BACKGROUND', (0,0),(-1,0),  colors.HexColor('#1e40af')),
            ('TEXTCOLOR',  (0,0),(-1,0),  colors.white),
            ('GRID',       (0,0),(-1,-1), 0.5, colors.HexColor('#e5e7eb')),
            ('ROWBACKGROUNDS', (0,1),(-1,-1), [colors.HexColor('#f9fafb'), colors.white]),
            ('PADDING',    (0,0),(-1,-1), 8),
        ]))
        story.append(t4)
        story.append(Spacer(1, 20))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#e5e7eb')))
        story.append(Spacer(1, 6))
        story.append(Paragraph("Document généré automatiquement et certifié par Bidhaa.", 
                                ParagraphStyle('footer', fontSize=8, textColor=colors.grey, alignment=1)))

        doc.build(story)
        buffer.seek(0)

        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="contrat_{contract.contract_number}.pdf"'
        return response