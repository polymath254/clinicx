from rest_framework import viewsets
from .models import Prescription
from .serializers import PrescriptionSerializer
from .permissions import PrescriptionPermission

class PrescriptionViewSet(viewsets.ModelViewSet):
    queryset = Prescription.objects.select_related('doctor', 'patient').prefetch_related('drugs__drug')
    serializer_class = PrescriptionSerializer
    permission_classes = [PrescriptionPermission]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.is_superuser or user.role == 'admin':
            return qs
        if user.role == 'doctor':
            return qs.filter(doctor=user)
        if user.role == 'patient':
            return qs.filter(patient=user)
        if user.role == 'pharmacist':
            return qs.all()
        return qs.none()
