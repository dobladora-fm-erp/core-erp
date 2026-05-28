from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import FacturaCompra, DetalleCompra
from .forms import FacturaCompraForm, DetalleCompraFormSet
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum
from decimal import Decimal
from inventario.models import InventarioBodega, MovimientoInventario
from core.audit import registrar_log

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
                    total_impuestos = Decimal('0.00')
                    
                    for detalle in detalles:
                        detalle.factura = factura
                        detalle.subtotal = detalle.cantidad * detalle.costo_unitario
                        detalle.save()
                        subtotal_factura += detalle.subtotal
                        
                        impuesto_linea = detalle.subtotal * (detalle.item.porcentaje_iva / Decimal('100.00'))
                        total_impuestos += impuesto_linea
                        
                        item = detalle.item
                        
                        # 1. Alimentar InventarioBodega
                        if item.maneja_inventario:
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
                    factura.impuestos = total_impuestos
                    factura.total = factura.subtotal + factura.impuestos
                    factura.save()

                    messages.success(request, f'Factura {factura.numero_factura_proveedor} registrada: Kardex alimentado y CxP Automática generada.')
                    registrar_log(request, 'Creación', 'Compras', f'Factura {factura.numero_factura_proveedor} registrada por ${factura.total}')
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

@login_required
@transaction.atomic
def compra_anular_view(request, factura_id):
    factura = get_object_or_404(FacturaCompra, id=factura_id)
    
    if request.method == 'POST':
        if factura.anulada:
            messages.error(request, 'La compra ya ha sido anulada previamente.')
            return redirect('compra_detalle', factura_id=factura.id)
            
        if hasattr(factura, 'cuentaporpagar') and factura.cuentaporpagar.pagoemitido_set.exists():
            messages.error(request, 'No se puede anular la compra porque ya existen pagos emitidos asociados.')
            return redirect('compra_detalle', factura_id=factura.id)

        factura.anulada = True
        factura.estado = 'Anulada'
        factura.save()
        
        if hasattr(factura, 'cuentaporpagar'):
            factura.cuentaporpagar.delete()
            
        for detalle in factura.detalles.all():
            if detalle.item.maneja_inventario and detalle.bodega_destino:
                inv_bodega, _ = InventarioBodega.objects.get_or_create(
                    item=detalle.item, 
                    bodega=detalle.bodega_destino,
                    defaults={'cantidad_actual': Decimal('0.00')}
                )
                inv_bodega.cantidad_actual -= detalle.cantidad
                
                stock_despues_restar = inv_bodega.cantidad_actual
                stock_con_compra_erronea = stock_despues_restar + detalle.cantidad
                
                if stock_despues_restar > 0:
                    # Despejar la fórmula del promedio ponderado para hallar el costo anterior
                    costo_reversado = ((stock_con_compra_erronea * detalle.item.costo_promedio) - (detalle.cantidad * detalle.costo_unitario)) / stock_despues_restar
                    detalle.item.costo_promedio = costo_reversado
                    detalle.item.save()
                    
                inv_bodega.save()
                
                MovimientoInventario.objects.create(
                    item=detalle.item,
                    bodega_origen=detalle.bodega_destino,
                    bodega_destino=None,
                    tipo_movimiento='Salida',
                    cantidad=detalle.cantidad,
                    costo_unitario=detalle.costo_unitario,
                    concepto=f"Salida por Anulación Factura {factura.numero_factura_proveedor}",
                    usuario=request.user
                )

        registrar_log(request, 'Anulación', 'Compras', f'Factura {factura.numero_factura_proveedor} anulada. Total: ${factura.total}')
        messages.success(request, f'La compra {factura.numero_factura_proveedor} fue anulada correctamente. Inventario reversado y CxP cancelada.')
        return redirect('compras_lista')
        
    return redirect('compra_detalle', factura_id=factura.id)
