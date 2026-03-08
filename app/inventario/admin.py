from django.contrib import admin
from .models import UnidadMedida, CategoriaItem, Item, ConversionUnidad, Bodega, InventarioBodega, MovimientoInventario

@admin.register(UnidadMedida)
class UnidadMedidaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'abreviatura')
    search_fields = ('nombre', 'abreviatura')

@admin.register(CategoriaItem)
class CategoriaItemAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

class ConversionUnidadInline(admin.TabularInline):
    model = ConversionUnidad
    extra = 1

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('codigo_sku', 'nombre', 'tipo_item', 'unidad_medida_base', 'precio_base')
    search_fields = ('codigo_sku', 'nombre', 'codigo_barras')
    list_filter = ('tipo_item', 'categoria', 'maneja_inventario')
    inlines = [ConversionUnidadInline]

@admin.register(ConversionUnidad)
class ConversionUnidadAdmin(admin.ModelAdmin):
    list_display = ('item', 'unidad_alternativa', 'factor_multiplicador')
    search_fields = ('item__nombre', 'item__codigo_sku')
    list_filter = ('unidad_alternativa',)

@admin.register(Bodega)
class BodegaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'direccion', 'es_activa')
    search_fields = ('nombre',)
    list_filter = ('es_activa',)

@admin.register(InventarioBodega)
class InventarioBodegaAdmin(admin.ModelAdmin):
    list_display = ('item', 'bodega', 'cantidad_actual')
    search_fields = ('item__nombre', 'item__codigo_sku', 'bodega__nombre')
    list_filter = ('bodega',)

@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ('fecha_movimiento', 'item', 'tipo_movimiento', 'cantidad', 'usuario')
    search_fields = ('item__nombre', 'item__codigo_sku', 'concepto')
    list_filter = ('tipo_movimiento', 'bodega_origen', 'bodega_destino', 'fecha_movimiento')
    
    # KARDEX INMUTABLE: Deshabilitar permisos de agregar, modificar y eliminar desde el Admin
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

