from rest_framework import permissions, exceptions
from rest_framework.permissions import SAFE_METHODS
from appointments.models import Appointment


class AppointmentPermission(permissions.BasePermission):
    """
    - Unauthenticated: NO access.
    - Admins (is_superuser or role='admin'): FULL access.
    - Patients: can create appointments for themselves, view/list their own, cancel if scheduled.
    - Doctors: can view/list their own, update status to 'completed' or 'cancelled'.
    """

    def has_permission(self, request, view):
        # Block anonymous users outright
        if not request.user or not request.user.is_authenticated:
            return False
        # Patients may create
        if view.action == 'create' and request.user.role == 'patient':
            return True
        # Others must pass to object-level checks for list/retrieve/update/delete
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Admins get full access
        if user.is_superuser or user.role == 'admin':
            return True

        # Patient: own appointments
        if user.role == 'patient' and obj.patient_id == user.id:
            # Can read and cancel if still scheduled
            if request.method in SAFE_METHODS:
                return True
            if view.action in ['partial_update', 'update'] and obj.status == Appointment.STATUS_SCHEDULED:
                return True

        # Doctor: their appointments
        if user.role == 'doctor' and obj.doctor_id == user.id:
            # Can read
            if request.method in SAFE_METHODS:
                return True
            # Can update status only
            if view.action in ['partial_update', 'update'] and 'status' in request.data:
                return True

        # Everything else is forbidden
        return False
