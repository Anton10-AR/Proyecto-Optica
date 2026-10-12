from django.urls import path

from . import views

urlpatterns = [
    path('usuarios/', views.usuario_lista, name='usuario_lista'),
    path('usuarios/nuevo/', views.UsuarioCrearView.as_view(), name='usuario_crear'),
    path('usuarios/<int:pk>/editar/', views.UsuarioEditarView.as_view(), name='usuario_editar'),
    path('usuarios/<int:pk>/clave/', views.usuario_resetear_clave, name='usuario_resetear_clave'),
    path('usuarios/<int:pk>/estado/', views.usuario_cambiar_estado, name='usuario_cambiar_estado'),
    path('actividad/', views.ActividadListaView.as_view(), name='actividad_lista'),
    path('sucursales/', views.SucursalListaView.as_view(), name='sucursal_lista'),
    path('sucursales/nueva/', views.SucursalCrearView.as_view(), name='sucursal_crear'),
    path('sucursales/<int:pk>/editar/', views.SucursalEditarView.as_view(), name='sucursal_editar'),
]
