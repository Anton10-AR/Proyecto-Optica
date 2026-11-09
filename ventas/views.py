import csv
from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from caja.servicios import caja_abierta
from core.models import Configuracion, Sucursal
from core.views import requiere_alguno

from . import reportes, servicios
from .forms import (
    AnularForm, AutorizarEntregaForm, ClienteForm, LineasVentaFormSet, PagoForm, RecetaChoiceField, RecetaForm,
    ReporteVentasForm, VentaForm,
)
from .models import Cliente, OrdenTrabajo, Receta, Venta

# Quién consulta clientes y recetas: quien los registra, quien vende, el gerente y el taller.
VER_CLIENTES = ('ventas.gestionar_clientes', 'ventas.registrar_receta', 'ventas.ver_todas_ventas',
                'ventas.ver_ordenes')


def _puede_ver_venta(usuario, venta):
    return venta.vendedor == usuario or usuario.has_perm('ventas.ver_todas_ventas')


def _mensajes_de_error(request, error):
    messages.error(request, ' '.join(error.messages))


# ---------- Ventas ----------

@login_required
def lista(request):
    usuario = request.user
    if usuario.has_perm('ventas.ver_todas_ventas'):
        ventas = Venta.objects.all()
    elif usuario.has_perm('ventas.registrar_venta'):
        ventas = Venta.objects.filter(vendedor=usuario)
    else:
        raise PermissionDenied
    ventas = ventas.select_related('vendedor', 'sucursal')
    pagina = Paginator(ventas, 20).get_page(request.GET.get('pagina'))
    return render(request, 'ventas/lista.html', {'pagina': pagina})


@login_required
@permission_required('ventas.registrar_venta', raise_exception=True)
def crear(request):
    if caja_abierta(request.user) is None:
        messages.warning(request, 'Debe abrir su caja antes de registrar ventas.')
        return redirect('mi_caja')
    inicial = {}
    cliente = Cliente.objects.filter(pk=request.GET.get('cliente') or 0).first()
    if cliente:
        inicial['cliente'] = cliente.pk
        receta = cliente.recetas.filter(pk=request.GET.get('receta') or 0).first() or cliente.recetas.first()
        inicial['receta'] = receta.pk if receta else None
    form = VentaForm(request.POST or None, initial=inicial)
    lineas = LineasVentaFormSet(request.POST or None, prefix='lineas',
                                form_kwargs={'sucursal': request.user.sucursal_id})
    if request.method == 'POST' and form.is_valid() and lineas.is_valid():
        try:
            venta = servicios.registrar_venta(request.user, lineas=lineas.lineas('cantidad'), **form.cleaned_data)
        except ValidationError as error:
            for mensaje in error.messages:
                form.add_error(None, mensaje)
        else:
            mensaje = f'Venta {venta.numero} registrada.'
            if hasattr(venta, 'orden'):
                mensaje += f' Se generó la {venta.orden} para el taller.'
            messages.success(request, mensaje)
            return redirect('venta_detalle', pk=venta.pk)
    articulos = lineas.empty_form.fields['articulo'].queryset
    return render(request, 'ventas/form.html', {
        'form': form, 'lineas': lineas,
        'precios': {str(a.pk): str(a.precio_venta) for a in articulos},
        'con_receta': [str(a.pk) for a in articulos if a.requiere_receta],
        'anticipo_porcentaje': Configuracion.actual().anticipo_minimo_porcentaje,
    })


@login_required
@permission_required('ventas.registrar_venta', raise_exception=True)
def recetas_del_cliente(request):
    """Opciones del campo «Receta» para el cliente elegido en la venta (HTMX)."""
    campo = RecetaChoiceField(queryset=Receta.objects.filter(cliente_id=request.GET.get('cliente') or 0),
                              empty_label='—')
    opciones = [('', '—')] + [(r.pk, campo.label_from_instance(r)) for r in campo.queryset]
    return render(request, 'ventas/_opciones.html', {'opciones': opciones})


@login_required
def detalle(request, pk):
    venta = get_object_or_404(Venta.objects.select_related('vendedor', 'sucursal', 'usuario_anulacion', 'cliente'),
                              pk=pk)
    if not _puede_ver_venta(request.user, venta):
        raise PermissionDenied
    orden = OrdenTrabajo.objects.filter(venta=venta).first()
    puede_anular = (venta.estado == Venta.Estado.VIGENTE and request.user.has_perm('ventas.anular_venta')
                    and not (orden and orden.estado == OrdenTrabajo.Estado.ENTREGADO))
    puede_cobrar = (venta.saldo > 0 and venta.estado == Venta.Estado.VIGENTE
                    and request.user.has_perm('ventas.registrar_venta'))
    return render(request, 'ventas/detalle.html', {
        'venta': venta, 'pagos': venta.pagos.select_related('usuario'), 'orden': orden,
        'detalles': venta.detalles.select_related('articulo').order_by('pk'), 'puede_anular': puede_anular,
        'pago_form': PagoForm(initial={'monto': venta.saldo}) if puede_cobrar else None,
    })


@require_POST
@login_required
@permission_required('ventas.registrar_venta', raise_exception=True)
def cobrar(request, pk):
    venta = get_object_or_404(Venta, pk=pk)
    form = PagoForm(request.POST)
    if form.is_valid():
        try:
            servicios.registrar_pago(venta, request.user, form.cleaned_data['monto'], form.cleaned_data['forma_pago'])
            messages.success(request, 'Pago registrado.')
        except ValidationError as error:
            _mensajes_de_error(request, error)
    else:
        messages.error(request, 'Revise el monto y la forma de pago.')
    # Al entregar un trabajo, quien cobra el saldo puede no ser el vendedor: vuelve a la orden, que sí puede ver.
    orden = OrdenTrabajo.objects.filter(venta=venta).first()
    if request.POST.get('desde') == 'orden' and orden:
        return redirect('orden_detalle', pk=orden.pk)
    return redirect('venta_detalle', pk=venta.pk)


@login_required
def nota(request, pk):
    """Nota de venta imprimible, con el vendedor en el encabezado."""
    venta = get_object_or_404(Venta.objects.select_related('vendedor', 'sucursal'), pk=pk)
    if not _puede_ver_venta(request.user, venta):
        raise PermissionDenied
    return render(request, 'ventas/nota.html', {
        'venta': venta, 'pagos': venta.pagos.all(), 'orden': OrdenTrabajo.objects.filter(venta=venta).first(),
        'detalles': venta.detalles.select_related('articulo').order_by('pk'),
    })


@login_required
@permission_required('ventas.anular_venta', raise_exception=True)
def anular(request, pk):
    """Anula la venta con un motivo: repone el stock y devuelve lo pagado desde la caja de quien anula."""
    venta = get_object_or_404(Venta.objects.select_related('vendedor', 'sucursal'), pk=pk)
    if venta.estado != Venta.Estado.VIGENTE:
        messages.info(request, f'La {venta} ya está anulada.')
        return redirect('venta_detalle', pk=venta.pk)
    form = AnularForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        try:
            servicios.anular_venta(venta, request.user, form.cleaned_data['motivo'])
        except ValidationError as error:
            for mensaje in error.messages:
                form.add_error(None, mensaje)
        else:
            messages.success(request, f'La {venta} quedó anulada. El stock se repuso.')
            return redirect('venta_detalle', pk=venta.pk)
    return render(request, 'ventas/anular.html', {
        'venta': venta, 'form': form, 'tiene_caja': caja_abierta(request.user) is not None,
        'orden': OrdenTrabajo.objects.filter(venta=venta).first(),
    })


# ---------- Clientes (RF05) ----------

@requiere_alguno(*VER_CLIENTES)
def cliente_lista(request):
    clientes = Cliente.objects.annotate(cantidad_recetas=Count('recetas', distinct=True))
    q = request.GET.get('q', '').strip()
    if q:
        clientes = clientes.filter(Q(nombre__icontains=q) | Q(ci_nit__icontains=q) | Q(telefono__icontains=q))
    pagina = Paginator(clientes.order_by('nombre'), 20).get_page(request.GET.get('pagina'))
    return render(request, 'ventas/clientes/lista.html', {
        'pagina': pagina, 'q': q, 'filtros': urlencode({'q': q}),
    })


@requiere_alguno(*VER_CLIENTES)
def cliente_detalle(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    ventas = cliente.ventas.select_related('vendedor', 'sucursal')
    if not request.user.has_perm('ventas.ver_todas_ventas'):
        ventas = ventas.filter(vendedor=request.user)
    return render(request, 'ventas/clientes/detalle.html', {
        'cliente': cliente, 'recetas': cliente.recetas.select_related('optico'),
        'ventas': ventas[:20], 'ordenes': OrdenTrabajo.objects.filter(venta__cliente=cliente).select_related('venta'),
    })


@login_required
@permission_required('ventas.gestionar_clientes', raise_exception=True)
def cliente_form(request, pk=None):
    cliente = get_object_or_404(Cliente, pk=pk) if pk else None
    form = ClienteForm(request.POST or None, instance=cliente)
    if request.method == 'POST' and form.is_valid():
        cliente = form.save()
        messages.success(request, f'Se guardó el cliente {cliente}.')
        return redirect('cliente_detalle', pk=cliente.pk)
    return render(request, 'ventas/clientes/form.html', {'form': form, 'cliente': cliente})


# ---------- Recetas (RF21, RF22) ----------

@login_required
@permission_required('ventas.registrar_receta', raise_exception=True)
def receta_crear(request, cliente_pk):
    cliente = get_object_or_404(Cliente, pk=cliente_pk)
    form = RecetaForm(request.POST or None, cliente=cliente, usuario=request.user)
    if request.method == 'POST' and form.is_valid():
        receta = form.save()
        messages.success(request, f'Se registró la receta del {receta.fecha:%d/%m/%Y} para {cliente}.')
        return redirect('cliente_detalle', pk=cliente.pk)
    return render(request, 'ventas/recetas/form.html', {'form': form, 'cliente': cliente})


@requiere_alguno(*VER_CLIENTES)
def receta_detalle(request, pk):
    receta = get_object_or_404(Receta.objects.select_related('cliente', 'optico', 'registrado_por'), pk=pk)
    return render(request, 'ventas/recetas/detalle.html', {
        'receta': receta, 'ordenes': receta.ordenes.select_related('venta'),
    })


# ---------- Órdenes de trabajo (RF23, RF24, RF31) ----------

@login_required
@permission_required('ventas.ver_ordenes', raise_exception=True)
def orden_lista(request):
    estado = request.GET.get('estado', 'activas')
    sucursales = Sucursal.objects.filter(activa=True)
    valor = request.GET.get('sucursal')
    if valor is None:
        sucursal = request.user.sucursal
    else:
        sucursal = sucursales.filter(pk=valor).first() if valor.isdigit() else None
    ordenes = OrdenTrabajo.objects.select_related('venta', 'venta__sucursal', 'venta__cliente', 'receta')
    if sucursal:
        ordenes = ordenes.filter(venta__sucursal=sucursal)
    conteo = dict(ordenes.values_list('estado').annotate(n=Count('id')))
    if estado == 'activas':
        ordenes = ordenes.filter(estado__in=[OrdenTrabajo.Estado.PENDIENTE, OrdenTrabajo.Estado.EN_TALLER,
                                             OrdenTrabajo.Estado.LISTO]).order_by('fecha')
    elif estado in OrdenTrabajo.Estado.values:
        ordenes = ordenes.filter(estado=estado)
    estados = [(valor, nombre, conteo.get(valor, 0)) for valor, nombre in OrdenTrabajo.Estado.choices]
    pagina = Paginator(ordenes, 25).get_page(request.GET.get('pagina'))
    return render(request, 'ventas/ordenes/lista.html', {
        'pagina': pagina, 'estado': estado, 'estados': estados, 'sucursal': sucursal, 'sucursales': sucursales,
        'activas': sum(conteo.get(e, 0) for e in (OrdenTrabajo.Estado.PENDIENTE, OrdenTrabajo.Estado.EN_TALLER,
                                                  OrdenTrabajo.Estado.LISTO)),
        'filtros': urlencode({'estado': estado, 'sucursal': sucursal.pk if sucursal else 'todas'}),
    })


@login_required
@permission_required('ventas.ver_ordenes', raise_exception=True)
def orden_detalle(request, pk):
    orden = get_object_or_404(OrdenTrabajo.objects.select_related(
        'venta', 'venta__sucursal', 'venta__vendedor', 'venta__cliente', 'receta', 'receta__optico',
        'entrega_autorizada_por'), pk=pk)
    venta, usuario = orden.venta, request.user
    con_saldo = venta.saldo > 0
    return render(request, 'ventas/ordenes/detalle.html', {
        'orden': orden, 'venta': venta, 'receta': orden.receta,
        'detalles': venta.detalles.select_related('articulo').order_by('pk'),
        'eventos': orden.eventos.select_related('usuario'),
        'puede_ver_venta': _puede_ver_venta(usuario, venta),
        'puede_avanzar': orden.siguiente_estado and usuario.has_perm('ventas.actualizar_ordenes'),
        'puede_entregar': orden.estado == OrdenTrabajo.Estado.LISTO and usuario.has_perm('ventas.entregar_ordenes'),
        'entrega_bloqueada': con_saldo and not orden.entrega_autorizada,
        'autorizar_form': AutorizarEntregaForm() if (
            orden.activa and con_saldo and not orden.entrega_autorizada
            and usuario.has_perm('ventas.autorizar_entrega_con_saldo')) else None,
        'pago_form': PagoForm(initial={'monto': venta.saldo}) if (
            orden.activa and con_saldo and usuario.has_perm('ventas.registrar_venta')) else None,
    })


def _operar_orden(request, pk, operacion, exito):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    try:
        orden = operacion(orden)
    except ValidationError as error:
        _mensajes_de_error(request, error)
    else:
        messages.success(request, exito.format(orden=orden, estado=orden.get_estado_display().lower()))
    return redirect('orden_detalle', pk=pk)


@require_POST
@login_required
@permission_required('ventas.actualizar_ordenes', raise_exception=True)
def orden_avanzar(request, pk):
    return _operar_orden(request, pk, lambda o: servicios.avanzar_orden(o, request.user, request.POST.get('nota')),
                         'La {orden} pasó a «{estado}».')


@require_POST
@login_required
@permission_required('ventas.autorizar_entrega_con_saldo', raise_exception=True)
def orden_autorizar(request, pk):
    form = AutorizarEntregaForm(request.POST)
    if not form.is_valid():
        messages.error(request, 'Indique el motivo de la autorización.')
        return redirect('orden_detalle', pk=pk)
    return _operar_orden(request, pk, lambda o: servicios.autorizar_entrega(o, request.user, form.cleaned_data['motivo']),
                         'Se autorizó la entrega de la {orden} con saldo pendiente.')


@require_POST
@login_required
@permission_required('ventas.entregar_ordenes', raise_exception=True)
def orden_entregar(request, pk):
    return _operar_orden(request, pk, lambda o: servicios.entregar_orden(o, request.user),
                         'La {orden} se entregó al cliente.')


# ---------- Reportes de ventas (RF07) ----------

VISTAS_REPORTE = [('resumen', 'Resumen'), ('vendedores', 'Por vendedor'), ('productos', 'Por producto')]


def _numero(valor):
    """Número con coma decimal, como lo espera Excel en español."""
    return str(valor).replace('.', ',')


def _csv(nombre, encabezados, filas):
    respuesta = HttpResponse(content_type='text/csv; charset=utf-8')
    respuesta['Content-Disposition'] = f'attachment; filename="{nombre}.csv"'
    respuesta.write('\ufeff')  # BOM: Excel abre el archivo como UTF-8.
    escritor = csv.writer(respuesta, delimiter=';')
    escritor.writerow(encabezados)
    escritor.writerows(filas)
    return respuesta


@login_required
@permission_required('ventas.ver_todas_ventas', raise_exception=True)
def reporte(request):
    """Ventas por período, vendedor y producto (RF07)."""
    vista = request.GET.get('vista') if request.GET.get('vista') in dict(VISTAS_REPORTE) else 'resumen'
    form = ReporteVentasForm(request.GET or None)
    desde, hasta, sucursal, vendedor = form.filtros()
    filtros = {'desde': f'{desde:%Y-%m-%d}', 'hasta': f'{hasta:%Y-%m-%d}',
               'sucursal': sucursal.pk if sucursal else '', 'vendedor': vendedor.pk if vendedor else ''}
    contexto = {'form': form, 'vista': vista, 'vistas': VISTAS_REPORTE, 'desde': desde, 'hasta': hasta,
                'sucursal': sucursal, 'vendedor': vendedor, 'filtros': urlencode(filtros),
                'ver_costos': request.user.has_perm('inventario.ver_kardex')}
    nombre = f'ventas_{vista}_{desde:%Y-%m-%d}_a_{hasta:%Y-%m-%d}'
    exportar = request.GET.get('formato') == 'csv'

    if vista == 'vendedores':
        filas = reportes.por_vendedor(desde, hasta, sucursal, vendedor)
        if exportar:
            return _csv(nombre, ['Vendedor', 'Sucursal', 'Ventas', 'Total (Bs)', 'Descuentos (Bs)',
                                 'Ticket promedio (Bs)', 'Saldo pendiente (Bs)'],
                        [[f['vendedor'], f['sucursales'], f['cantidad'], _numero(f['total']),
                          _numero(f['descuentos']), _numero(f['ticket_promedio']), _numero(f['saldo'])]
                         for f in filas])
        contexto['filas'] = filas
        contexto['totales'] = {c: sum(f[c] for f in filas) for c in ('cantidad', 'total', 'descuentos', 'saldo')}
    elif vista == 'productos':
        filas, sin_detalle = reportes.por_producto(desde, hasta, sucursal, vendedor)
        if exportar:
            encabezados = ['Código', 'Artículo', 'Categoría', 'Unidades', 'Importe (Bs)']
            if contexto['ver_costos']:
                encabezados += ['Costo (Bs)', 'Margen (Bs)', 'Margen (%)']
            return _csv(nombre, encabezados, [
                [f['articulo__codigo'], f['articulo__nombre'], f['articulo__categoria__nombre'], f['unidades'],
                 _numero(f['importe'])]
                + ([_numero(f['costo']), _numero(f['margen']), _numero(f['margen_porcentaje'] or '')]
                   if contexto['ver_costos'] else [])
                for f in filas])
        contexto.update(filas=filas, sin_detalle=sin_detalle,
                        totales={c: sum(f[c] for f in filas) for c in ('unidades', 'importe', 'costo', 'margen')})
    else:
        datos = reportes.resumen(desde, hasta, sucursal, vendedor)
        if exportar:
            return _csv(nombre, ['Fecha', 'Ventas', 'Total (Bs)'],
                        [[f'{d["dia"]:%d/%m/%Y}', d['cantidad'], _numero(d['total'])] for d in datos['dias']])
        contexto['datos'] = datos
    return render(request, 'ventas/reporte.html', contexto)
