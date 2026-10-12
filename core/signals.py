from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver

from .auditoria import Accion, registrar


@receiver(user_logged_in)
def al_iniciar_sesion(sender, request, user, **kwargs):
    registrar(Accion.INICIO_SESION, request, usuario=user)


@receiver(user_logged_out)
def al_cerrar_sesion(sender, request, user, **kwargs):
    if user is not None:
        registrar(Accion.CIERRE_SESION, request, usuario=user)


@receiver(user_login_failed)
def al_fallar_inicio(sender, credentials, request=None, **kwargs):
    registrar(Accion.INICIO_FALLIDO, request, credencial=credentials.get('username', ''))
