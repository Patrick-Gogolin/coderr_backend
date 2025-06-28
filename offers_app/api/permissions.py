from rest_framework import permissions

class IsTypeBusiness(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method != 'POST':
            return True

        return request.user.userprofile.type == 'business' 