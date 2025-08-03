from rest_framework import permissions

class isUserFromTypeCustomer(permissions.BasePermission):
    """
    Permission to allow access only to authenticated users
    whose associated UserProfile has a type of 'customer'.

    Methods:
        - has_permission(request, view):
            Returns True if the user is authenticated and userprofile.type == 'customer',
            otherwise False.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        userprofile = getattr(user, 'userprofile', None)
        return getattr(userprofile, 'type', None) == 'customer'

class isCreatorOfReview(permissions.BasePermission):
    """
    Object-level permission to allow only the creator (reviewer)
    of a review object to have permission for actions.

    Methods:
        - has_object_permission(request, view, obj):
            Returns True if the request user is authenticated and is the reviewer of the object,
            otherwise False.
    """
    
    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated and
            obj.reviewer == request.user
        )