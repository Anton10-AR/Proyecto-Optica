from django.urls import path

from . import views

urlpatterns = [
    path('', views.lista, name='venta_lista'),
    path('nueva/', views.crear, name='venta_crear'),
    path('<int:pk>/', views.detalle, name='venta_detalle'),
    path('<int:pk>/cobrar/', views.cobrar, name='venta_cobrar'),
    path('<int:pk>/nota/', views.nota, name='venta_nota'),
]
