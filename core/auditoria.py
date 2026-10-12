from .models import RegistroActividad

Accion = RegistroActividad.Accion


def ip_de(request):
    if request is None:
        return None
    return request.META.get('REMOTE_ADDR')


def registrar(accion, request=None, usuario=None, afectado=None, credencial='', detalle=''):
    if usuario is None and request is not None and request.user.is_authenticated:
        usuario = request.user
    return RegistroActividad.objects.create(
        accion=accion,
        usuario=usuario,
        usuario_afectado=afectado,
        credencial=credencial[:150],
        ip=ip_de(request),
        detalle=detalle[:255],
    )
