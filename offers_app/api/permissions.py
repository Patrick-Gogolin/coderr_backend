from rest_framework import permissions

class OfferPermission(permissions.BasePermission):
    """
    Custom permission class for Offer-related operations.

    Global Permissions (has_permission):
    - All users must be authenticated.
    - Only users with a user profile of type 'business' are allowed to create offers (POST).
    - All authenticated users can read (GET, HEAD, OPTIONS) offer data.

    Object-Level Permissions (has_object_permission):
    - Only the user who created the offer (obj.user) is allowed to update or delete the offer (PUT, PATCH, DELETE).
    - Read access to individual offers is allowed for authenticated users.

    Usage:
        Should be used in combination with `IsAuthenticated` if needed,
        for example in the `get_permissions` method of a ViewSet:
        
        def get_permissions(self):
            if self.action == 'retrieve':
                return [IsAuthenticated()]
            if self.action in ['create', 'update', 'partial_update', 'destroy']:
                return [IsAuthenticated(), OfferPermission()]
            return []
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.method == 'POST':
            return hasattr(request.user, 'userprofile') and request.user.userprofile.type == 'business'
        
        return True
    
    def has_object_permission(self, request, view, obj):
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            return obj.user == request.user
        
        return True