from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import CuentaPorCobrar, CuentaPorPagar, CuentaBancaria
from .forms import PagoRecibidoForm, PagoEmitidoForm, CuentaBancariaForm

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

@login_required
def cuenta_bancaria_crear_view(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'ajax' in request.GET
    if request.method == 'POST':
        form = CuentaBancariaForm(request.POST)
        if form.is_valid():
            banco = form.save()
            if is_ajax:
                return JsonResponse({'success': True, 'id': banco.id, 'text': str(banco)})
            messages.success(request, f'Cuenta {banco} creada exitosamente.')
            return redirect('tesoreria_lista')
    else:
        form = CuentaBancariaForm()
    
    return render(request, 'tesoreria/form_banco.html', {'form': form, 'titulo': 'Nueva Cuenta Bancaria', 'is_ajax': is_ajax})

@login_required
def cuenta_bancaria_editar_view(request, banco_id):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'ajax' in request.GET
    banco = get_object_or_404(CuentaBancaria, id=banco_id)
    if request.method == 'POST':
        form = CuentaBancariaForm(request.POST, instance=banco)
        if form.is_valid():
            form.save()
            if is_ajax:
                return JsonResponse({'success': True, 'id': banco.id, 'text': str(banco)})
            messages.success(request, f'Cuenta actualizada exitosamente.')
            return redirect('tesoreria_lista')
    else:
        form = CuentaBancariaForm(instance=banco)
        
    return render(request, 'tesoreria/form_banco.html', {'form': form, 'titulo': f'Editar Cuenta: {banco}', 'is_ajax': is_ajax})

@login_required
def cuenta_bancaria_ver_view(request, banco_id):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'ajax' in request.GET
    banco = get_object_or_404(CuentaBancaria, id=banco_id)
    form = CuentaBancariaForm(instance=banco)
    return render(request, 'tesoreria/form_banco.html', {'form': form, 'titulo': f'Ver Cuenta: {banco}', 'is_ajax': is_ajax})
