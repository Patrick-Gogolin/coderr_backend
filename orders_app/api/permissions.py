from rest_framework import permissions

class isUserFromTypeCustomer(permissions.BasePermission):
    """
    - GET: Only signed in user.
    - POST: customer only
    - PUT/PATCH: only business_user
    - DELETE:  only admin
    """
       
    def has_permission(self, request, view):

        if not request.user or not request.user.is_authenticated:
            return False
        
        user_type = getattr(request.user.userprofile, 'type', None)
        
        if request.method == 'GET':
            return True
        
        if request.method in ['POST']:
            return user_type == 'customer'

        if request.method in ['PUT', 'PATCH']:
            return user_type == 'business'
        
        if request.method == 'DELETE':
            return request.user.is_staff
        
        return False
    
    def has_object_permission(self, request, view, obj):
        user_type = getattr(request.user.userprofile, 'type', None)

        if request.method in ['PUT', 'PATCH']:
            return user_type == 'business' and obj.business_user == request.user
