from django.urls import path

from . import views

urlpatterns = [
    path('', views.marcar, name='asistencia_marcar'),
    path('mi-historial/', views.mi_historial, name='asistencia_mi_historial'),
    path('todas/', views.todas, name='asistencia_todas'),
]
