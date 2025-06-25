from rest_framework import permissions

class IsOwnerOfProfile(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == 'PATCH' or request.method == 'PUT':
            return obj.user == request.user
        return True