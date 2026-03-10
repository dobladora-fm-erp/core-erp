from django.urls import path
from . import views

urlpatterns = [
    path('lista/', views.ventas_lista_view, name='ventas_lista'),
    path('nueva/', views.venta_crear_view, name='venta_crear'),
    path('<int:factura_id>/', views.venta_detalle_view, name='venta_detalle'),
]
