"""
Middleware para autenticación JWT desde cookies HttpOnly.

Este middleware intercepta las requests y añade el header Authorization
leyendo el token desde la cookie 'access_token'.
"""


class JWTAuthCookieMiddleware:
    """
    Middleware que convierte cookies HttpOnly a headers Authorization.
    
    Permite que SimpleJWT funcione con cookies en lugar de headers.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Leer el token desde la cookie
        access_token = request.COOKIES.get('access_token')
        
        # Si existe el token y NO hay Authorization header, agregarlo
        if access_token and not request.META.get('HTTP_AUTHORIZATION'):
            request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
        
        response = self.get_response(request)
        return response
