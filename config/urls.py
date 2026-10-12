from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from core import views as core_views

urlpatterns = [
    path('', core_views.inicio, name='inicio'),
    path('cuentas/login/', core_views.LoginView.as_view(), name='login'),
    path('cuentas/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('cuentas/clave/', core_views.CambiarClaveView.as_view(), name='password_change'),
    path('administracion/', include('core.urls')),
    path('caja/', include('caja.urls')),
    path('ventas/', include('ventas.urls')),
    path('asistencia/', include('asistencia.urls')),
    path('admin/', admin.site.urls),
]
