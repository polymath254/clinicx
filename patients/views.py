# patients/views.py
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import PatientProfile
from .serializers import PatientProfileSerializer
from .permissions import IsPatientOrAdminOrAssignedDoctor

class PatientProfileViewSet(viewsets.ModelViewSet):
    queryset = PatientProfile.objects.select_related('user')
    serializer_class = PatientProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsPatientOrAdminOrAssignedDoctor]

    def get_queryset(self):
        user = self.request.user
        # Admins see all
        if user.is_superuser or user.role == "admin":
            return PatientProfile.objects.all()
        # Patients see only their own
        if user.role == "patient" and hasattr(user, 'patient_profile'):
            return PatientProfile.objects.filter(user=user)
        # Doctors could see assigned patients (permission will check per-object)
        if user.role == "doctor":
            return PatientProfile.objects.all()
        return PatientProfile.objects.none()

    def retrieve(self, request, *args, **kwargs):
        # support /patients/me/ returning self
        if kwargs.get('pk') == 'me':
            return self.me(request)
        return super().retrieve(request, *args, **kwargs)

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        profile = PatientProfile.objects.get(user=request.user)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

