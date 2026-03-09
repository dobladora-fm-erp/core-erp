from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from ventas.models import FacturaVenta
from tesoreria.models import CuentaPorPagar, CuentaPorCobrar
from inventario.models import InventarioBodega
from django.utils.timezone import now

@login_required
def dashboard_view(request):
    mes_actual = now().month
    
    # Sumatoria de Ingresos (Ventas Confirmadas del mes)
    ingresos = FacturaVenta.objects.filter(estado='Confirmada', fecha_emision__month=mes_actual).aggregate(total=Sum('total'))['total'] or 0
    
    # Sumatoria de Carteras (Deudas pendientes)
    cxp = CuentaPorPagar.objects.filter(estado='Pendiente').aggregate(total=Sum('saldo_pendiente'))['total'] or 0
    cxc = CuentaPorCobrar.objects.filter(estado='Pendiente').aggregate(total=Sum('saldo_pendiente'))['total'] or 0
    
    # Conteo de Stock Crítico (Ítems con 15 unidades o menos)
    stock_critico = InventarioBodega.objects.filter(cantidad_actual__lte=15).count()

    context = {
        'ingresos_mes': ingresos,
        'cxp_total': cxp,
        'cxc_total': cxc,
        'stock_critico': stock_critico
    }
    return render(request, 'core/dashboard.html', context)
