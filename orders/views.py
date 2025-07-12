from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Order
from .serializers import OrderSerializer
from .permissions import IsPharmacistOrAdminOrOwner

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.select_related('patient','prescription','drug').all()
    serializer_class = OrderSerializer
    permission_classes = [IsPharmacistOrAdminOrOwner]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.role == 'pharmacist':
            return super().get_queryset()
        if user.role == 'patient':
            return Order.objects.filter(patient=user)
        return Order.objects.none()

    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

