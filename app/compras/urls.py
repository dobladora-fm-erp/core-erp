from django.urls import path
from . import views

urlpatterns = [
    path('lista/', views.compras_lista_view, name='compras_lista'),
    path('nueva/', views.compra_crear_view, name='compra_crear'),
    path('<int:factura_id>/', views.compra_detalle_view, name='compra_detalle'),
]
