from django.db import models
from terceros.models import Tercero
from inventario.models import Item, Bodega
from django.core.exceptions import ValidationError
from core.models import Empresa

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
    anulada = models.BooleanField(default=False)

    # Facturación Electrónica DIAN
    cufe = models.CharField(max_length=150, unique=True, null=True, blank=True, verbose_name="CUFE")
    cadena_qr = models.TextField(null=True, blank=True, verbose_name="Cadena QR")
    xml_dian = models.FileField(upload_to='dian_xmls/', null=True, blank=True, verbose_name="XML DIAN")
    DIAN_ESTADO_CHOICES = [
        ('No Enviada', 'No Enviada'),
        ('Aceptada', 'Aceptada'),
        ('Rechazada', 'Rechazada'),
    ]
    dian_estado = models.CharField(max_length=20, choices=DIAN_ESTADO_CHOICES, default='No Enviada', verbose_name="Estado DIAN")
    dian_fecha_validacion = models.DateTimeField(null=True, blank=True, verbose_name="Fecha Validación DIAN")

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

class ResolucionDIAN(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name="Empresa")
    prefijo = models.CharField(max_length=5, verbose_name="Prefijo")
    numero_inicial = models.IntegerField(verbose_name="Número Inicial")
    numero_final = models.IntegerField(verbose_name="Número Final")
    siguiente_numero = models.IntegerField(verbose_name="Siguiente Número")
    fecha_inicio = models.DateField(verbose_name="Fecha de Inicio")
    fecha_fin = models.DateField(verbose_name="Fecha de Fin")
    activa = models.BooleanField(default=True, verbose_name="Es Activa")

    class Meta:
        verbose_name = "Resolución DIAN"
        verbose_name_plural = "Resoluciones DIAN"

    def clean(self):
        super().clean()
        if self.activa:
            resoluciones_activas = ResolucionDIAN.objects.filter(empresa=self.empresa, activa=True)
            if self.pk:
                resoluciones_activas = resoluciones_activas.exclude(pk=self.pk)
            if resoluciones_activas.exists():
                raise ValidationError("Solo puede haber una resolución activa por empresa.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Resolución {self.prefijo} {self.numero_inicial} a {self.numero_final} ({'Activa' if self.activa else 'Inactiva'})"

class NotaCreditoVenta(models.Model):
    DIAN_ESTADO_CHOICES = [
        ('No Enviada', 'No Enviada'),
        ('Aceptada', 'Aceptada'),
        ('Rechazada', 'Rechazada')
    ]
    factura = models.OneToOneField(FacturaVenta, on_delete=models.PROTECT, verbose_name="Factura")
    numero_nota = models.CharField(max_length=20, unique=True, verbose_name="Número de Nota")
    fecha_emision = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Emisión")
    motivo = models.TextField(verbose_name="Motivo", default="Devolución de mercancía y anulación de factura")
    dian_estado = models.CharField(max_length=20, choices=DIAN_ESTADO_CHOICES, default='No Enviada', verbose_name="Estado DIAN")

    class Meta:
        verbose_name = "Nota Crédito"
        verbose_name_plural = "Notas Crédito"

    def __str__(self):
        return f"{self.numero_nota} (Factura {self.factura.numero_factura})"
