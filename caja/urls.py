from django.urls import path

from . import views

urlpatterns = [
    path('', views.mi_caja, name='mi_caja'),
    path('abrir/', views.abrir, name='caja_abrir'),
    path('movimiento/', views.movimiento, name='caja_movimiento'),
    path('cerrar/', views.cerrar, name='caja_cerrar'),
    path('todas/', views.todas, name='caja_todas'),
    path('<int:pk>/', views.detalle, name='caja_detalle'),
]
