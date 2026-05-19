from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import CuentaBancaria, CuentaPorCobrar, CuentaPorPagar, PagoRecibido, PagoEmitido

@admin.register(CuentaBancaria)
class CuentaBancariaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'entidad_bancaria', 'tipo_cuenta', 'saldo_actual')
    # Bloqueamos la edición manual del saldo para evitar fraudes
    readonly_fields = ('saldo_actual',)

@admin.register(CuentaPorCobrar)
class CuentaPorCobrarAdmin(admin.ModelAdmin):
    list_display = ('factura_origen', 'cliente', 'monto_total', 'saldo_pendiente', 'estado', 'fecha_vencimiento')
    list_filter = ('estado', 'fecha_vencimiento')
    readonly_fields = ('monto_total', 'saldo_pendiente', 'estado')

@admin.register(CuentaPorPagar)
class CuentaPorPagarAdmin(admin.ModelAdmin):
    list_display = ('factura_origen', 'proveedor', 'monto_total', 'saldo_pendiente', 'estado', 'fecha_vencimiento')
    list_filter = ('estado', 'fecha_vencimiento')
    readonly_fields = ('monto_total', 'saldo_pendiente', 'estado')

@admin.register(PagoRecibido)
class PagoRecibidoAdmin(admin.ModelAdmin):
    list_display = ('cuenta_por_cobrar', 'monto', 'cuenta_destino', 'fecha_pago')
    readonly_fields = ('fecha_pago',)

    def has_change_permission(self, request, obj=None):
        return False # Pagos inmutables
    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(PagoEmitido)
class PagoEmitidoAdmin(admin.ModelAdmin):
    list_display = ('cuenta_por_pagar', 'monto', 'cuenta_origen', 'fecha_pago')
    readonly_fields = ('fecha_pago',)

    def has_change_permission(self, request, obj=None):
        return False # Pagos inmutables
    def has_delete_permission(self, request, obj=None):
        return False
