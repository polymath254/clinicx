from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Read-only API for all authenticated users; write (none) restricted to admins.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        # Disallow any write methods
        if request.method not in permissions.SAFE_METHODS:
            return False
        # Any authenticated user can read; admin can write if needed in future
        return True
