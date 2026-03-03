from django.contrib import admin
from .models import Departamento, Municipio, ActividadCIIU, Empresa

@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ('codigo_dane', 'nombre')
    search_fields = ('codigo_dane', 'nombre')

@admin.register(Municipio)
class MunicipioAdmin(admin.ModelAdmin):
    list_display = ('codigo_dane', 'nombre', 'departamento')
    search_fields = ('codigo_dane', 'nombre')
    list_filter = ('departamento',)

@admin.register(ActividadCIIU)
class ActividadCIIUAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'descripcion')
    search_fields = ('codigo', 'descripcion')

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('razon_social', 'nit', 'dv', 'tipo_persona', 'municipio')
    search_fields = ('razon_social', 'nit')
    list_filter = ('tipo_persona', 'regimen_iva')
