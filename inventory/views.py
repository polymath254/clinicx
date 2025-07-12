
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Supplier, Drug, PurchaseOrder
from .serializers import SupplierSerializer, DrugSerializer, PurchaseOrderSerializer
from .permissions import IsPharmacistOrAdmin

class SupplierViewSet(viewsets.ModelViewSet):
    queryset         = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsPharmacistOrAdmin]

class DrugViewSet(viewsets.ModelViewSet):
    queryset         = Drug.objects.select_related('supplier').all()
    serializer_class = DrugSerializer
    permission_classes = [IsPharmacistOrAdmin]

class PurchaseOrderViewSet(viewsets.ModelViewSet):
    queryset         = PurchaseOrder.objects.select_related('supplier','drug').all()
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsPharmacistOrAdmin]

    @action(detail=True, methods=['post'], url_path='deliver')
    def deliver(self, request, pk=None):
        po = self.get_object()
        po.mark_delivered()
        return Response(self.get_serializer(po).data)
