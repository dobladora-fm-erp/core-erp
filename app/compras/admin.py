from django.contrib import admin
from django.db import transaction
from decimal import Decimal
from .models import FacturaCompra, DetalleCompra
from inventario.models import MovimientoInventario

class DetalleCompraInline(admin.TabularInline):
    model = DetalleCompra
    extra = 1

    def has_add_permission(self, request, obj=None):
        if obj and obj.estado == 'Confirmada': return False
        return super().has_add_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        if obj and obj.estado == 'Confirmada': return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.estado == 'Confirmada': return False
        return super().has_delete_permission(request, obj)

@admin.register(FacturaCompra)
class FacturaCompraAdmin(admin.ModelAdmin):
    list_display = ('numero_factura_proveedor', 'proveedor', 'fecha_emision', 'total', 'estado', 'procesada')
    search_fields = ('numero_factura_proveedor', 'proveedor__razon_social', 'proveedor__numero_identificacion')
    list_filter = ('estado', 'fecha_emision', 'procesada')
    inlines = [DetalleCompraInline]

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.estado == 'Confirmada':
            return [f.name for f in self.model._meta.fields]
        return self.readonly_fields

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        obj = form.instance
        
        # 1. Autocálculo de Totales
        total_detalles = sum(detalle.subtotal for detalle in obj.detalles.all())
        iva_calculado = total_detalles * Decimal('0.19') # Calculamos 19% de IVA
        
        obj.subtotal = total_detalles
        obj.impuestos = iva_calculado
        obj.total = total_detalles + iva_calculado
        obj.save(update_fields=['subtotal', 'impuestos', 'total'])

        # 2. Lógica del Kardex (Solo si no está procesada)
        if obj.estado == 'Confirmada' and not obj.procesada:
            from inventario.models import MovimientoInventario
            from django.db import transaction
            with transaction.atomic():
                for detalle in obj.detalles.all():
                    MovimientoInventario.objects.create(
                        item=detalle.item,
                        bodega_destino=detalle.bodega_destino,
                        tipo_movimiento='Entrada',
                        cantidad=detalle.cantidad,
                        costo_unitario=detalle.costo_unitario,
                        concepto=f"Compra Factura Proveedor: {obj.numero_factura_proveedor}",
                        usuario=request.user
                    )
                obj.procesada = True
                obj.save(update_fields=['procesada'])


