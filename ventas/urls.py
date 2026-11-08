from django.urls import path

from . import views

urlpatterns = [
    path('', views.lista, name='venta_lista'),
    path('nueva/', views.crear, name='venta_crear'),
    path('nueva/recetas/', views.recetas_del_cliente, name='venta_recetas'),
    path('<int:pk>/', views.detalle, name='venta_detalle'),
    path('<int:pk>/cobrar/', views.cobrar, name='venta_cobrar'),
    path('<int:pk>/nota/', views.nota, name='venta_nota'),
    path('<int:pk>/anular/', views.anular, name='venta_anular'),
    path('clientes/', views.cliente_lista, name='cliente_lista'),
    path('clientes/nuevo/', views.cliente_form, name='cliente_crear'),
    path('clientes/<int:pk>/', views.cliente_detalle, name='cliente_detalle'),
    path('clientes/<int:pk>/editar/', views.cliente_form, name='cliente_editar'),
    path('clientes/<int:cliente_pk>/recetas/nueva/', views.receta_crear, name='receta_crear'),
    path('recetas/<int:pk>/', views.receta_detalle, name='receta_detalle'),
    path('ordenes/', views.orden_lista, name='orden_lista'),
    path('ordenes/<int:pk>/', views.orden_detalle, name='orden_detalle'),
    path('ordenes/<int:pk>/avanzar/', views.orden_avanzar, name='orden_avanzar'),
    path('ordenes/<int:pk>/autorizar/', views.orden_autorizar, name='orden_autorizar'),
    path('ordenes/<int:pk>/entregar/', views.orden_entregar, name='orden_entregar'),
]
