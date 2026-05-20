from django import forms
from .models import Item

class ItemForm(forms.ModelForm):
    precio_base = forms.DecimalField(localize=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    costo_promedio = forms.DecimalField(localize=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    porcentaje_iva = forms.DecimalField(localize=True, widget=forms.TextInput(attrs={'class': 'form-control'}))

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
            'maneja_inventario': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
