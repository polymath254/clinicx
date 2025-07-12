from rest_framework import permissions

class IsAdminOnly(permissions.BasePermission):
    """
    Only superusers (admins) may view notification logs.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_superuser)
