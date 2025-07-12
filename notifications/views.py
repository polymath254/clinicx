from rest_framework import viewsets
from .models import NotificationLog
from .serializers import NotificationLogSerializer
from .permissions import IsAdminOnly

class NotificationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Admin-only: list or retrieve notification logs.
    """
    queryset = NotificationLog.objects.all().order_by('-created_at')
    serializer_class = NotificationLogSerializer
    permission_classes = [IsAdminOnly]
    pagination_class = None  # or use default pagination
