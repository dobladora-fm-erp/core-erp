from django.db import models
from django.contrib.auth.models import User


class LogAuditoria(models.Model):
    ACCION_CHOICES = [
        ('Anulación', 'Anulación'),
        ('Creación', 'Creación'),
        ('Modificación', 'Modificación'),
        ('Pago', 'Pago'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Usuario")
    accion = models.CharField(max_length=30, choices=ACCION_CHOICES, verbose_name="Acción")
    modulo = models.CharField(max_length=50, verbose_name="Módulo")
    detalle = models.TextField(verbose_name="Detalle de la Operación")
    direccion_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name="Dirección IP")
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y Hora")

    class Meta:
        verbose_name = "Log de Auditoría"
        verbose_name_plural = "Logs de Auditoría"
        ordering = ['-fecha']

    def __str__(self):
        return f"[{self.fecha.strftime('%Y-%m-%d %H:%M')}] {self.accion} en {self.modulo} por {self.usuario.username}"


def registrar_log(request, accion, modulo, detalle):
    """Helper para registrar un evento de auditoría desde cualquier vista."""
    ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', '0.0.0.0'))
    if ',' in ip:
        ip = ip.split(',')[0].strip()
    LogAuditoria.objects.create(
        usuario=request.user,
        accion=accion,
        modulo=modulo,
        detalle=detalle,
        direccion_ip=ip
    )
