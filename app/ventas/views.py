from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import FacturaVenta

@login_required
def ventas_lista_view(request):
    facturas = FacturaVenta.objects.select_related('cliente').all().order_by('-fecha_emision')
    return render(request, 'ventas/lista_ventas.html', {'facturas': facturas})
