from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from ventas.models import FacturaVenta
from compras.models import FacturaCompra
from .models import CuentaPorCobrar, CuentaPorPagar, PagoRecibido, PagoEmitido

@receiver(post_save, sender=FacturaVenta)
def crear_cxc_automatica(sender, instance, created, **kwargs):
    # Si la factura de venta se confirma, nace automáticamente la Cuenta por Cobrar
    if instance.estado == 'Confirmada':
        CuentaPorCobrar.objects.get_or_create(
            factura_origen=instance,
            defaults={
                'cliente': instance.cliente,
                'monto_total': instance.total,
                'saldo_pendiente': instance.total,
                'fecha_vencimiento': instance.fecha_vencimiento,
                'estado': 'Pendiente'
            }
        )

@receiver(post_save, sender=FacturaCompra)
def crear_cxp_automatica(sender, instance, created, **kwargs):
    # Si la factura de compra se confirma, nace automáticamente la Cuenta por Pagar
    if instance.estado == 'Confirmada':
        CuentaPorPagar.objects.get_or_create(
            factura_origen=instance,
            defaults={
                'proveedor': instance.proveedor,
                'monto_total': instance.total,
                'saldo_pendiente': instance.total,
                'fecha_vencimiento': instance.fecha_vencimiento,
                'estado': 'Pendiente'
            }
        )

@receiver(post_save, sender=PagoRecibido)
def procesar_pago_recibido(sender, instance, created, **kwargs):
    if created:
        with transaction.atomic():
            # 1. Bajar saldo a la deuda
            cxc = instance.cuenta_por_cobrar
            cxc.saldo_pendiente -= instance.monto
            if cxc.saldo_pendiente <= 0:
                cxc.estado = 'Pagada'
            cxc.save(update_fields=['saldo_pendiente', 'estado'])
            
            # 2. Subir plata al banco
            banco = instance.cuenta_destino
            banco.saldo_actual += instance.monto
            banco.save(update_fields=['saldo_actual'])

@receiver(post_save, sender=PagoEmitido)
def procesar_pago_emitido(sender, instance, created, **kwargs):
    if created:
        with transaction.atomic():
            # 1. Bajar saldo a la deuda
            cxp = instance.cuenta_por_pagar
            cxp.saldo_pendiente -= instance.monto
            if cxp.saldo_pendiente <= 0:
                cxp.estado = 'Pagada'
            cxp.save(update_fields=['saldo_pendiente', 'estado'])
            
            # 2. Restar plata del banco
            banco = instance.cuenta_origen
            banco.saldo_actual -= instance.monto
            banco.save(update_fields=['saldo_actual'])
