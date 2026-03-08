from django.db import models
from django.contrib.auth.models import User

class UnidadMedida(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre", help_text="Ej: Kilogramo")
    abreviatura = models.CharField(max_length=20, verbose_name="Abreviatura", help_text="Ej: kg")

    def __str__(self):
        return f"{self.nombre} ({self.abreviatura})"

class CategoriaItem(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre de la Categoría")
    descripcion = models.TextField(null=True, blank=True, verbose_name="Descripción")

    def __str__(self):
        return self.nombre

class Item(models.Model):
    TIPO_ITEM_CHOICES = [
        ('Almacenable', 'Almacenable (Producto/Materia Prima)'),
        ('Consumible', 'Consumible (Insumo Menor)'),
        ('Servicio', 'Servicio (Intangible)'),
        ('Retal', 'Retal (Subproducto de Corte)'),
    ]

    # Identificación
    codigo_sku = models.CharField(max_length=50, unique=True, verbose_name="Código SKU")
    nombre = models.CharField(max_length=255, verbose_name="Nombre del Ítem")
    codigo_barras = models.CharField(max_length=100, null=True, blank=True, verbose_name="Código de Barras")

    # Tipología
    tipo_item = models.CharField(max_length=30, choices=TIPO_ITEM_CHOICES, verbose_name="Tipo de Ítem")

    # Relaciones
    categoria = models.ForeignKey(CategoriaItem, on_delete=models.PROTECT, verbose_name="Categoría")
    unidad_medida_base = models.ForeignKey(
        UnidadMedida, 
        on_delete=models.PROTECT, 
        help_text="La unidad mínima en la que se controla el stock",
        verbose_name="Unidad de Medida Base"
    )

    # Finanzas y Control
    precio_base = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Precio Base")
    costo_promedio = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Costo Promedio")
    porcentaje_iva = models.DecimalField(max_digits=5, decimal_places=2, default=19.00, verbose_name="Porcentaje de IVA (%)")
    maneja_inventario = models.BooleanField(default=True, verbose_name="Maneja Inventario")

    def __str__(self):
        return f"[{self.codigo_sku}] {self.nombre}"

class ConversionUnidad(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='conversiones', verbose_name="Ítem")
    unidad_alternativa = models.ForeignKey(UnidadMedida, on_delete=models.PROTECT, verbose_name="Unidad Alternativa")
    factor_multiplicador = models.DecimalField(
        max_digits=10, 
        decimal_places=4, 
        help_text="Ej: Si la unidad base es Kg y la alternativa es Tonelada, el factor es 1000",
        verbose_name="Factor Multiplicador"
    )

    def __str__(self):
        return f"1 {self.unidad_alternativa.abreviatura} = {self.factor_multiplicador} {self.item.unidad_medida_base.abreviatura}(s) de {self.item.nombre}"

class Bodega(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    direccion = models.CharField(max_length=255, null=True, blank=True, verbose_name="Dirección")
    es_activa = models.BooleanField(default=True, verbose_name="Es Activa")

    def __str__(self):
        return self.nombre

class InventarioBodega(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, verbose_name="Ítem")
    bodega = models.ForeignKey(Bodega, on_delete=models.CASCADE, verbose_name="Bodega")
    cantidad_actual = models.DecimalField(max_digits=12, decimal_places=4, default=0, verbose_name="Cantidad Actual")

    class Meta:
        unique_together = ('item', 'bodega')
        verbose_name = "Inventario por Bodega"
        verbose_name_plural = "Inventarios por Bodega"

    def __str__(self):
        return f"{self.item.nombre} en {self.bodega.nombre}: {self.cantidad_actual}"

class MovimientoInventario(models.Model):
    TIPO_MOVIMIENTO_CHOICES = [
        ('Entrada', 'Entrada (Compra/Devolución)'),
        ('Salida', 'Salida (Venta/Merma)'),
        ('Traslado', 'Traslado entre Bodegas'),
        ('Ajuste', 'Ajuste de Inventario'),
    ]

    item = models.ForeignKey(Item, on_delete=models.PROTECT, verbose_name="Ítem")
    bodega_origen = models.ForeignKey(
        Bodega, 
        related_name='movimientos_salida', 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True,
        verbose_name="Bodega Origen"
    )
    bodega_destino = models.ForeignKey(
        Bodega, 
        related_name='movimientos_entrada', 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True,
        verbose_name="Bodega Destino"
    )
    usuario = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Usuario")

    tipo_movimiento = models.CharField(max_length=20, choices=TIPO_MOVIMIENTO_CHOICES, verbose_name="Tipo de Movimiento")
    cantidad = models.DecimalField(max_digits=12, decimal_places=4, verbose_name="Cantidad")
    costo_unitario = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        help_text="Costo al momento del movimiento",
        verbose_name="Costo Unitario"
    )

    fecha_movimiento = models.DateTimeField(auto_now_add=True, verbose_name="Fecha del Movimiento")
    concepto = models.CharField(
        max_length=255, 
        help_text="Ej: Factura de Compra #123, Ajuste por gotera",
        verbose_name="Concepto"
    )

    class Meta:
        verbose_name = "Movimiento de Inventario (Kardex)"
        verbose_name_plural = "Movimientos de Inventario (Kardex)"

    def __str__(self):
        return f"{self.tipo_movimiento} - {self.item.nombre} ({self.cantidad}) el {self.fecha_movimiento.strftime('%Y-%m-%d %H:%M')}"

