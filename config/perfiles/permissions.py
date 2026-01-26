from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permite lectura a cualquiera (GET), pero escritura (PUT, PATCH, DELETE)
    solo al dueño del objeto.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class IsModelUser(permissions.BasePermission):
    """
    Verifica si el usuario autenticado tiene el flag 'es_modelo=True'.
    Nota: He cambiado el nombre de 'IsModeloUser' a 'IsModelUser' para 
    coincidir con el import de views.py.
    """
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and getattr(request.user, 'es_modelo', False)
        )

class IsProfileOwner(permissions.BasePermission):
    """
    Asegura que el usuario sea el dueño del perfil específico.
    Útil si alguna vez necesitas editar un perfil por ID, aunque
    en MiPerfilView esto se maneja automáticamente en el get_queryset.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user