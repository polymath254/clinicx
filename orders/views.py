from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Order
from .serializers import OrderSerializer
from .tasks import send_order_sms_task

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        order = serializer.save()
        customer = order.customer
        phone = customer.phone_number  # assumes Customer model has phone_number field
        message = f"Dear {customer.name}, your order for {order.item} (Amount: {order.amount}) has been placed. Thank you!"
        # Call Celery task asynchronously
        send_order_sms_task.delay(phone, message)
