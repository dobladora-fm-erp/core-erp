from django import forms
from django.forms import inlineformset_factory
from .models import OrdenProduccion, InsumoConsumido, ProductoGenerado

class OrdenProduccionForm(forms.ModelForm):
    class Meta:
        model = OrdenProduccion
        fields = ['observaciones']
        widgets = {
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Ej: Lote especial L-455 de tejas cortas'}),
        }

class InsumoConsumidoForm(forms.ModelForm):
    class Meta:
        model = InsumoConsumido
        fields = ['item', 'bodega_origen', 'cantidad']
        widgets = {
            'item': forms.Select(attrs={'class': 'form-select form-control-sm'}),
            'bodega_origen': forms.Select(attrs={'class': 'form-select form-control-sm'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01', 'min': '0.01'}),
        }

class ProductoGeneradoForm(forms.ModelForm):
    class Meta:
        model = ProductoGenerado
        fields = ['item', 'bodega_destino', 'cantidad', 'costo_unitario_asignado']
        widgets = {
            'item': forms.Select(attrs={'class': 'form-select form-control-sm'}),
            'bodega_destino': forms.Select(attrs={'class': 'form-select form-control-sm'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01', 'min': '0.01'}),
            'costo_unitario_asignado': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01', 'min': '0'}),
        }

InsumoFormSet = inlineformset_factory(
    OrdenProduccion,
    InsumoConsumido,
    form=InsumoConsumidoForm,
    extra=1,
    can_delete=True
)

ProductoFormSet = inlineformset_factory(
    OrdenProduccion,
    ProductoGenerado,
    form=ProductoGeneradoForm,
    extra=1,
    can_delete=True
)
