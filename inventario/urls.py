from django.urls import path

from . import views

urlpatterns = [
    path('articulos/', views.articulo_lista, name='articulo_lista'),
    path('articulos/nuevo/', views.ArticuloCrearView.as_view(), name='articulo_crear'),
    path('articulos/<int:pk>/', views.articulo_detalle, name='articulo_detalle'),
    path('articulos/<int:pk>/editar/', views.ArticuloEditarView.as_view(), name='articulo_editar'),
    path('articulos/<int:pk>/kardex/', views.kardex, name='kardex'),
    path('categorias/', views.CategoriaListaView.as_view(), name='categoria_lista'),
    path('categorias/nueva/', views.CategoriaCrearView.as_view(), name='categoria_crear'),
    path('categorias/<int:pk>/editar/', views.CategoriaEditarView.as_view(), name='categoria_editar'),
    path('proveedores/', views.proveedor_lista, name='proveedor_lista'),
    path('proveedores/nuevo/', views.ProveedorCrearView.as_view(), name='proveedor_crear'),
    path('proveedores/<int:pk>/editar/', views.ProveedorEditarView.as_view(), name='proveedor_editar'),
    path('ingresos/', views.ingreso_lista, name='ingreso_lista'),
    path('ingresos/nuevo/', views.ingreso_crear, name='ingreso_crear'),
    path('ingresos/<int:pk>/', views.ingreso_detalle, name='ingreso_detalle'),
    path('ajustes/', views.ajuste_lista, name='ajuste_lista'),
    path('ajustes/nuevo/', views.ajuste_crear, name='ajuste_crear'),
    path('traspasos/', views.traspaso_lista, name='traspaso_lista'),
    path('traspasos/nuevo/', views.traspaso_crear, name='traspaso_crear'),
    path('traspasos/<int:pk>/', views.traspaso_detalle, name='traspaso_detalle'),
    path('traspasos/<int:pk>/recibir/', views.traspaso_recibir, name='traspaso_recibir'),
]
