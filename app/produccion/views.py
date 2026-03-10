from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
import uuid
from decimal import Decimal
from django.db.models import Sum

from .models import OrdenProduccion, InsumoConsumido, ProductoGenerado
from .forms import OrdenProduccionForm, InsumoFormSet, ProductoFormSet
from inventario.models import InventarioBodega, MovimientoInventario

@login_required
def produccion_lista_view(request):
    ordenes = OrdenProduccion.objects.prefetch_related('insumos__item', 'productos__item').all().order_by('-fecha_creacion')
    return render(request, 'produccion/lista_produccion.html', {'ordenes': ordenes})

@login_required
def produccion_crear_view(request):
    if request.method == 'POST':
        form = OrdenProduccionForm(request.POST)
        insumos_formset = InsumoFormSet(request.POST, prefix='insumos')
        productos_formset = ProductoFormSet(request.POST, prefix='productos')
        
        if form.is_valid() and insumos_formset.is_valid() and productos_formset.is_valid():
            try:
                with transaction.atomic():
                    # Validar Insumos y Productos
                    hay_insumos = any(f.cleaned_data and not f.cleaned_data.get('DELETE', False) for f in insumos_formset.forms)
                    hay_productos = any(f.cleaned_data and not f.cleaned_data.get('DELETE', False) for f in productos_formset.forms)
                    
                    if not hay_insumos or not hay_productos:
                        raise ValueError('Debes declarar al menos un Insumo Consumido (Resta) y un Producto Generado (Suma).')
                    
                    orden = form.save(commit=False)
                    orden.numero_orden = f"PROD-{uuid.uuid4().hex[:6].upper()}"
                    orden.estado = 'Finalizada'
                    orden.procesada = True
                    orden.save()
                    
                    insumos = insumos_formset.save(commit=False)
                    for insumo in insumos:
                        insumo.orden = orden
                        
                        # 1. Rebajar de Bodega Origen
                        inv_bodega = InventarioBodega.objects.select_for_update().filter(
                            item=insumo.item, 
                            bodega=insumo.bodega_origen
                        ).first()
                        
                        if not inv_bodega or inv_bodega.cantidad_actual < insumo.cantidad:
                            disp = inv_bodega.cantidad_actual if inv_bodega else 0
                            raise ValueError(f"Stock insuficiente de materia prima '{insumo.item.nombre}' en la bodega seleccionada. Disp: {disp}")
                            
                        inv_bodega.cantidad_actual -= insumo.cantidad
                        inv_bodega.save()
                        
                        # Movimiento Salida Kardex
                        MovimientoInventario.objects.create(
                            item=insumo.item,
                            bodega_origen=insumo.bodega_origen,
                            tipo_movimiento='Salida',
                            cantidad=insumo.cantidad,
                            costo_unitario=insumo.item.costo_promedio,
                            concepto=f"Consumo en Orden {orden.numero_orden}",
                            usuario=request.user
                        )
                        insumo.save()

                    for insborrado in insumos_formset.deleted_objects:
                        insborrado.delete()

                    productos = productos_formset.save(commit=False)
                    for producto in productos:
                        producto.orden = orden
                        
                        # 2. Aumentar en Bodega Destino
                        inv_bodega_dest, _ = InventarioBodega.objects.select_for_update().get_or_create(
                            item=producto.item, 
                            bodega=producto.bodega_destino,
                            defaults={'cantidad_actual': Decimal('0.00')}
                        )
                        inv_bodega_dest.cantidad_actual += producto.cantidad
                        inv_bodega_dest.save()
                        
                        MovimientoInventario.objects.create(
                            item=producto.item,
                            bodega_destino=producto.bodega_destino,
                            tipo_movimiento='Entrada',
                            cantidad=producto.cantidad,
                            costo_unitario=producto.costo_unitario_asignado,
                            concepto=f"Producción {orden.numero_orden}",
                            usuario=request.user
                        )
                        
                        # Recalcular Costo Promedio del P.T.
                        item_pt = producto.item
                        stock_actual = InventarioBodega.objects.filter(item=item_pt).aggregate(Sum('cantidad_actual'))['cantidad_actual__sum'] or Decimal('0.00')
                        stock_antes = stock_actual - producto.cantidad
                        costo_antes = item_pt.costo_promedio
                        
                        if stock_actual > 0:
                            nuevo_costo = ((stock_antes * costo_antes) + (producto.cantidad * producto.costo_unitario_asignado)) / stock_actual
                            item_pt.costo_promedio = nuevo_costo
                            item_pt.save()
                            
                        producto.save()

                    for ptborrado in productos_formset.deleted_objects:
                        ptborrado.delete()
                    
                    messages.success(request, f'Orden de Producción {orden.numero_orden} procesada exitosamente. Inventario Transmutado.')
                    return redirect('produccion_lista')
            except ValueError as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, f'Error validando la orden: {str(e)}')
    else:
        form = OrdenProduccionForm()
        insumos_formset = InsumoFormSet(prefix='insumos')
        productos_formset = ProductoFormSet(prefix='productos')
        
    return render(request, 'produccion/crear_produccion.html', {
        'form': form, 
        'insumos_formset': insumos_formset,
        'productos_formset': productos_formset
    })

@login_required
def produccion_detalle_view(request, orden_id):
    orden = get_object_or_404(OrdenProduccion, id=orden_id)
    return render(request, 'produccion/detalle_produccion.html', {
        'orden': orden,
        'insumos': orden.insumos.all(),
        'productos': orden.productos.all()
    })
