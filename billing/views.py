from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Invoice, Payment
from .serializers import InvoiceSerializer, PaymentSerializer
from .permissions import IsInvoiceOwnerOrAdmin, IsPaymentOwnerOrAdmin
from .tasks import initiate_mpesa_payment

class InvoiceViewSet(viewsets.ModelViewSet):
    queryset         = Invoice.objects.select_related('patient')
    serializer_class = InvoiceSerializer
    permission_classes = [IsInvoiceOwnerOrAdmin]

    def perform_create(self, serializer):
        # Admin or system creates invoices
        serializer.save()

    @action(detail=True, methods=['post'], url_path='pay', permission_classes=[IsInvoiceOwnerOrAdmin])
    def pay(self, request, pk=None):
        invoice = self.get_object()
        if invoice.status != Invoice.STATUS_PENDING:
            return Response({"detail": "Invoice not payable."}, status=status.HTTP_400_BAD_REQUEST)
        # Create or get Payment
        payment, _ = Payment.objects.get_or_create(
            invoice=invoice,
            defaults={'amount': invoice.amount}
        )
        # Initiate STK push asynchronously
        initiate_mpesa_payment.delay(payment.id)
        return Response({"payment_id": payment.id}, status=status.HTTP_202_ACCEPTED)


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset         = Payment.objects.select_related('invoice__patient')
    serializer_class = PaymentSerializer
    permission_classes = [IsPaymentOwnerOrAdmin]
