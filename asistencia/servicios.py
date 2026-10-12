import math
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Marcacion

RADIO_TIERRA_M = 6_371_000


def distancia_metros(lat1, lon1, lat2, lon2):
    """Distancia entre dos coordenadas (fórmula del haversine)."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * RADIO_TIERRA_M * math.asin(math.sqrt(a))


def ultima_marcacion_de_hoy(usuario):
    hoy = timezone.localdate()
    return Marcacion.objects.filter(usuario=usuario, fecha_hora__date=hoy).order_by('-fecha_hora').first()


def proximo_tipo(usuario):
    ultima = ultima_marcacion_de_hoy(usuario)
    if ultima and ultima.tipo == Marcacion.Tipo.ENTRADA:
        return Marcacion.Tipo.SALIDA
    return Marcacion.Tipo.ENTRADA


def registrar_marcacion(usuario, latitud, longitud):
    """Registra la entrada o salida del usuario si está dentro del radio de su sucursal.

    El tipo alterna: si la última marcación del día fue una entrada, la siguiente es una salida.
    """
    sucursal = usuario.sucursal
    if sucursal is None:
        raise ValidationError('No tiene una sucursal asignada. Pida al administrador que se la asigne.')
    distancia = distancia_metros(float(latitud), float(longitud), float(sucursal.latitud), float(sucursal.longitud))
    if distancia > sucursal.radio_metros:
        raise ValidationError(
            f'Está a {distancia:.0f} m de la sucursal {sucursal}. '
            f'Debe estar a menos de {sucursal.radio_metros} m para marcar.'
        )
    return Marcacion.objects.create(
        usuario=usuario, sucursal=sucursal, tipo=proximo_tipo(usuario),
        latitud=Decimal(str(latitud)).quantize(Decimal('0.000001')),
        longitud=Decimal(str(longitud)).quantize(Decimal('0.000001')),
        distancia_metros=round(distancia),
    )
