from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import CuentaBancaria, CuentaPorCobrar, CuentaPorPagar, PagoRecibido, PagoEmitido

@admin.register(CuentaBancaria)
class CuentaBancariaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'saldo_actual')
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

    def save_model(self, request, obj, form, change):
        if not obj.pk: # Solo si es un pago nuevo
            with transaction.atomic():
                if obj.monto > obj.cuenta_por_cobrar.saldo_pendiente:
                    raise ValidationError("El pago no puede ser mayor al saldo pendiente.")
                
                # 1. Bajar saldo a la deuda
                cxc = obj.cuenta_por_cobrar
                cxc.saldo_pendiente -= obj.monto
                if cxc.saldo_pendiente <= 0:
                    cxc.estado = 'Pagada'
                cxc.save(update_fields=['saldo_pendiente', 'estado'])
                
                # 2. Subir plata al banco
                banco = obj.cuenta_destino
                banco.saldo_actual += obj.monto
                banco.save(update_fields=['saldo_actual'])
                
            super().save_model(request, obj, form, change)

@admin.register(PagoEmitido)
class PagoEmitidoAdmin(admin.ModelAdmin):
    list_display = ('cuenta_por_pagar', 'monto', 'cuenta_origen', 'fecha_pago')
    readonly_fields = ('fecha_pago',)

    def has_change_permission(self, request, obj=None):
        return False # Pagos inmutables
    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        if not obj.pk: # Solo si es un pago nuevo
            with transaction.atomic():
                if obj.monto > obj.cuenta_por_pagar.saldo_pendiente:
                    raise ValidationError("El pago no puede ser mayor a la deuda.")
                
                # 1. Bajar saldo a la deuda
                cxp = obj.cuenta_por_pagar
                cxp.saldo_pendiente -= obj.monto
                if cxp.saldo_pendiente <= 0:
                    cxp.estado = 'Pagada'
                cxp.save(update_fields=['saldo_pendiente', 'estado'])
                
                # 2. Restar plata del banco
                banco = obj.cuenta_origen
                banco.saldo_actual -= obj.monto
                banco.save(update_fields=['saldo_actual'])
                
            super().save_model(request, obj, form, change)
