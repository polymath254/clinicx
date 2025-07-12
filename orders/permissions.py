from rest_framework import permissions, exceptions
from rest_framework.permissions import SAFE_METHODS
from appointments.models import Appointment


class IsPharmacistOrAdminOrOwner(permissions.BasePermission):
    """
    - Unauthenticated: no access.
    - Admins: full CRUD.
    - Pharmacists: create & view all.
    - Patients: view their own orders only.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        # Creating orders: only pharmacists or admins
        if view.action == 'create':
            return user.role in ['pharmacist'] or user.is_superuser
        # Others defer to object-level
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        # Admin full access
        if user.is_superuser:
            return True
        # Pharmacists full access
        if user.role == 'pharmacist':
            return True
        # Patients: can only view their own
        if user.role == 'patient' and obj.patient_id == user.id:
            return request.method in SAFE_METHODS
        return False
