from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CuentaPorCobrar, CuentaPorPagar
from .forms import PagoRecibidoForm, PagoEmitidoForm

@login_required
def tesoreria_lista_view(request):
    cxc = CuentaPorCobrar.objects.select_related('factura_origen', 'cliente').all().order_by('fecha_vencimiento')
    cxp = CuentaPorPagar.objects.select_related('factura_origen', 'proveedor').all().order_by('fecha_vencimiento')
    return render(request, 'tesoreria/lista_tesoreria.html', {'cxc': cxc, 'cxp': cxp})

@login_required
def registrar_pago_recibido_view(request):
    if request.method == 'POST':
        form = PagoRecibidoForm(request.POST)
        if form.is_valid():
            try:
                pago = form.save()
                messages.success(request, f'Pago recibido exitosamente por valor de ${pago.monto}.')
                return redirect('tesoreria_lista')
            except Exception as e:
                messages.error(request, f'Error validando pago: {str(e)}')
    else:
        # Pre-seleccionar cuenta si viene en GET
        cxc_id = request.GET.get('cxc')
        initial_data = {}
        if cxc_id:
            initial_data['cuenta_por_cobrar'] = cxc_id
        form = PagoRecibidoForm(initial=initial_data)
        
    return render(request, 'tesoreria/registrar_pago_recibido.html', {'form': form})

@login_required
def registrar_pago_emitido_view(request):
    if request.method == 'POST':
        form = PagoEmitidoForm(request.POST)
        if form.is_valid():
            try:
                pago = form.save()
                messages.success(request, f'Pago emitido exitosamente por valor de ${pago.monto}.')
                return redirect('tesoreria_lista')
            except Exception as e:
                messages.error(request, f'Error validando pago: {str(e)}')
    else:
        # Pre-seleccionar cuenta si viene en GET
        cxp_id = request.GET.get('cxp')
        initial_data = {}
        if cxp_id:
            initial_data['cuenta_por_pagar'] = cxp_id
        form = PagoEmitidoForm(initial=initial_data)

    return render(request, 'tesoreria/registrar_pago_emitido.html', {'form': form})
