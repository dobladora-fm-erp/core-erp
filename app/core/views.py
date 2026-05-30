from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q, F
from ventas.models import FacturaVenta
from tesoreria.models import CuentaPorPagar, CuentaPorCobrar, PagoRecibido, PagoEmitido
from inventario.models import InventarioBodega, Item
from terceros.models import Tercero
from django.utils.timezone import now

@login_required
def dashboard_view(request):
    # Selector de período (GET params o defaults)
    mes = request.GET.get('mes')
    anio = request.GET.get('anio')
    
    mes_seleccionado = int(mes) if mes else now().month
    anio_seleccionado = int(anio) if anio else now().year
    
    # Sumatoria de Ingresos (Ventas no anuladas del período seleccionado)
    ingresos = FacturaVenta.objects.filter(anulada=False, fecha_emision__year=anio_seleccionado, fecha_emision__month=mes_seleccionado).aggregate(total=Sum('total'))['total'] or 0
    
    # Sumatoria de Carteras (Deudas pendientes)
    cxp = CuentaPorPagar.objects.filter(estado='Pendiente').aggregate(total=Sum('saldo_pendiente'))['total'] or 0
    cxc = CuentaPorCobrar.objects.filter(estado='Pendiente').aggregate(total=Sum('saldo_pendiente'))['total'] or 0
    
    # Stock Crítico dinámico: ítems donde cantidad_actual <= stock_minimo del ítem
    alertas_stock = InventarioBodega.objects.select_related('item', 'bodega').filter(
        cantidad_actual__lte=F('item__stock_minimo'),
        item__maneja_inventario=True
    ).order_by('cantidad_actual')
    stock_critico = alertas_stock.count()

    # Rango de años para el selector
    anio_actual = now().year
    rango_anios = range(anio_actual - 2, anio_actual + 1)

    context = {
        'ingresos_mes': ingresos,
        'cxp_total': cxp,
        'cxc_total': cxc,
        'stock_critico': stock_critico,
        'alertas_stock': alertas_stock[:10],
        'mes_seleccionado': mes_seleccionado,
        'anio_seleccionado': anio_seleccionado,
        'rango_anios': rango_anios,
    }
    return render(request, 'core/dashboard.html', context)

@login_required
def centro_reportes_view(request):
    return render(request, 'core/centro_reportes.html')

@login_required
def reporte_cartera_view(request):
    # Consolidado de CxC y CxP agrupadas por Tercero
    # Se usa annotate para sumar los saldos de facturas pendientes
    terceros_cartera = Tercero.objects.annotate(
        cxc_total=Sum('cuentaporcobrar__saldo_pendiente', filter=Q(cuentaporcobrar__estado='Pendiente')),
        cxp_total=Sum('cuentaporpagar__saldo_pendiente', filter=Q(cuentaporpagar__estado='Pendiente'))
    ).filter(Q(cxc_total__gt=0) | Q(cxp_total__gt=0)).order_by('razon_social', 'nombres')

    context = {
        'terceros_cartera': terceros_cartera
    }
    return render(request, 'core/reporte_cartera.html', context)

@login_required
def inventario_valorizado_view(request):
    # Resumen del stock actual por Ítem y Bodega, multiplicado por su costo promedio
    # Se usa select_related para optimizar la consulta y annotate para calcular el valor total
    inventario_valorizado = InventarioBodega.objects.select_related('item', 'bodega').annotate(
        valor_total=F('cantidad_actual') * F('item__costo_promedio')
    ).filter(cantidad_actual__gt=0).order_by('item__nombre')

    # Total general del inventario valorizado
    total_general = inventario_valorizado.aggregate(total=Sum('valor_total'))['total'] or 0

    context = {
        'inventario_valorizado': inventario_valorizado,
        'total_general': total_general
    }
    return render(request, 'core/inventario_valorizado.html', context)

@login_required
def flujo_caja_basico_view(request):
    mes_actual = now().month
    anio_actual = now().year

    # Ingresos vs Egresos en el mes actual
    pagos_recibidos = PagoRecibido.objects.filter(fecha_pago__year=anio_actual, fecha_pago__month=mes_actual).aggregate(total=Sum('monto'))['total'] or 0
    pagos_emitidos = PagoEmitido.objects.filter(fecha_pago__year=anio_actual, fecha_pago__month=mes_actual).aggregate(total=Sum('monto'))['total'] or 0

    flujo_neto = pagos_recibidos - pagos_emitidos

    # Obtener el detalle si se desea mostrar
    detalle_ingresos = PagoRecibido.objects.filter(fecha_pago__year=anio_actual, fecha_pago__month=mes_actual).select_related('cuenta_por_cobrar__cliente', 'cuenta_destino')
    detalle_egresos = PagoEmitido.objects.filter(fecha_pago__year=anio_actual, fecha_pago__month=mes_actual).select_related('cuenta_por_pagar__proveedor', 'cuenta_origen')

    context = {
        'mes_actual': mes_actual,
        'anio_actual': anio_actual,
        'pagos_recibidos': pagos_recibidos,
        'pagos_emitidos': pagos_emitidos,
        'flujo_neto': flujo_neto,
        'detalle_ingresos': detalle_ingresos,
        'detalle_egresos': detalle_egresos
    }
    return render(request, 'core/flujo_caja.html', context)

import csv
from django.http import HttpResponse

@login_required
def exportar_cartera_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="Reporte_Cartera_{now().strftime("%Y%m%d_%H%M")}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Tercero', 'Identificacion', 'Cuentas por Cobrar (CxC)', 'Cuentas por Pagar (CxP)'])

    terceros_cartera = Tercero.objects.annotate(
        cxc_total=Sum('cuentaporcobrar__saldo_pendiente', filter=Q(cuentaporcobrar__estado='Pendiente')),
        cxp_total=Sum('cuentaporpagar__saldo_pendiente', filter=Q(cuentaporpagar__estado='Pendiente'))
    ).filter(Q(cxc_total__gt=0) | Q(cxp_total__gt=0)).order_by('razon_social', 'nombres')

    for tercero in terceros_cartera:
        nombre = tercero.razon_social or f"{tercero.nombres or ''} {tercero.apellidos or ''}".strip()
        writer.writerow([
            nombre,
            tercero.numero_identificacion,
            tercero.cxc_total or 0,
            tercero.cxp_total or 0
        ])

    return response

@login_required
def exportar_inventario_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="Inventario_Valorizado_{now().strftime("%Y%m%d_%H%M")}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Item', 'Codigo SKU', 'Bodega', 'Cantidad Actual', 'Costo Promedio', 'Valor Total'])

    inventario_valorizado = InventarioBodega.objects.select_related('item', 'bodega').annotate(
        valor_total=F('cantidad_actual') * F('item__costo_promedio')
    ).filter(cantidad_actual__gt=0).order_by('item__nombre')

    for inv in inventario_valorizado:
        writer.writerow([
            inv.item.nombre,
            inv.item.codigo_sku,
            inv.bodega.nombre,
            inv.cantidad_actual,
            inv.item.costo_promedio,
            inv.valor_total
        ])

    return response

@login_required
def exportar_flujo_caja_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="Flujo_Caja_{now().strftime("%Y%m%d_%H%M")}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Tipo de Movimiento', 'Fecha', 'Tercero', 'Cuenta Bancaria', 'Referencia', 'Monto'])

    mes_actual = now().month
    anio_actual = now().year

    detalle_ingresos = PagoRecibido.objects.filter(fecha_pago__year=anio_actual, fecha_pago__month=mes_actual).select_related('cuenta_por_cobrar__cliente', 'cuenta_destino')
    detalle_egresos = PagoEmitido.objects.filter(fecha_pago__year=anio_actual, fecha_pago__month=mes_actual).select_related('cuenta_por_pagar__proveedor', 'cuenta_origen')

    for ingreso in detalle_ingresos:
        tercero_str = ingreso.cuenta_por_cobrar.cliente.razon_social or f"{ingreso.cuenta_por_cobrar.cliente.nombres or ''} {ingreso.cuenta_por_cobrar.cliente.apellidos or ''}".strip()
        writer.writerow([
            'Ingreso (Pago Recibido)',
            ingreso.fecha_pago,
            tercero_str,
            ingreso.cuenta_destino.nombre,
            ingreso.referencia,
            ingreso.monto
        ])
        
    for egreso in detalle_egresos:
        tercero_str = egreso.cuenta_por_pagar.proveedor.razon_social or f"{egreso.cuenta_por_pagar.proveedor.nombres or ''} {egreso.cuenta_por_pagar.proveedor.apellidos or ''}".strip()
        writer.writerow([
            'Egreso (Pago Emitido)',
            egreso.fecha_pago,
            tercero_str,
            egreso.cuenta_origen.nombre,
            egreso.referencia,
            egreso.monto
        ])

    return response

@login_required
def reporte_cartera_edades_view(request):
    hoy = now().date()
    cxc_pendientes = CuentaPorCobrar.objects.select_related('cliente', 'factura_origen').filter(estado='Pendiente').order_by('fecha_vencimiento')
    
    cartera_0_30 = []
    cartera_31_60 = []
    cartera_mas_60 = []
    
    total_0_30 = 0
    total_31_60 = 0
    total_mas_60 = 0
    
    for cxc in cxc_pendientes:
        dias_mora = (hoy - cxc.fecha_vencimiento).days
        cxc.dias_mora = dias_mora if dias_mora > 0 else 0
        
        if cxc.dias_mora <= 30:
            cartera_0_30.append(cxc)
            total_0_30 += cxc.saldo_pendiente
        elif 31 <= cxc.dias_mora <= 60:
            cartera_31_60.append(cxc)
            total_31_60 += cxc.saldo_pendiente
        else:
            cartera_mas_60.append(cxc)
            total_mas_60 += cxc.saldo_pendiente
            
    total_general = total_0_30 + total_31_60 + total_mas_60
    
    context = {
        'cartera_0_30': cartera_0_30,
        'cartera_31_60': cartera_31_60,
        'cartera_mas_60': cartera_mas_60,
        'total_0_30': total_0_30,
        'total_31_60': total_31_60,
        'total_mas_60': total_mas_60,
        'total_general': total_general
    }
    return render(request, 'core/cartera_edades.html', context)
