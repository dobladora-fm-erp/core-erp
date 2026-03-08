from django.contrib import admin
from django.core.exceptions import ValidationError
from decimal import Decimal
from .models import FacturaVenta, DetalleVenta

class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
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

@admin.register(FacturaVenta)
class FacturaVentaAdmin(admin.ModelAdmin):
    list_display = ('numero_factura', 'cliente', 'fecha_emision', 'total', 'estado', 'procesada')
    list_filter = ('estado', 'fecha_emision')
    search_fields = ('numero_factura', 'cliente__razon_social', 'cliente__numero_identificacion')
    inlines = [DetalleVentaInline]

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.estado == 'Confirmada':
            return [f.name for f in self.model._meta.fields]
        return self.readonly_fields

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        obj = form.instance
        
        # 1. Autocálculo de Totales
        total_detalles = sum(detalle.subtotal for detalle in obj.detalles.all())
        iva_calculado = total_detalles * Decimal('0.19')
        
        obj.subtotal = total_detalles
        obj.impuestos = iva_calculado
        obj.total = total_detalles + iva_calculado
        obj.save(update_fields=['subtotal', 'impuestos', 'total'])

        # 2. Validación de Stock y Trazabilidad Kardex
        if obj.estado == 'Confirmada' and not obj.procesada:
            from inventario.models import MovimientoInventario, InventarioBodega
            from django.db import transaction
            
            with transaction.atomic():
                for detalle in obj.detalles.all():
                    # Validación estricta de negativos
                    if detalle.item.maneja_inventario:
                        saldo = InventarioBodega.objects.filter(item=detalle.item, bodega=detalle.bodega_origen).first()
                        cantidad_disponible = saldo.cantidad_actual if saldo else 0
                        if cantidad_disponible < detalle.cantidad:
                            raise ValidationError(f"Stock insuficiente para {detalle.item}. Disponible: {cantidad_disponible}, Requerido: {detalle.cantidad}")

                    # Registro de salida en Kardex
                    MovimientoInventario.objects.create(
                        item=detalle.item,
                        bodega_origen=detalle.bodega_origen,
                        tipo_movimiento='Salida',
                        cantidad=detalle.cantidad,
                        costo_unitario=detalle.item.costo_promedio,
                        concepto=f"Venta Factura: {obj.numero_factura}",
                        usuario=request.user
                    )
                obj.procesada = True
                obj.save(update_fields=['procesada'])
