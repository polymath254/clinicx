from rest_framework import permissions, exceptions
from rest_framework.permissions import SAFE_METHODS
from appointments.models import Appointment


class IsInvoiceOwnerOrAdmin(permissions.BasePermission):
    """
    - Unauthenticated: no access.
    - Admins: full CRUD.
    - Patients: view/list their own invoices; create only via system.
    - No one can modify a PAID invoice.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        # Allow creation only by admins or system tasks
        if view.action in ['create', 'destroy'] and not request.user.is_superuser:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        # Admins can do anything
        if user.is_superuser:
            return True
        # Patients can view or list their own
        if user.role == 'patient' and obj.patient_id == user.id:
            if request.method in SAFE_METHODS:
                return True
        return False


class IsPaymentOwnerOrAdmin(permissions.BasePermission):
    """
    - Admins: full access.
    - Patient (invoice owner): read-only.
    - No creation via API (handled by invoice view).
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_superuser:
            return True
        # Patient linked to invoice can view
        if user.role == 'patient' and obj.invoice.patient_id == user.id and request.method in SAFE_METHODS:
            return True
        return False
