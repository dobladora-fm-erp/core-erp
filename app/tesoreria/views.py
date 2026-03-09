from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import CuentaPorCobrar, CuentaPorPagar

@login_required
def tesoreria_lista_view(request):
    cxc = CuentaPorCobrar.objects.select_related('factura_origen', 'cliente').all().order_by('fecha_vencimiento')
    cxp = CuentaPorPagar.objects.select_related('factura_origen', 'proveedor').all().order_by('fecha_vencimiento')
    return render(request, 'tesoreria/lista_tesoreria.html', {'cxc': cxc, 'cxp': cxp})
