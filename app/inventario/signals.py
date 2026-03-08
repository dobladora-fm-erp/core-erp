from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import MovimientoInventario, InventarioBodega

@receiver(post_save, sender=MovimientoInventario)
def actualizar_stock_bodega(sender, instance, created, **kwargs):
    if created:
        with transaction.atomic():
            tipo = instance.tipo_movimiento
            cantidad = instance.cantidad
            item = instance.item

            if tipo in ['Entrada', 'Ajuste'] and cantidad > 0:
                if instance.bodega_destino:
                    inventario_dest, _ = InventarioBodega.objects.get_or_create(
                        item=item,
                        bodega=instance.bodega_destino
                    )
                    inventario_dest.cantidad_actual += cantidad
                    inventario_dest.save()

            elif tipo == 'Salida':
                if instance.bodega_origen:
                    inventario_orig, _ = InventarioBodega.objects.get_or_create(
                        item=item,
                        bodega=instance.bodega_origen
                    )
                    inventario_orig.cantidad_actual -= cantidad
                    inventario_orig.save()

            elif tipo == 'Traslado':
                if instance.bodega_origen and instance.bodega_destino:
                    # Restar de origen
                    inventario_orig, _ = InventarioBodega.objects.get_or_create(
                        item=item,
                        bodega=instance.bodega_origen
                    )
                    inventario_orig.cantidad_actual -= cantidad
                    inventario_orig.save()

                    # Sumar a destino
                    inventario_dest, _ = InventarioBodega.objects.get_or_create(
                        item=item,
                        bodega=instance.bodega_destino
                    )
                    inventario_dest.cantidad_actual += cantidad
                    inventario_dest.save()
