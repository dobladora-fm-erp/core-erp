from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('reportes/', views.centro_reportes_view, name='centro_reportes'),
    path('reportes/cartera/', views.reporte_cartera_view, name='reporte_cartera'),
    path('reportes/cartera/exportar/', views.exportar_cartera_csv, name='exportar_cartera_csv'),
    path('reportes/cartera-edades/', views.reporte_cartera_edades_view, name='reporte_cartera_edades'),
    path('reportes/inventario/', views.inventario_valorizado_view, name='inventario_valorizado'),
    path('reportes/inventario/exportar/', views.exportar_inventario_csv, name='exportar_inventario_csv'),
    path('reportes/flujo-caja/', views.flujo_caja_basico_view, name='flujo_caja_basico'),
    path('reportes/flujo-caja/exportar/', views.exportar_flujo_caja_csv, name='exportar_flujo_caja_csv'),
]
