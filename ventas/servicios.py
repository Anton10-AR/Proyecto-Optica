from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.formats import number_format

from caja.models import MovimientoCaja
from caja.servicios import caja_abierta, registrar_movimiento

from .models import Pago, Venta


@transaction.atomic
def registrar_pago(venta, usuario, monto, forma_pago):
    """Cobra un pago de la venta y lo registra como ingreso en la caja abierta del usuario."""
    venta = Venta.objects.select_for_update().get(pk=venta.pk)
    if venta.estado != Venta.Estado.VIGENTE:
        raise ValidationError('No se puede cobrar una venta anulada.')
    if monto > venta.saldo:
        raise ValidationError(f'El pago supera el saldo pendiente (Bs {number_format(venta.saldo, 2)}).')
    movimiento = registrar_movimiento(
        usuario, MovimientoCaja.Tipo.INGRESO, forma_pago, monto, f'Pago de la nota de venta {venta.numero}',
    )
    return Pago.objects.create(
        venta=venta, usuario=usuario, movimiento_caja=movimiento, monto=monto, forma_pago=forma_pago,
    )


@transaction.atomic
def registrar_venta(vendedor, cliente_nombre, cliente_ci, descripcion, total, monto_pago, forma_pago):
    """Registra la venta con el vendedor autenticado y cobra el pago inicial (anticipo o total)."""
    if caja_abierta(vendedor) is None:
        raise ValidationError('Debe abrir su caja antes de registrar ventas.')
    if monto_pago > total:
        raise ValidationError('El pago inicial no puede superar el total de la venta.')
    venta = Venta.objects.create(
        vendedor=vendedor, sucursal_id=vendedor.sucursal_id,
        cliente_nombre=cliente_nombre, cliente_ci=cliente_ci, descripcion=descripcion, total=total,
    )
    registrar_pago(venta, vendedor, monto_pago, forma_pago)
    return venta
