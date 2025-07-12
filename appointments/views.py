from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Appointment
from .serializers import AppointmentSerializer
from .permissions import AppointmentPermission

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.select_related('patient', 'doctor').all()
    serializer_class = AppointmentSerializer
    permission_classes = [AppointmentPermission]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.role == 'admin':
            return super().get_queryset()
        if user.role == 'patient':
            return Appointment.objects.filter(patient=user)
        if user.role == 'doctor':
            return Appointment.objects.filter(doctor=user)
        return Appointment.objects.none()

    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
