from django.db import models
from terceros.models import Tercero
from inventario.models import Item, Bodega

class FacturaCompra(models.Model):
    ESTADO_CHOICES = [
        ('Borrador', 'Borrador'),
        ('Confirmada', 'Confirmada'),
        ('Anulada', 'Anulada'),
    ]

    proveedor = models.ForeignKey(
        Tercero, 
        on_delete=models.PROTECT, 
        limit_choices_to={'es_proveedor': True},
        verbose_name="Proveedor"
    )
    numero_factura_proveedor = models.CharField(max_length=50, verbose_name="Número de Factura del Proveedor")
    
    fecha_emision = models.DateField(verbose_name="Fecha de Emisión")
    fecha_vencimiento = models.DateField(verbose_name="Fecha de Vencimiento")

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Subtotal")
    impuestos = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Impuestos")
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Total")

    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Borrador', verbose_name="Estado")
    procesada = models.BooleanField(
        default=False, 
        editable=False, 
        help_text="Indica si la factura ya inyectó el stock al inventario"
    )

    class Meta:
        verbose_name = "Factura de Compra"
        verbose_name_plural = "Facturas de Compra"

    def __str__(self):
        return f"Factura #{self.numero_factura_proveedor} - {self.proveedor.razon_social or self.proveedor.numero_identificacion}"

class DetalleCompra(models.Model):
    factura = models.ForeignKey(FacturaCompra, related_name='detalles', on_delete=models.CASCADE, verbose_name="Factura")
    item = models.ForeignKey(Item, on_delete=models.PROTECT, verbose_name="Ítem")
    bodega_destino = models.ForeignKey(Bodega, on_delete=models.PROTECT, verbose_name="Bodega de Destino")

    cantidad = models.DecimalField(max_digits=12, decimal_places=4, verbose_name="Cantidad")
    costo_unitario = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Costo Unitario")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, editable=False, verbose_name="Subtotal")

    class Meta:
        verbose_name = "Detalle de Compra"
        verbose_name_plural = "Detalles de Compra"

    def save(self, *args, **kwargs):
        # Calcular automáticamente el subtotal multiplicando cantidad por costo_unitario antes de guardar
        if self.cantidad is not None and self.costo_unitario is not None:
            self.subtotal = self.cantidad * self.costo_unitario
        else:
            self.subtotal = 0
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cantidad} x {self.item.nombre} (Factura #{self.factura.numero_factura_proveedor})"
