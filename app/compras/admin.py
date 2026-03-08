from django.contrib import admin
from django.db import transaction
from .models import FacturaCompra, DetalleCompra
from inventario.models import MovimientoInventario

class DetalleCompraInline(admin.TabularInline):
    model = DetalleCompra
    extra = 1

@admin.register(FacturaCompra)
class FacturaCompraAdmin(admin.ModelAdmin):
    list_display = ('numero_factura_proveedor', 'proveedor', 'fecha_emision', 'total', 'estado', 'procesada')
    search_fields = ('numero_factura_proveedor', 'proveedor__razon_social', 'proveedor__numero_identificacion')
    list_filter = ('estado', 'fecha_emision', 'procesada')
    inlines = [DetalleCompraInline]

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        
        factura = form.instance
        
        if factura.estado == 'Confirmada' and not factura.procesada:
            with transaction.atomic():
                # Actualizar los totales automáticamente basándose en los inlines ingresados
                factura.subtotal = sum(detalle.subtotal for detalle in factura.detalles.all())
                factura.total = factura.subtotal + factura.impuestos
                
                # Inyectar el inventario al Kardex
                for detalle in factura.detalles.all():
                    MovimientoInventario.objects.create(
                        item=detalle.item,
                        bodega_destino=detalle.bodega_destino,
                        usuario=request.user,
                        tipo_movimiento='Entrada',
                        cantidad=detalle.cantidad,
                        costo_unitario=detalle.costo_unitario,
                        concepto=f"Factura de Compra #{factura.numero_factura_proveedor} (Proveedor: {factura.proveedor.razon_social or factura.proveedor.numero_identificacion})"
                    )

                factura.procesada = True
                factura.save()

@admin.register(DetalleCompra)
class DetalleCompraAdmin(admin.ModelAdmin):
    list_display = ('factura', 'item', 'bodega_destino', 'cantidad', 'costo_unitario', 'subtotal')
    search_fields = ('factura__numero_factura_proveedor', 'item__nombre', 'item__codigo_sku')
    list_filter = ('bodega_destino',)
    readonly_fields = ('subtotal',)
