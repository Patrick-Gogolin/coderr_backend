from rest_framework import permissions

class isUserFromTypeCustomer(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        userprofile = getattr(user, 'userprofile', None)
        return getattr(userprofile, 'type', None) == 'customer'

class isCreatorOfReview(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated and
            obj.reviewer == request.user
        )