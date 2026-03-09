from django.db.models.signals import post_save
from django.dispatch import receiver
from ventas.models import FacturaVenta
from compras.models import FacturaCompra
from .models import CuentaPorCobrar, CuentaPorPagar

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
