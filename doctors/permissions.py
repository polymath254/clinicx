from rest_framework import permissions

class IsDoctorOrAdmin(permissions.BasePermission):
    """
    - Unauthenticated: no access.
    - Admins (is_superuser or role='admin'): full CRUD.
    - SAFE_METHODS (GET, HEAD, OPTIONS): any authenticated user (patients can read doctor list/details).
    - Non-safe (POST/PUT/PATCH/DELETE): only the doctor themselves or admin.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Admin full access
        if user.is_superuser or user.role == 'admin':
            return True

        # Any authenticated user can read
        if request.method in permissions.SAFE_METHODS:
            return True

        # Only the doctor themself can modify their profile
        if user.role == 'doctor' and obj.user_id == user.id:
            return True

        return False
