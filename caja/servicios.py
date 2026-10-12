from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import FormaPago, MovimientoCaja, SesionCaja


def caja_abierta(usuario):
    return SesionCaja.objects.filter(usuario=usuario, estado=SesionCaja.Estado.ABIERTA).first()


def abrir_caja(usuario, monto_inicial, observacion=''):
    if usuario.sucursal_id is None:
        raise ValidationError('No tiene una sucursal asignada. Pida al administrador que se la asigne.')
    if caja_abierta(usuario):
        raise ValidationError('Ya tiene una caja abierta.')
    return SesionCaja.objects.create(
        usuario=usuario, sucursal_id=usuario.sucursal_id,
        monto_inicial=monto_inicial, observacion=observacion,
    )


def registrar_movimiento(usuario, tipo, forma_pago, monto, concepto):
    """Registra un movimiento en la caja abierta del usuario. Debe llamarse dentro de una transacción
    si forma parte de una operación mayor (por ejemplo, el cobro de una venta)."""
    sesion = caja_abierta(usuario)
    if sesion is None:
        raise ValidationError('Debe abrir su caja antes de registrar movimientos.')
    es_egreso_efectivo = tipo == MovimientoCaja.Tipo.EGRESO and forma_pago == FormaPago.EFECTIVO
    if es_egreso_efectivo and monto > sesion.efectivo_esperado:
        raise ValidationError('El egreso supera el efectivo disponible en caja.')
    return MovimientoCaja.objects.create(
        sesion=sesion, usuario=usuario, tipo=tipo, forma_pago=forma_pago, monto=monto, concepto=concepto,
    )


@transaction.atomic
def cerrar_caja(usuario, monto_contado, observacion=''):
    sesion = caja_abierta(usuario)
    if sesion is None:
        raise ValidationError('No tiene una caja abierta.')
    sesion = SesionCaja.objects.select_for_update().get(pk=sesion.pk)
    sesion.monto_esperado = sesion.efectivo_esperado
    sesion.monto_contado = monto_contado
    sesion.fecha_cierre = timezone.now()
    sesion.estado = SesionCaja.Estado.CERRADA
    if observacion:
        sesion.observacion = observacion
    sesion.save()
    return sesion
