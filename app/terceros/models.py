from django.db import models
from core.models import Municipio

class Tercero(models.Model):
    TIPO_DOCUMENTO_CHOICES = [
        ('NIT', 'NIT'),
        ('CC', 'Cédula de Ciudadanía'),
        ('CE', 'Cédula de Extranjería'),
        ('Pasaporte', 'Pasaporte'),
    ]

    TIPO_PERSONA_CHOICES = [
        ('Juridica', 'Jurídica'),
        ('Natural', 'Natural'),
    ]

    REGIMEN_IVA_CHOICES = [
        ('Responsable', 'Responsable de IVA'),
        ('No Responsable', 'No Responsable de IVA'),
    ]

    VALIDACION_API_CHOICES = [
        ('Validado', 'Validado'),
        ('Pendiente', 'Pendiente'),
        ('Desactualizado', 'Desactualizado'),
    ]

    # Roles
    es_cliente = models.BooleanField(default=False, verbose_name="Es Cliente")
    es_proveedor = models.BooleanField(default=False, verbose_name="Es Proveedor")
    es_empleado = models.BooleanField(default=False, verbose_name="Es Empleado")

    # Identificación
    tipo_documento = models.CharField(max_length=20, choices=TIPO_DOCUMENTO_CHOICES, verbose_name="Tipo de Documento")
    numero_identificacion = models.CharField(max_length=20, unique=True, verbose_name="Número de Identificación")
    dv = models.CharField(max_length=1, null=True, blank=True, verbose_name="Dígito de Verificación (DV)")
    tipo_persona = models.CharField(max_length=20, choices=TIPO_PERSONA_CHOICES, verbose_name="Tipo de Persona")

    # Nombres
    razon_social = models.CharField(max_length=255, null=True, blank=True, verbose_name="Razón Social")
    nombres = models.CharField(max_length=100, null=True, blank=True, verbose_name="Nombres")
    apellidos = models.CharField(max_length=100, null=True, blank=True, verbose_name="Apellidos")

    # Contacto
    municipio = models.ForeignKey(Municipio, on_delete=models.PROTECT, verbose_name="Municipio")
    direccion = models.CharField(max_length=255, verbose_name="Dirección")
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")
    correo_electronico = models.EmailField(verbose_name="Correo Electrónico")

    # Tributario
    regimen_iva = models.CharField(max_length=30, choices=REGIMEN_IVA_CHOICES, verbose_name="Régimen de IVA")
    responsabilidades_fiscales = models.CharField(
        max_length=100,
        help_text="Ej: O-13, O-47",
        verbose_name="Responsabilidades Fiscales"
    )

    # Control DIAN/API
    datos_completos = models.BooleanField(default=False, verbose_name="Datos Completos")
    validacion_api_estado = models.CharField(
        max_length=30,
        choices=VALIDACION_API_CHOICES,
        default='Pendiente',
        verbose_name="Estado de Validación API"
    )
    fecha_ultima_validacion = models.DateTimeField(null=True, blank=True, verbose_name="Fecha Última Validación")
    requiere_atencion_contador = models.BooleanField(default=False, verbose_name="Requiere Atención Contador")

    def __str__(self):
        if self.razon_social:
            return self.razon_social
        return f"{self.nombres or ''} {self.apellidos or ''}".strip() or self.numero_identificacion
