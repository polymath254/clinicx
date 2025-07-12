
from rest_framework import permissions

class IsPatientOrAdminOrAssignedDoctor(permissions.BasePermission):
    """
    - Unauthenticated: no access.
    - Admins (is_superuser or role='admin'): full access.
    - Patients: read/write own profile only.
    - Doctors: read (SAFE_METHODS) on assigned patients only.
    """

    def has_permission(self, request, view):
        # Deny anonymous
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Admins get full access
        if user.is_superuser or user.role == 'admin':
            return True

        # Patient can read/write their own profile
        if user.role == 'patient' and obj.user_id == user.id:
            return True

        # Doctor: only read operations, and only if assigned
        if user.role == 'doctor' and request.method in permissions.SAFE_METHODS:
            # You'll need to implement the actual assignment check
            if hasattr(obj, 'is_assigned_to') and obj.is_assigned_to(user):
                return True

        # Everything else is forbidden
        return False


