from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import DoctorProfile
from .serializers import DoctorProfileSerializer
from .permissions import IsDoctorOrAdmin

class DoctorProfileViewSet(viewsets.ModelViewSet):
    queryset = DoctorProfile.objects.select_related('user').all()
    serializer_class = DoctorProfileSerializer
    permission_classes = [IsDoctorOrAdmin]

    def get_queryset(self):
        user = self.request.user
        # Admin sees all
        if user.is_superuser or user.role == 'admin':
            return super().get_queryset()
        # Doctors see only their own
        if user.role == 'doctor':
            return DoctorProfile.objects.filter(user=user)
        # Patients (and other roles) can see doctors for booking
        return super().get_queryset()

    @action(detail=False, methods=['get'], url_path='me', permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        try:
            profile = DoctorProfile.objects.get(user=request.user)
        except DoctorProfile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)
