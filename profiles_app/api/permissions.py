from rest_framework import permissions

class IsOwnerOfProfile(permissions.BasePermission):
    """
    Custom permission to allow only the owner of a profile to update it.

    Use case:
    - Ensures that users can only update (`PATCH`, `PUT`) their own profile.
    - Read-only access (`GET`, etc.) is allowed for any user unless restricted elsewhere.

    Returns:
    - `True` if the request method is safe or the requesting user owns the profile.
    - `False` if attempting to update a profile not owned by the user.
    """
    
    def has_object_permission(self, request, view, obj):
        if request.method == 'PATCH' or request.method == 'PUT':
            return obj.user == request.user
        return True