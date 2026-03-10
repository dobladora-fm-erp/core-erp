from django import forms
from django.forms import inlineformset_factory
from .models import FacturaVenta, DetalleVenta

class FacturaVentaForm(forms.ModelForm):
    class Meta:
        model = FacturaVenta
        fields = ['cliente', 'fecha_vencimiento']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'fecha_vencimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class DetalleVentaForm(forms.ModelForm):
    class Meta:
        model = DetalleVenta
        fields = ['item', 'bodega_origen', 'cantidad', 'precio_unitario']
        widgets = {
            'item': forms.Select(attrs={'class': 'form-select form-control-sm item-select'}),
            'bodega_origen': forms.Select(attrs={'class': 'form-select form-control-sm'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control form-control-sm cantidad-input', 'step': '0.01', 'min': '0.01'}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control form-control-sm precio-input', 'step': '0.01', 'min': '0'}),
        }

DetalleVentaFormSet = inlineformset_factory(
    FacturaVenta,
    DetalleVenta,
    form=DetalleVentaForm,
    extra=1,
    can_delete=True
)
