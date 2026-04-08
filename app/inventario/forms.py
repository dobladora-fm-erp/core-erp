from django import forms
from .models import Item

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = [
            'codigo_sku', 'nombre', 'codigo_barras',
            'tipo_item', 'categoria', 'unidad_medida_base',
            'precio_base', 'costo_promedio', 'porcentaje_iva', 'maneja_inventario'
        ]
        widgets = {
            'codigo_sku': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo_barras': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_item': forms.Select(attrs={'class': 'form-select'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'unidad_medida_base': forms.Select(attrs={'class': 'form-select'}),
            'precio_base': forms.NumberInput(attrs={'class': 'form-control'}),
            'costo_promedio': forms.NumberInput(attrs={'class': 'form-control'}),
            'porcentaje_iva': forms.NumberInput(attrs={'class': 'form-control'}),
            'maneja_inventario': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
