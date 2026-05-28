from django.urls import path
from . import views

urlpatterns = [
    path('lista/', views.ventas_lista_view, name='ventas_lista'),
    path('nueva/', views.venta_crear_view, name='venta_crear'),
    path('<int:factura_id>/', views.venta_detalle_view, name='venta_detalle'),
    path('<int:factura_id>/anular/', views.anular_venta_view, name='venta_anular'),
    path('<int:factura_id>/pdf/', views.venta_pdf_view, name='venta_pdf'),
    path('<int:factura_id>/emitir-dian/', views.emitir_factura_dian_view, name='venta_emitir_dian'),
]
