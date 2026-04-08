from django import forms
from .models import Tercero

class TerceroForm(forms.ModelForm):
    class Meta:
        model = Tercero
        fields = [
            'es_cliente', 'es_proveedor', 'es_empleado',
            'tipo_documento', 'numero_identificacion', 'dv', 'tipo_persona',
            'razon_social', 'nombres', 'apellidos',
            'municipio', 'direccion', 'telefono', 'correo_electronico',
            'regimen_iva', 'responsabilidades_fiscales'
        ]
        widgets = {
            'es_cliente': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'es_proveedor': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'es_empleado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'tipo_documento': forms.Select(attrs={'class': 'form-select'}),
            'numero_identificacion': forms.TextInput(attrs={'class': 'form-control'}),
            'dv': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_persona': forms.Select(attrs={'class': 'form-select', 'id': 'id_tipo_persona'}),
            'razon_social': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_razon_social'}),
            'nombres': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_nombres'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_apellidos'}),
            'municipio': forms.Select(attrs={'class': 'form-select'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'correo_electronico': forms.EmailInput(attrs={'class': 'form-control'}),
            'regimen_iva': forms.Select(attrs={'class': 'form-select'}),
            'responsabilidades_fiscales': forms.TextInput(attrs={'class': 'form-control'}),
        }
