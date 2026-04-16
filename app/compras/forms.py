from django import forms
from django.forms import inlineformset_factory
from .models import FacturaCompra, DetalleCompra

class FacturaCompraForm(forms.ModelForm):
    class Meta:
        model = FacturaCompra
        fields = ['proveedor', 'numero_factura_proveedor', 'fecha_emision', 'fecha_vencimiento']
        widgets = {
            'proveedor': forms.Select(attrs={'class': 'form-select', 'data-add-url': '/terceros/crear/', 'data-edit-url': '/terceros/__id__/editar/', 'data-view-url': '/terceros/__id__/ver/'}),
            'numero_factura_proveedor': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_emision': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_vencimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class DetalleCompraForm(forms.ModelForm):
    class Meta:
        model = DetalleCompra
        fields = ['item', 'bodega_destino', 'cantidad', 'costo_unitario']
        widgets = {
            'item': forms.Select(attrs={'class': 'form-select form-control-sm item-select'}),
            'bodega_destino': forms.Select(attrs={'class': 'form-select form-control-sm'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control form-control-sm cantidad-input', 'step': '0.01', 'min': '0.01'}),
            'costo_unitario': forms.NumberInput(attrs={'class': 'form-control form-control-sm costo-input', 'step': '0.01', 'min': '0'}),
        }

DetalleCompraFormSet = inlineformset_factory(
    FacturaCompra,
    DetalleCompra,
    form=DetalleCompraForm,
    extra=1,
    can_delete=True
)
