from django.urls import path

from . import views

urlpatterns = [
    path('', views.marcar, name='asistencia_marcar'),
    path('mi-historial/', views.mi_historial, name='asistencia_mi_historial'),
    path('mi-asistencia/', views.mi_asistencia, name='asistencia_mia'),
    path('todas/', views.todas, name='asistencia_todas'),
    path('reporte/', views.reporte, name='asistencia_reporte'),
    path('reporte/<int:pk>/', views.reporte_empleado, name='asistencia_reporte_empleado'),
    path('personal/', views.personal_lista, name='personal_lista'),
    path('personal/<int:pk>/', views.empleado_ficha, name='empleado_ficha'),
    path('horarios/', views.horario_lista, name='horario_lista'),
    path('horarios/nuevo/', views.horario_form, name='horario_crear'),
    path('horarios/<int:pk>/editar/', views.horario_form, name='horario_editar'),
    path('permisos/', views.ausencia_lista, name='ausencia_lista'),
    path('permisos/<int:pk>/eliminar/', views.ausencia_eliminar, name='ausencia_eliminar'),
    path('feriados/', views.feriado_lista, name='feriado_lista'),
    path('feriados/<int:pk>/eliminar/', views.feriado_eliminar, name='feriado_eliminar'),
]
