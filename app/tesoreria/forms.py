from django import forms
from .models import PagoRecibido, PagoEmitido, CuentaPorCobrar, CuentaPorPagar

class PagoRecibidoForm(forms.ModelForm):
    class Meta:
        model = PagoRecibido
        fields = ['cuenta_por_cobrar', 'cuenta_destino', 'monto', 'referencia']
        widgets = {
            'cuenta_por_cobrar': forms.Select(attrs={'class': 'form-select'}),
            'cuenta_destino': forms.Select(attrs={'class': 'form-select'}),
            'monto': forms.NumberInput(attrs={'class': 'form-control'}),
            'referencia': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limitar cobros sólo a cuentas pendientes
        self.fields['cuenta_por_cobrar'].queryset = CuentaPorCobrar.objects.filter(estado='Pendiente')
        # Formatear la etiqueta para mayor claridad
        self.fields['cuenta_por_cobrar'].label_from_instance = lambda obj: f"CxC - {obj.cliente} - Saldo: ${obj.saldo_pendiente}"

class PagoEmitidoForm(forms.ModelForm):
    class Meta:
        model = PagoEmitido
        fields = ['cuenta_por_pagar', 'cuenta_origen', 'monto', 'referencia']
        widgets = {
            'cuenta_por_pagar': forms.Select(attrs={'class': 'form-select'}),
            'cuenta_origen': forms.Select(attrs={'class': 'form-select'}),
            'monto': forms.NumberInput(attrs={'class': 'form-control'}),
            'referencia': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limitar pagos sólo a cuentas pendientes
        self.fields['cuenta_por_pagar'].queryset = CuentaPorPagar.objects.filter(estado='Pendiente')
        self.fields['cuenta_por_pagar'].label_from_instance = lambda obj: f"CxP - {obj.proveedor} - Saldo: ${obj.saldo_pendiente}"
