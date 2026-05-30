from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from .models import CuentaPorCobrar, CuentaPorPagar, CuentaBancaria
from .forms import PagoRecibidoForm, PagoEmitidoForm, CuentaBancariaForm
from core.audit import registrar_log

@login_required
def tesoreria_lista_view(request):
    filtro_estado = request.GET.get('estado', 'Pendiente')
    
    cxc_qs = CuentaPorCobrar.objects.select_related('factura_origen', 'cliente').order_by('fecha_vencimiento')
    cxp_qs = CuentaPorPagar.objects.select_related('factura_origen', 'proveedor').order_by('fecha_vencimiento')
    
    if filtro_estado != 'Todas':
        cxc_qs = cxc_qs.filter(estado=filtro_estado)
        cxp_qs = cxp_qs.filter(estado=filtro_estado)
    
    paginator_cxc = Paginator(cxc_qs, 15)
    paginator_cxp = Paginator(cxp_qs, 15)
    
    page_cxc = request.GET.get('page_cxc', 1)
    page_cxp = request.GET.get('page_cxp', 1)
    
    cxc = paginator_cxc.get_page(page_cxc)
    cxp = paginator_cxp.get_page(page_cxp)
    
    return render(request, 'tesoreria/lista_tesoreria.html', {
        'cxc': cxc, 'cxp': cxp, 'filtro_estado': filtro_estado
    })

@login_required
@transaction.atomic
def registrar_pago_recibido_view(request):
    if request.method == 'POST':
        form = PagoRecibidoForm(request.POST)
        if form.is_valid():
            try:
                pago = form.save(commit=False)
                # 1. Guardar el pago PRIMERO (dispara full_clean con saldo original)
                pago.save()
                # 2. DESPUÉS modificar saldos con bloqueo de fila
                cxc = CuentaPorCobrar.objects.select_for_update().get(id=pago.cuenta_por_cobrar.id)
                banco = CuentaBancaria.objects.select_for_update().get(id=pago.cuenta_destino.id)
                cxc.saldo_pendiente -= pago.monto
                if cxc.saldo_pendiente <= 0:
                    cxc.estado = 'Pagada'
                cxc.save()
                banco.saldo_actual += pago.monto
                banco.save()
                messages.success(request, f'Pago recibido exitosamente por valor de ${pago.monto}.')
                registrar_log(request, 'Pago', 'Tesorería', f'Pago recibido de ${pago.monto} para CxC #{pago.cuenta_por_cobrar.id} en {banco.nombre}')
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
@transaction.atomic
def registrar_pago_emitido_view(request):
    if request.method == 'POST':
        form = PagoEmitidoForm(request.POST)
        if form.is_valid():
            try:
                pago = form.save(commit=False)
                # 1. Guardar el pago PRIMERO (dispara full_clean con saldo original)
                pago.save()
                # 2. DESPUÉS modificar saldos con bloqueo de fila
                cxp = CuentaPorPagar.objects.select_for_update().get(id=pago.cuenta_por_pagar.id)
                banco = CuentaBancaria.objects.select_for_update().get(id=pago.cuenta_origen.id)
                if banco.saldo_actual < pago.monto:
                    raise ValidationError(f'Fondos insuficientes en la cuenta bancaria seleccionada. Disponible: ${banco.saldo_actual}, Requerido: ${pago.monto}')
                cxp.saldo_pendiente -= pago.monto
                if cxp.saldo_pendiente <= 0:
                    cxp.estado = 'Pagada'
                cxp.save()
                banco.saldo_actual -= pago.monto
                banco.save()
                messages.success(request, f'Pago emitido exitosamente por valor de ${pago.monto}.')
                registrar_log(request, 'Pago', 'Tesorería', f'Pago emitido de ${pago.monto} para CxP #{pago.cuenta_por_pagar.id} desde {banco.nombre}')
                return redirect('tesoreria_lista')
            except ValidationError as e:
                messages.error(request, e.message)
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
            if is_ajax:
                return JsonResponse({'success': False, 'errors': form.errors.get_json_data()}, status=400)
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
            if is_ajax:
                return JsonResponse({'success': False, 'errors': form.errors.get_json_data()}, status=400)
    else:
        form = CuentaBancariaForm(instance=banco)
        
    return render(request, 'tesoreria/form_banco.html', {'form': form, 'titulo': f'Editar Cuenta: {banco}', 'is_ajax': is_ajax})

@login_required
def cuenta_bancaria_ver_view(request, banco_id):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'ajax' in request.GET
    banco = get_object_or_404(CuentaBancaria, id=banco_id)
    form = CuentaBancariaForm(instance=banco)
    return render(request, 'tesoreria/form_banco.html', {'form': form, 'titulo': f'Ver Cuenta: {banco}', 'is_ajax': is_ajax})

@login_required
def historial_abonos_cxc_view(request, cxc_id):
    from .models import PagoRecibido
    cxc = get_object_or_404(CuentaPorCobrar, id=cxc_id)
    pagos = PagoRecibido.objects.filter(cuenta_por_cobrar=cxc).select_related('cuenta_destino').order_by('-fecha_pago')
    
    return render(request, 'tesoreria/historial_abonos.html', {
        'cxc': cxc,
        'pagos': pagos,
    })
