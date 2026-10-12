from django.shortcuts import redirect
from django.urls import reverse


class CambioClaveObligatorioMiddleware:
    """Si el usuario tiene una contraseña inicial o reseteada, lo obliga a cambiarla."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        if user.is_authenticated and user.debe_cambiar_clave:
            permitidas = (reverse('password_change'), reverse('logout'))
            if request.path not in permitidas and not request.path.startswith('/static/'):
                return redirect('password_change')
        return self.get_response(request)
