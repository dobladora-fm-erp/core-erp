from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import FacturaVenta, DetalleVenta
from .forms import FacturaVentaForm, DetalleVentaFormSet
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum
from decimal import Decimal
from django.utils import timezone
import uuid
from inventario.models import InventarioBodega, MovimientoInventario

@login_required
def ventas_lista_view(request):
    facturas = FacturaVenta.objects.select_related('cliente').all().order_by('-fecha_emision')
    return render(request, 'ventas/lista_ventas.html', {'facturas': facturas})

@login_required
def venta_crear_view(request):
    if request.method == 'POST':
        form = FacturaVentaForm(request.POST)
        formset = DetalleVentaFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    valido = False
                    for f in formset.forms:
                        if f.cleaned_data and not f.cleaned_data.get('DELETE', False):
                            valido = True
                            break
                            
                    if not valido:
                        messages.error(request, 'Debes agregar al menos un ítem a la factura de venta.')
                        return render(request, 'ventas/crear_venta.html', {'form': form, 'formset': formset})

                    factura = form.save(commit=False)
                    factura.numero_factura = f"VEN-{uuid.uuid4().hex[:6].upper()}"  # Genera ID definitivo
                    factura.fecha_emision = timezone.now().date()
                    factura.estado = 'Confirmada'
                    factura.subtotal = Decimal('0.00')
                    factura.impuestos = Decimal('0.00')
                    factura.total = Decimal('0.00')
                    factura.save()
                    
                    detalles = formset.save(commit=False)
                    subtotal_factura = Decimal('0.00')
                    
                    for detalle in detalles:
                        detalle.factura = factura
                        detalle.subtotal = detalle.cantidad * detalle.precio_unitario
                        
                        # Validar Stock y descontar Kardex
                        if detalle.item.maneja_inventario:
                            inv_bodega = InventarioBodega.objects.select_for_update().filter(
                                item=detalle.item, 
                                bodega=detalle.bodega_origen
                            ).first()
                            
                            if not inv_bodega or inv_bodega.cantidad_actual < detalle.cantidad:
                                disp = inv_bodega.cantidad_actual if inv_bodega else 0
                                raise ValueError(f"Stock insuficiente de {detalle.item.nombre} en la bodega seleccionada. (Disponible: {disp})")
                            
                            inv_bodega.cantidad_actual -= detalle.cantidad
                            inv_bodega.save()
                            
                            MovimientoInventario.objects.create(
                                item=detalle.item,
                                bodega_origen=detalle.bodega_origen,
                                tipo_movimiento='Salida',
                                cantidad=detalle.cantidad,
                                costo_unitario=detalle.item.costo_promedio, # Se cruza el costo promedio real de inventario y NO el precio de venta para balance de KARDEX
                                concepto=f"Factura Venta {factura.numero_factura}",
                                usuario=request.user
                            )
                        
                        detalle.save()
                        subtotal_factura += detalle.subtotal

                    for detalle_borrado in formset.deleted_objects:
                        detalle_borrado.delete()
                    
                    factura.subtotal = subtotal_factura
                    factura.impuestos = factura.subtotal * Decimal('0.19') # IVA 19%
                    factura.total = factura.subtotal + factura.impuestos
                    factura.save()

                    messages.success(request, f'Factura {factura.numero_factura} registrada. Stock descontado y cuenta por cobrar generada exitosamente.')
                    return redirect('ventas_lista')
            except ValueError as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, f'Error validando la venta: {str(e)}')
    else:
        form = FacturaVentaForm()
        formset = DetalleVentaFormSet()
    
    return render(request, 'ventas/crear_venta.html', {'form': form, 'formset': formset})

@login_required
def venta_detalle_view(request, factura_id):
    factura = get_object_or_404(FacturaVenta, id=factura_id)
    detalles = factura.detalles.all()

    return render(request, 'ventas/detalle_venta.html', {
        'factura': factura,
        'detalles': detalles
    })

@login_required
@transaction.atomic
def anular_venta_view(request, factura_id):
    factura = get_object_or_404(FacturaVenta, id=factura_id)
    
    if request.method == 'POST':
        if factura.anulada:
            messages.error(request, 'La factura ya ha sido anulada previamente.')
            return redirect('venta_detalle', factura_id=factura.id)
            
        # Revisar si hay CuentaPorCobrar con PagosRecibidos
        if hasattr(factura, 'cuentaporcobrar') and factura.cuentaporcobrar.pagorecibido_set.exists():
            messages.error(request, 'No se puede anular la factura porque ya existen pagos registrados (dinero en banco).')
            return redirect('venta_detalle', factura_id=factura.id)

        # 1. Marcar como anulada
        factura.anulada = True
        factura.estado = 'Anulada'
        factura.save()
        
        # 2. Eliminar la CuentaPorCobrar
        if hasattr(factura, 'cuentaporcobrar'):
            factura.cuentaporcobrar.delete()
            
        # 3. Devolver inventario y generar movimientos
        for detalle in factura.detalles.all():
            # Restaurar stock
            inv_bodega, _ = InventarioBodega.objects.get_or_create(
                item=detalle.item, 
                bodega=detalle.bodega_origen,
                defaults={'cantidad_actual': 0}
            )
            inv_bodega.cantidad_actual += detalle.cantidad
            inv_bodega.save()
            
            # Movimiento KARDEX de anulación
            MovimientoInventario.objects.create(
                item=detalle.item,
                bodega_origen=None,
                bodega_destino=detalle.bodega_origen,
                tipo_movimiento='Entrada',
                cantidad=detalle.cantidad,
                costo_unitario=detalle.item.costo_promedio,
                concepto=f"Entrada por Anulación Factura {factura.numero_factura}",
                usuario=request.user
            )

        messages.success(request, f'La factura {factura.numero_factura} fue anulada correctamente. Inventario devuelto y cartera cancelada.')
        return redirect('ventas_lista')
        
    return redirect('venta_detalle', factura_id=factura.id)
