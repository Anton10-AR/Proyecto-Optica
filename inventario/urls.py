from django.urls import path

from . import views

urlpatterns = [
    path('articulos/', views.articulo_lista, name='articulo_lista'),
    path('articulos/nuevo/', views.ArticuloCrearView.as_view(), name='articulo_crear'),
    path('articulos/<int:pk>/', views.articulo_detalle, name='articulo_detalle'),
    path('articulos/<int:pk>/editar/', views.ArticuloEditarView.as_view(), name='articulo_editar'),
    path('categorias/', views.CategoriaListaView.as_view(), name='categoria_lista'),
    path('categorias/nueva/', views.CategoriaCrearView.as_view(), name='categoria_crear'),
    path('categorias/<int:pk>/editar/', views.CategoriaEditarView.as_view(), name='categoria_editar'),
    path('proveedores/', views.proveedor_lista, name='proveedor_lista'),
    path('proveedores/nuevo/', views.ProveedorCrearView.as_view(), name='proveedor_crear'),
    path('proveedores/<int:pk>/editar/', views.ProveedorEditarView.as_view(), name='proveedor_editar'),
]
