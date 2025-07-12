from rest_framework import permissions

class IsPharmacistOrAdmin(permissions.BasePermission):
    """
    Only authenticated users with role 'pharmacist' or 'admin' can access inventory.
    """

    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and u.role in ['pharmacist', 'admin'])

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)
