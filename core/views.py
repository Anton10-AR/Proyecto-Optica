from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, ListView, UpdateView

from .auditoria import Accion, registrar
from .forms import CambiarClaveForm, LoginForm, ResetearClaveForm, SucursalForm, UsuarioCrearForm, UsuarioForm
from .models import RegistroActividad, Sucursal, Usuario


class PermisoMixin(LoginRequiredMixin, PermissionRequiredMixin):
    raise_exception = True


def usuarios_gestionables(request):
    """Un administrador que no es superusuario no puede modificar cuentas de superusuario."""
    usuarios = Usuario.objects.all()
    if not request.user.is_superuser:
        usuarios = usuarios.filter(is_superuser=False)
    return usuarios


@login_required
def inicio(request):
    return render(request, 'core/inicio.html')


# ---------- Sesión ----------

class LoginView(auth_views.LoginView):
    form_class = LoginForm
    redirect_authenticated_user = True


class CambiarClaveView(auth_views.PasswordChangeView):
    form_class = CambiarClaveForm
    success_url = reverse_lazy('inicio')

    def form_valid(self, form):
        respuesta = super().form_valid(form)
        usuario = self.request.user
        if usuario.debe_cambiar_clave:
            usuario.debe_cambiar_clave = False
            usuario.save(update_fields=['debe_cambiar_clave'])
        registrar(Accion.CAMBIO_CLAVE, self.request, afectado=usuario)
        messages.success(self.request, 'Su contraseña se cambió correctamente.')
        return respuesta


# ---------- Usuarios ----------

@login_required
@permission_required('core.view_usuario', raise_exception=True)
def usuario_lista(request):
    usuarios = Usuario.objects.select_related('rol', 'sucursal')
    q = request.GET.get('q', '').strip()
    rol = request.GET.get('rol', '')
    estado = request.GET.get('estado', '')
    if q:
        usuarios = usuarios.filter(
            Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(ci__icontains=q) | Q(username__icontains=q)
        )
    if rol:
        usuarios = usuarios.filter(rol_id=rol)
    if estado in ('activo', 'inactivo'):
        usuarios = usuarios.filter(is_active=(estado == 'activo'))
    pagina = Paginator(usuarios, 15).get_page(request.GET.get('pagina'))
    contexto = {'pagina': pagina, 'roles': Group.objects.order_by('name'), 'q': q, 'rol': rol, 'estado': estado}
    # Con HTMX (búsqueda en vivo) solo se devuelve la tabla.
    plantilla = 'core/usuarios/_tabla.html' if request.headers.get('HX-Request') else 'core/usuarios/lista.html'
    return render(request, plantilla, contexto)


class UsuarioCrearView(PermisoMixin, CreateView):
    permission_required = 'core.add_usuario'
    model = Usuario
    form_class = UsuarioCrearForm
    template_name = 'core/usuarios/form.html'
    success_url = reverse_lazy('usuario_lista')

    @transaction.atomic
    def form_valid(self, form):
        respuesta = super().form_valid(form)
        registrar(Accion.CREACION_USUARIO, self.request, afectado=self.object,
                  detalle=f'Rol: {self.object.rol}')
        messages.success(self.request, f'Se creó el usuario {self.object.username}.')
        return respuesta


class UsuarioEditarView(PermisoMixin, UpdateView):
    permission_required = 'core.change_usuario'
    model = Usuario
    form_class = UsuarioForm
    template_name = 'core/usuarios/form.html'
    success_url = reverse_lazy('usuario_lista')

    def get_queryset(self):
        return usuarios_gestionables(self.request)

    @transaction.atomic
    def form_valid(self, form):
        cambios = ', '.join(form.changed_data)
        respuesta = super().form_valid(form)
        if cambios:
            registrar(Accion.ACTUALIZACION_USUARIO, self.request, afectado=self.object,
                      detalle=f'Campos modificados: {cambios}')
        messages.success(self.request, f'Se actualizó el usuario {self.object.username}.')
        return respuesta


@login_required
@permission_required('core.change_usuario', raise_exception=True)
def usuario_resetear_clave(request, pk):
    usuario = get_object_or_404(usuarios_gestionables(request), pk=pk)
    form = ResetearClaveForm(usuario, request.POST or None)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            form.save(commit=False)
            usuario.debe_cambiar_clave = True
            usuario.save()
            registrar(Accion.RESETEO_CLAVE, request, afectado=usuario)
        messages.success(request, f'Se reseteó la contraseña de {usuario.username}. '
                                  'Deberá cambiarla en su próximo inicio de sesión.')
        return redirect('usuario_lista')
    return render(request, 'core/usuarios/resetear_clave.html', {'form': form, 'usuario_obj': usuario})


@require_POST
@login_required
@permission_required('core.change_usuario', raise_exception=True)
def usuario_cambiar_estado(request, pk):
    """Baja lógica: desactiva o reactiva la cuenta sin borrar su historial.

    Una cuenta inactiva no puede iniciar sesión, y sus sesiones abiertas dejan de ser
    válidas en la siguiente petición (ModelBackend.get_user rechaza usuarios inactivos).
    """
    usuario = get_object_or_404(usuarios_gestionables(request), pk=pk)
    if usuario == request.user:
        raise PermissionDenied('No puede desactivar su propia cuenta.')
    with transaction.atomic():
        usuario.is_active = not usuario.is_active
        usuario.save(update_fields=['is_active'])
        accion = Accion.REACTIVACION_USUARIO if usuario.is_active else Accion.DESACTIVACION_USUARIO
        registrar(accion, request, afectado=usuario)
    estado = 'reactivó' if usuario.is_active else 'desactivó'
    messages.success(request, f'Se {estado} la cuenta de {usuario.username}.')
    return redirect('usuario_lista')


class ActividadListaView(PermisoMixin, ListView):
    permission_required = 'core.view_registroactividad'
    model = RegistroActividad
    template_name = 'core/actividad_lista.html'
    paginate_by = 25

    def get_queryset(self):
        registros = RegistroActividad.objects.select_related('usuario', 'usuario_afectado')
        accion = self.request.GET.get('accion', '')
        if accion:
            registros = registros.filter(accion=accion)
        return registros

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['acciones'] = RegistroActividad.Accion.choices
        contexto['accion'] = self.request.GET.get('accion', '')
        return contexto


# ---------- Sucursales ----------

class SucursalListaView(PermisoMixin, ListView):
    permission_required = 'core.view_sucursal'
    model = Sucursal
    template_name = 'core/sucursales/lista.html'


class SucursalCrearView(PermisoMixin, CreateView):
    permission_required = 'core.add_sucursal'
    model = Sucursal
    form_class = SucursalForm
    template_name = 'core/sucursales/form.html'
    success_url = reverse_lazy('sucursal_lista')


class SucursalEditarView(PermisoMixin, UpdateView):
    permission_required = 'core.change_sucursal'
    model = Sucursal
    form_class = SucursalForm
    template_name = 'core/sucursales/form.html'
    success_url = reverse_lazy('sucursal_lista')
