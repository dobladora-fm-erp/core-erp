from django.contrib import admin
from .models import Tercero

@admin.register(Tercero)
class TerceroAdmin(admin.ModelAdmin):
    list_display = (
        'numero_identificacion', 
        '__str__', 
        'es_cliente', 
        'es_proveedor', 
        'validacion_api_estado'
    )
    search_fields = ('numero_identificacion', 'razon_social', 'nombres', 'apellidos')
    list_filter = ('es_cliente', 'es_proveedor', 'es_empleado', 'validacion_api_estado', 'tipo_persona' , 'tipo_documento')

    def save_model(self, request, obj, form, change):
        # Additional custom logic if required could go here
        super().save_model(request, obj, form, change)
