from rest_framework import permissions

class OfferPermission(permissions.BasePermission):
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