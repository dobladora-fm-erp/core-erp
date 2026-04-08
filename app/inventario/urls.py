from django.urls import path
from . import views

urlpatterns = [
    path('lista/', views.inventario_lista_view, name='inventario_lista'),
    path('items/', views.items_lista_view, name='items_lista'),
    path('items/crear/', views.item_crear_view, name='item_crear'),
    path('items/<int:item_id>/editar/', views.item_editar_view, name='item_editar'),
]
