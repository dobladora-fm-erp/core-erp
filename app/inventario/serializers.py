from rest_framework import serializers
from .models import Item, InventarioBodega

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'codigo_sku', 'nombre', 'precio_base']

class InventarioBodegaSerializer(serializers.ModelSerializer):
    item = ItemSerializer(read_only=True)
    bodega_nombre = serializers.CharField(source='bodega.nombre', read_only=True)
    
    class Meta:
        model = InventarioBodega
        fields = ['id', 'item', 'bodega_nombre', 'cantidad_actual']
