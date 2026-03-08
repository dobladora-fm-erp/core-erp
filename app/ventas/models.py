from django.db import models
from terceros.models import Tercero
from inventario.models import Item, Bodega

class FacturaVenta(models.Model):
    cliente = models.ForeignKey(Tercero, on_delete=models.PROTECT, limit_choices_to={'es_cliente': True})
    numero_factura = models.CharField(max_length=50, unique=True)
    fecha_emision = models.DateField()
    fecha_vencimiento = models.DateField()
    
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    impuestos = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    ESTADO_CHOICES = [('Borrador', 'Borrador'), ('Confirmada', 'Confirmada'), ('Anulada', 'Anulada')]
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Borrador')
    procesada = models.BooleanField(default=False, editable=False)

    def __str__(self):
        return f"Factura {self.numero_factura} - {self.cliente}"

class DetalleVenta(models.Model):
    factura = models.ForeignKey(FacturaVenta, related_name='detalles', on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    bodega_origen = models.ForeignKey(Bodega, on_delete=models.PROTECT)
    cantidad = models.DecimalField(max_digits=12, decimal_places=4)
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        from decimal import Decimal
        self.subtotal = Decimal(str(self.cantidad)) * Decimal(str(self.precio_unitario))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cantidad} x {self.item.nombre}"
