from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, FileResponse, Http404
from .utils import render_to_pdf
from django.contrib.auth.decorators import login_required
from .models import FacturaVenta, DetalleVenta, ResolucionDIAN, NotaCreditoVenta
from .forms import FacturaVentaForm, DetalleVentaFormSet
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.db.models import Sum
from decimal import Decimal
from django.utils import timezone
import uuid
from inventario.models import InventarioBodega, MovimientoInventario
from core.audit import registrar_log

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
                    
                    # 1. Obtener y actualizar resolución DIAN
                    resolucion = ResolucionDIAN.objects.select_for_update().filter(activa=True).first()
                    if not resolucion:
                        raise ValueError("No hay una Resolución DIAN activa configurada en el sistema. Contacte al administrador.")
                    if resolucion.siguiente_numero > resolucion.numero_final:
                        raise ValueError("La Resolución DIAN actual ha superado el número final permitido.")
                        
                    factura.numero_factura = f"{resolucion.prefijo}-{resolucion.siguiente_numero}"
                    resolucion.siguiente_numero += 1
                    resolucion.save()
                    
                    factura.fecha_emision = timezone.now().date()
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
                                costo_unitario=detalle.item.costo_promedio,
                                concepto=f"Factura Venta {factura.numero_factura}",
                                usuario=request.user
                            )
                        
                        detalle.save()
                        subtotal_factura += detalle.subtotal
                        
                        impuesto_linea = detalle.subtotal * (detalle.item.porcentaje_iva / Decimal('100.00'))
                        total_impuestos += impuesto_linea

                    for detalle_borrado in formset.deleted_objects:
                        detalle_borrado.delete()
                    
                    factura.subtotal = subtotal_factura
                    factura.impuestos = total_impuestos
                    factura.total = factura.subtotal + factura.impuestos
                    factura.save()

                    messages.success(request, f'Factura {factura.numero_factura} registrada. Stock descontado y cuenta por cobrar generada exitosamente.')
                    registrar_log(request, 'Creación', 'Ventas', f'Factura {factura.numero_factura} creada por ${factura.total}')
                    return redirect('ventas_lista')
            except ValueError as e:
                messages.error(request, str(e))
            except IntegrityError:
                messages.error(request, 'Error de concurrencia o stock insuficiente detectado en la base de datos.')
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
    tiene_nota_credito = hasattr(factura, 'notacreditoventa')

    return render(request, 'ventas/detalle_venta.html', {
        'factura': factura,
        'detalles': detalles,
        'tiene_nota_credito': tiene_nota_credito
    })

@login_required
@transaction.atomic
def anular_venta_view(request, factura_id):
    factura = get_object_or_404(FacturaVenta, id=factura_id)
    
    if request.method == 'POST':
        if factura.anulada:
            messages.error(request, 'La factura ya ha sido anulada previamente.')
            return redirect('venta_detalle', factura_id=factura.id)

        if factura.dian_estado == 'Aceptada':
            messages.error(request, 'ERROR FISCAL: Esta factura ya fue transmitida y aceptada por la DIAN. No puede ser anulada internamente. Debe emitir una Nota Crédito.')
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
            
        # 3. Devolver inventario y generar movimientos (solo ítems tangibles)
        for detalle in factura.detalles.all():
            if detalle.item.maneja_inventario:
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

        registrar_log(request, 'Anulación', 'Ventas', f'Factura {factura.numero_factura} anulada. Total: ${factura.total}')
        messages.success(request, f'La factura {factura.numero_factura} fue anulada correctamente. Inventario devuelto y cartera cancelada.')
        return redirect('ventas_lista')
        
    return redirect('venta_detalle', factura_id=factura.id)

@login_required
@transaction.atomic
def nota_credito_crear_view(request, factura_id):
    factura = get_object_or_404(FacturaVenta, id=factura_id)
    
    if request.method == 'POST':
        if factura.dian_estado != 'Aceptada':
            messages.error(request, 'Solo se pueden generar notas crédito para facturas aceptadas por la DIAN.')
            return redirect('venta_detalle', factura_id=factura.id)
            
        if hasattr(factura, 'notacreditoventa'):
            messages.error(request, 'Esta factura ya tiene una nota crédito generada.')
            return redirect('venta_detalle', factura_id=factura.id)
            
        # 1. Marcar estado interno y deuda
        factura.estado = 'Anulada'
        factura.anulada = True
        factura.save()
        
        if hasattr(factura, 'cuentaporcobrar'):
            # Lógica financiera
            factura.cuentaporcobrar.saldo_pendiente = Decimal('0.00')
            factura.cuentaporcobrar.estado = 'Pagada'
            factura.cuentaporcobrar.save()
            
        # 2. Devolver inventario y generar movimientos (solo ítems tangibles)
        for detalle in factura.detalles.all():
            if detalle.item.maneja_inventario:
                inv_bodega, _ = InventarioBodega.objects.get_or_create(
                    item=detalle.item, 
                    bodega=detalle.bodega_origen,
                    defaults={'cantidad_actual': 0}
                )
                inv_bodega.cantidad_actual += detalle.cantidad
                inv_bodega.save()
                
                MovimientoInventario.objects.create(
                    item=detalle.item,
                    bodega_destino=detalle.bodega_origen,
                    usuario=request.user,
                    tipo_movimiento='Entrada',
                    cantidad=detalle.cantidad,
                    costo_unitario=detalle.item.costo_promedio,
                    concepto=f'Devolución por Nota Crédito a Factura {factura.numero_factura}'
                )
                
        # 3. Guardar registro de la Nota Crédito
        # Simulamos un número de nota (en un ERP real, habría una ResolucionDIAN para NC)
        numero_nc = f"NC-{uuid.uuid4().hex[:6].upper()}"
        
        NotaCreditoVenta.objects.create(
            factura=factura,
            numero_nota=numero_nc,
            motivo="Devolución de mercancía y anulación de factura",
            dian_estado='Aceptada'
        )
        
        registrar_log(request.user, "Ventas", f"Generada Nota Crédito {numero_nc} para la Factura {factura.numero_factura}")
        messages.success(request, f'Nota Crédito {numero_nc} generada correctamente. El inventario ha sido reintegrado y la cartera cancelada.')
        
    return redirect('venta_detalle', factura_id=factura.id)

@login_required
def venta_pdf_view(request, factura_id):
    factura = get_object_or_404(FacturaVenta, id=factura_id)
    detalles = factura.detalles.all()
    
    context = {
        'factura': factura,
        'detalles': detalles,
    }
    
    pdf = render_to_pdf('ventas/factura_pdf.html', context)
    if pdf:
        response = pdf
        filename = f"Factura_FM_{factura.numero_factura}.pdf"
        content = f"inline; filename={filename}"
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Error Rendering PDF", status=400)


@login_required
@transaction.atomic
def emitir_factura_dian_view(request, factura_id):
    from .dian_service import generar_xml_factura, generar_cufe, generar_cadena_qr

    factura = get_object_or_404(FacturaVenta, id=factura_id)

    if request.method == 'POST':
        # Validaciones previas
        if factura.anulada:
            messages.error(request, 'No se puede emitir una factura anulada a la DIAN.')
            return redirect('venta_detalle', factura_id=factura.id)

        if factura.dian_estado != 'No Enviada':
            messages.error(request, f'Esta factura ya fue procesada por la DIAN. Estado actual: {factura.dian_estado}')
            return redirect('venta_detalle', factura_id=factura.id)

        try:
            # 1. Generar CUFE (SHA-384)
            factura.cufe = generar_cufe(factura)

            # 2. Generar XML UBL 2.1
            generar_xml_factura(factura)

            # 3. Generar cadena QR
            factura.cadena_qr = generar_cadena_qr(factura)

            # 4. Marcar como aceptada
            factura.dian_estado = 'Aceptada'
            factura.dian_fecha_validacion = timezone.now()
            factura.save()

            registrar_log(request, 'Creación', 'Ventas', f'Factura {factura.numero_factura} emitida a la DIAN. CUFE: {factura.cufe[:20]}...')
            messages.success(request, f'✅ Factura {factura.numero_factura} emitida exitosamente a la DIAN. CUFE generado y XML almacenado.')
        except Exception as e:
            messages.error(request, f'Error al emitir factura a la DIAN: {str(e)}')

    return redirect('venta_detalle', factura_id=factura.id)


@login_required
def descargar_xml_dian_view(request, factura_id):
    factura = get_object_or_404(FacturaVenta, id=factura_id)
    if not factura.xml_dian or not factura.xml_dian.storage.exists(factura.xml_dian.name):
        raise Http404("El archivo XML no se encuentra en el servidor.")
    
    response = FileResponse(factura.xml_dian.open('rb'), content_type='application/xml')
    response['Content-Disposition'] = f'attachment; filename="Factura_{factura.numero_factura}_DIAN.xml"'
    return response
