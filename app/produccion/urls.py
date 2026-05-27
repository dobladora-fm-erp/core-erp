from django.urls import path
from . import views

urlpatterns = [
    path('lista/', views.produccion_lista_view, name='produccion_lista'),
    path('nueva/', views.produccion_crear_view, name='produccion_crear'),
    path('<int:orden_id>/', views.produccion_detalle_view, name='produccion_detalle'),
    path('<int:orden_id>/anular/', views.produccion_anular_view, name='produccion_anular'),
]
