from django.contrib import admin
from .models import UnidadMedida, CategoriaItem, Item, ConversionUnidad

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
