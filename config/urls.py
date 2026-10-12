from django.contrib import admin
from django.urls import include, path

from core import views as core_views

urlpatterns = [
    path('', core_views.inicio, name='inicio'),
    path('cuentas/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
]
