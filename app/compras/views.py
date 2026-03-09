from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import FacturaCompra

@login_required
def compras_lista_view(request):
    # Traemos las facturas ordenadas por la más reciente primero
    facturas = FacturaCompra.objects.select_related('proveedor').all().order_by('-fecha_emision')
    return render(request, 'compras/lista_compras.html', {'facturas': facturas})
