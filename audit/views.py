from rest_framework import viewsets
from .models import AuditLog
from .serializers import AuditLogSerializer
from .permissions import IsAdminOrReadOnly

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ['user', 'action', 'content_type__model', 'object_id']
    search_fields = ['details']
    ordering_fields = ['timestamp']
