from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import FacturaCompra, DetalleCompra
from .forms import FacturaCompraForm, DetalleCompraFormSet
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum
from decimal import Decimal
from tesoreria.models import CuentaPorPagar
from inventario.models import InventarioBodega, MovimientoInventario

@login_required
def compras_lista_view(request):
    facturas = FacturaCompra.objects.select_related('proveedor').all().order_by('-fecha_emision')
    return render(request, 'compras/lista_compras.html', {'facturas': facturas})

@login_required
def compra_crear_view(request):
    if request.method == 'POST':
        form = FacturaCompraForm(request.POST)
        formset = DetalleCompraFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    # Validar si hay items reales (ignorando los marcados para eliminar)
                    valido = False
                    for f in formset.forms:
                        if f.cleaned_data and not f.cleaned_data.get('DELETE', False):
                            valido = True
                            break
                            
                    if not valido:
                        messages.error(request, 'Debes agregar al menos un ítem a la factura de compra.')
                        return render(request, 'compras/crear_compra.html', {'form': form, 'formset': formset})

                    factura = form.save(commit=False)
                    factura.estado = 'Confirmada'
                    factura.subtotal = Decimal('0.00')
                    factura.impuestos = Decimal('0.00')
                    factura.total = Decimal('0.00')
                    factura.save()
                    
                    detalles = formset.save(commit=False)
                    subtotal_factura = Decimal('0.00')
                    
                    for detalle in detalles:
                        detalle.factura = factura
                        detalle.subtotal = detalle.cantidad * detalle.costo_unitario
                        detalle.save()
                        subtotal_factura += detalle.subtotal
                        
                        item = detalle.item
                        
                        # 1. Alimentar InventarioBodega
                        inv_bodega, created = InventarioBodega.objects.select_for_update().get_or_create(
                            item=item, 
                            bodega=detalle.bodega_destino,
                            defaults={'cantidad_actual': Decimal('0.00')}
                        )
                        inv_bodega.cantidad_actual += detalle.cantidad
                        inv_bodega.save()
                        
                        # 2. Registrar el Movimiento (Kardex)
                        MovimientoInventario.objects.create(
                            item=item,
                            bodega_destino=detalle.bodega_destino,
                            tipo_movimiento='Entrada',
                            cantidad=detalle.cantidad,
                            costo_unitario=detalle.costo_unitario, # Costo exacto para Kardex transaccional
                            concepto=f"Factura Compra {factura.numero_factura_proveedor}",
                            usuario=request.user
                        )
                        
                        # 3. Recalcular Costo Promedio Unitario en Item Maestro
                        stock_actual = InventarioBodega.objects.filter(item=item).aggregate(Sum('cantidad_actual'))['cantidad_actual__sum'] or Decimal('0.00')
                        stock_antes = stock_actual - detalle.cantidad
                        costo_antes = item.costo_promedio
                        
                        if stock_actual > 0:
                            # Formula costo ponderado
                            nuevo_costo = ((stock_antes * costo_antes) + (detalle.cantidad * detalle.costo_unitario)) / stock_actual
                            item.costo_promedio = nuevo_costo
                            item.save()

                    for detalle_borrado in formset.deleted_objects:
                        detalle_borrado.delete()
                    
                    factura.subtotal = subtotal_factura
                    factura.impuestos = factura.subtotal * Decimal('0.19') # IVA 19%
                    factura.total = factura.subtotal + factura.impuestos
                    factura.save()
                    
                    # Generar Cuenta por Pagar (Tesorería)
                    CuentaPorPagar.objects.create(
                        factura_origen=factura,
                        proveedor=factura.proveedor,
                        fecha_vencimiento=factura.fecha_vencimiento,
                        monto_total=factura.total,
                        saldo_pendiente=factura.total
                    )

                    messages.success(request, f'Factura {factura.numero_factura_proveedor} registrada: Kardex alimentado y CxP Automática generada.')
                    return redirect('compras_lista')
            except Exception as e:
                messages.error(request, f'Error validando la compra: {str(e)}')
    else:
        form = FacturaCompraForm()
        formset = DetalleCompraFormSet()
    
    return render(request, 'compras/crear_compra.html', {'form': form, 'formset': formset})

@login_required
def compra_detalle_view(request, factura_id):
    factura = get_object_or_404(FacturaCompra, id=factura_id)
    detalles = factura.detalles.all()

    return render(request, 'compras/detalle_compra.html', {
        'factura': factura,
        'detalles': detalles
    })

# Podemos retirar o ignorar compra_detalle_eliminar_view y compra_confirmar_view ya que la facturación es en 1 solo paso.
