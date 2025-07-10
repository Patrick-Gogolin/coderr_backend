from rest_framework import permissions

class isUserFromTypeCustomer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user.userprofile, 'type', None) == 'customer'