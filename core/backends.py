from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q


class UsuarioOCorreoBackend(ModelBackend):
    """Autentica con el nombre de usuario o el correo, sin distinguir mayúsculas.

    Hereda de ModelBackend, que rechaza a los usuarios inactivos (baja lógica).
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
        Usuario = get_user_model()
        credencial = username.strip()
        try:
            usuario = Usuario.objects.get(Q(username__iexact=credencial) | Q(email__iexact=credencial))
        except (Usuario.DoesNotExist, Usuario.MultipleObjectsReturned):
            # Hashear igual para que el tiempo de respuesta no revele si el usuario existe.
            Usuario().set_password(password)
            return None
        if usuario.check_password(password) and self.user_can_authenticate(usuario):
            return usuario
        return None
