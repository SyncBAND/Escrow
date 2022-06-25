from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.exceptions import PermissionDenied

class IsOwnerProfileOrReadOnly(BasePermission):

    model = None
    message = "You don't have permission to access"

    def has_object_permission(self, request, view, obj):
        # safe = request.method in SAFE_METHODS
        
        if request.user.is_superuser:
            return True
        return str(obj.id)==str(request.user.id)
