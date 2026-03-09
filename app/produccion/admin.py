from django.contrib import admin
from django.core.exceptions import ValidationError
from .models import OrdenProduccion, InsumoConsumido, ProductoGenerado

class InsumoConsumidoInline(admin.TabularInline):
    model = InsumoConsumido
    extra = 1
    def has_add_permission(self, request, obj=None):
        if obj and obj.estado == 'Finalizada': return False
        return super().has_add_permission(request, obj)
    def has_change_permission(self, request, obj=None):
        if obj and obj.estado == 'Finalizada': return False
        return super().has_change_permission(request, obj)
    def has_delete_permission(self, request, obj=None):
        if obj and obj.estado == 'Finalizada': return False
        return super().has_delete_permission(request, obj)

class ProductoGeneradoInline(admin.TabularInline):
    model = ProductoGenerado
    extra = 1
    def has_add_permission(self, request, obj=None):
        if obj and obj.estado == 'Finalizada': return False
        return super().has_add_permission(request, obj)
    def has_change_permission(self, request, obj=None):
        if obj and obj.estado == 'Finalizada': return False
        return super().has_change_permission(request, obj)
    def has_delete_permission(self, request, obj=None):
        if obj and obj.estado == 'Finalizada': return False
        return super().has_delete_permission(request, obj)

@admin.register(OrdenProduccion)
class OrdenProduccionAdmin(admin.ModelAdmin):
    list_display = ('numero_orden', 'fecha_creacion', 'estado', 'procesada')
    list_filter = ('estado', 'fecha_creacion')
    inlines = [InsumoConsumidoInline, ProductoGeneradoInline]

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.estado == 'Finalizada':
            return [f.name for f in self.model._meta.fields]
        return self.readonly_fields

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        obj = form.instance

        if obj.estado == 'Finalizada' and not obj.procesada:
            from inventario.models import MovimientoInventario, InventarioBodega
            from django.db import transaction
            
            with transaction.atomic():
                # 1. Validar y descontar Insumos (Materia Prima)
                for insumo in obj.insumos.all():
                    saldo = InventarioBodega.objects.filter(item=insumo.item, bodega=insumo.bodega_origen).first()
                    cantidad_disponible = saldo.cantidad_actual if saldo else 0
                    if cantidad_disponible < insumo.cantidad:
                        raise ValidationError(f"Stock insuficiente para procesar {insumo.item}. Disponible: {cantidad_disponible}")
                    
                    MovimientoInventario.objects.create(
                        item=insumo.item,
                        bodega_origen=insumo.bodega_origen,
                        tipo_movimiento='Salida',
                        cantidad=insumo.cantidad,
                        costo_unitario=insumo.item.costo_promedio,
                        concepto=f"Consumo OP: {obj.numero_orden}",
                        usuario=request.user
                    )
                
                # 2. Ingresar Productos Terminados y Retales
                for prod in obj.productos.all():
                    MovimientoInventario.objects.create(
                        item=prod.item,
                        bodega_destino=prod.bodega_destino,
                        tipo_movimiento='Entrada',
                        cantidad=prod.cantidad,
                        costo_unitario=prod.costo_unitario_asignado,
                        concepto=f"Producción OP: {obj.numero_orden}",
                        usuario=request.user
                    )
                
                obj.procesada = True
                obj.save(update_fields=['procesada'])
