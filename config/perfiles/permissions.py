from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    Assumes the model instance has a `user` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        return obj.user == request.user


class IsProfileOwner(permissions.BasePermission):
    """
    Custom permission to only allow the owner of a profile to access/edit it.
    Specifically designed for PerfilModelo where user is accessed via obj.user
    """

    def has_permission(self, request, view):
        # User must be authenticated
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Check if the user owns this profile
        return obj.user == request.user


class IsModeloUser(permissions.BasePermission):
    """
    Permission to check if the authenticated user is a modelo (es_modelo=True)
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, 'es_modelo')
            and request.user.es_modelo
        )
