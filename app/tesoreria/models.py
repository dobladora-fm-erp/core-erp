from django.db import models
from django.core.exceptions import ValidationError
from terceros.models import Tercero
from ventas.models import FacturaVenta
from compras.models import FacturaCompra

class CuentaBancaria(models.Model):
    nombre = models.CharField(max_length=100, help_text="Ej: Bancolombia, Caja General")
    tipo = models.CharField(max_length=50, choices=[('Banco', 'Banco'), ('Efectivo', 'Efectivo/Caja')])
    numero_cuenta = models.CharField(max_length=50, null=True, blank=True)
    saldo_actual = models.DecimalField(max_digits=15, decimal_places=2, default=0, editable=False)

    def __str__(self):
        return f"{self.nombre} - Saldo: ${self.saldo_actual}"

class CuentaPorCobrar(models.Model):
    cliente = models.ForeignKey(Tercero, on_delete=models.PROTECT, limit_choices_to={'es_cliente': True})
    factura_origen = models.OneToOneField(FacturaVenta, on_delete=models.PROTECT, help_text="Factura que genera la deuda")
    monto_total = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    saldo_pendiente = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    fecha_vencimiento = models.DateField()
    
    ESTADO_CHOICES = [('Pendiente', 'Pendiente'), ('Pagada', 'Pagada')]
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Pendiente', editable=False)

    def __str__(self):
        return f"CxC - {self.cliente} - Factura {self.factura_origen.numero_factura}"

class CuentaPorPagar(models.Model):
    proveedor = models.ForeignKey(Tercero, on_delete=models.PROTECT, limit_choices_to={'es_proveedor': True})
    factura_origen = models.OneToOneField(FacturaCompra, on_delete=models.PROTECT, help_text="Factura que genera la deuda")
    monto_total = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    saldo_pendiente = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    fecha_vencimiento = models.DateField()
    
    ESTADO_CHOICES = [('Pendiente', 'Pendiente'), ('Pagada', 'Pagada')]
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Pendiente', editable=False)

    def __str__(self):
        return f"CxP - {self.proveedor} - Factura {self.factura_origen.numero_factura_proveedor}"

class PagoRecibido(models.Model):
    cuenta_por_cobrar = models.ForeignKey(CuentaPorCobrar, on_delete=models.PROTECT)
    cuenta_destino = models.ForeignKey(CuentaBancaria, on_delete=models.PROTECT, help_text="A dónde entró la plata")
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_pago = models.DateField(auto_now_add=True)
    referencia = models.CharField(max_length=100, help_text="Ej: Transferencia #12345")

    def __str__(self):
        return f"Pago de ${self.monto} para {self.cuenta_por_cobrar}"

class PagoEmitido(models.Model):
    cuenta_por_pagar = models.ForeignKey(CuentaPorPagar, on_delete=models.PROTECT)
    cuenta_origen = models.ForeignKey(CuentaBancaria, on_delete=models.PROTECT, help_text="De dónde salió la plata")
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_pago = models.DateField(auto_now_add=True)
    referencia = models.CharField(max_length=100, help_text="Ej: Cheque #987")

    def __str__(self):
        return f"Egreso de ${self.monto} para {self.cuenta_por_pagar}"
