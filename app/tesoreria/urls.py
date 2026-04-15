from django.urls import path
from . import views

urlpatterns = [
    path('lista/', views.tesoreria_lista_view, name='tesoreria_lista'),
    path('pagos-recibidos/registrar/', views.registrar_pago_recibido_view, name='registrar_pago_recibido'),
    path('pagos-emitidos/registrar/', views.registrar_pago_emitido_view, name='registrar_pago_emitido'),
    path('bancos/crear/', views.cuenta_bancaria_crear_view, name='cuenta_bancaria_crear'),
    path('bancos/<int:banco_id>/editar/', views.cuenta_bancaria_editar_view, name='cuenta_bancaria_editar'),
    path('bancos/<int:banco_id>/ver/', views.cuenta_bancaria_ver_view, name='cuenta_bancaria_ver'),
]
