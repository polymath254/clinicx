from rest_framework import permissions, exceptions
from rest_framework.permissions import SAFE_METHODS
from appointments.models import Appointment


class PrescriptionPermission(permissions.BasePermission):
    """
    - Unauthenticated: no access.
    - Admins (is_superuser or role='admin'): full CRUD.
    - Doctors: create for any patient, manage their own prescriptions.
    - Patients: list/retrieve their own; cannot create.
    - Pharmacists: list/retrieve all (read-only).
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Doctors may create
        if view.action == 'create' and request.user.role == 'doctor':
            return True

        # Everyone else defers to object permissions for list/detail
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Admin full access
        if user.is_superuser or user.role == 'admin':
            return True

        # Doctors: manage their own prescriptions
        if user.role == 'doctor' and obj.doctor_id == user.id:
            return True

        # Patients: read-only on own
        if user.role == 'patient' and obj.patient_id == user.id:
            return request.method in SAFE_METHODS

        # Pharmacists: read-only on all
        if user.role == 'pharmacist' and request.method in SAFE_METHODS:
            return True

        return False
