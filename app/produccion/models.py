from django.db import models
from inventario.models import Item, Bodega

class OrdenProduccion(models.Model):
    numero_orden = models.CharField(max_length=50, unique=True, verbose_name="Número de Orden (Lote)")
    fecha_creacion = models.DateField(auto_now_add=True)
    
    ESTADO_CHOICES = [('Borrador', 'Borrador'), ('Finalizada', 'Finalizada (Mueve Inventario)')]
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Borrador')
    procesada = models.BooleanField(default=False, editable=False)
    observaciones = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Orden {self.numero_orden} - {self.estado}"

class InsumoConsumido(models.Model):
    orden = models.ForeignKey(OrdenProduccion, related_name='insumos', on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.PROTECT, help_text="Materia Prima a consumir")
    bodega_origen = models.ForeignKey(Bodega, on_delete=models.PROTECT)
    cantidad = models.DecimalField(max_digits=12, decimal_places=4)

    def __str__(self):
        return f"- {self.cantidad} de {self.item.nombre}"

class ProductoGenerado(models.Model):
    orden = models.ForeignKey(OrdenProduccion, related_name='productos', on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.PROTECT, help_text="Producto Terminado o Retal generado")
    bodega_destino = models.ForeignKey(Bodega, on_delete=models.PROTECT)
    cantidad = models.DecimalField(max_digits=12, decimal_places=4)
    costo_unitario_asignado = models.DecimalField(max_digits=12, decimal_places=2, help_text="Costo estimado por unidad tras la transformación")

    def __str__(self):
        return f"+ {self.cantidad} de {self.item.nombre}"
