from django.urls import path
from . import views

urlpatterns = [
    path('lista/', views.tesoreria_lista_view, name='tesoreria_lista'),
    path('pagos-recibidos/registrar/', views.registrar_pago_recibido_view, name='registrar_pago_recibido'),
    path('pagos-emitidos/registrar/', views.registrar_pago_emitido_view, name='registrar_pago_emitido'),
]
