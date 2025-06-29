from rest_framework import permissions

class IsTypeBusiness(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method != 'POST':
            return True

        return request.user.userprofile.type == 'business'
    
class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user