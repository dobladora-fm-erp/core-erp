from django.db import models

class Departamento(models.Model):
    codigo_dane = models.CharField(max_length=10, unique=True, verbose_name="Código DANE")
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Departamento")

    def __str__(self):
        return f"{self.codigo_dane} - {self.nombre}"

class Municipio(models.Model):
    codigo_dane = models.CharField(max_length=10, unique=True, verbose_name="Código DANE")
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Municipio")
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE, verbose_name="Departamento")

    def __str__(self):
        return f"{self.nombre} ({self.departamento.nombre})"

class ActividadCIIU(models.Model):
    codigo = models.CharField(max_length=10, unique=True, verbose_name="Código CIIU")
    descripcion = models.CharField(max_length=255, verbose_name="Descripción")

    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"

class Empresa(models.Model):
    TIPO_PERSONA_CHOICES = [
        ('Juridica', 'Jurídica'),
        ('Natural', 'Natural'),
    ]
    REGIMEN_IVA_CHOICES = [
        ('Responsable', 'Responsable de IVA'),
        ('No Responsable', 'No Responsable de IVA'),
    ]

    razon_social = models.CharField(max_length=255, verbose_name="Razón Social")
    nit = models.CharField(max_length=20, unique=True, verbose_name="NIT")
    dv = models.CharField(max_length=1, verbose_name="DV")
    tipo_persona = models.CharField(max_length=20, choices=TIPO_PERSONA_CHOICES, verbose_name="Tipo de Persona")
    regimen_iva = models.CharField(max_length=30, choices=REGIMEN_IVA_CHOICES, verbose_name="Régimen de IVA")
    responsabilidades_fiscales = models.CharField(
        max_length=100, 
        help_text="Ej: O-13, O-47", 
        verbose_name="Responsabilidades Fiscales"
    )
    direccion = models.CharField(max_length=255, verbose_name="Dirección")
    telefono = models.CharField(max_length=50, verbose_name="Teléfono")
    correo_facturacion = models.EmailField(verbose_name="Correo de Facturación")
    correo_emision = models.EmailField(null=True, blank=True, verbose_name="Correo Emisión (SMTP)")
    smtp_password = models.CharField(max_length=128, null=True, blank=True, verbose_name="Contraseña SMTP")
    logo = models.ImageField(upload_to='logos/', null=True, blank=True, verbose_name="Logo")
    
    # Bóveda Fiscal DIAN
    certificado_p12 = models.FileField(upload_to='certificados_dian/', null=True, blank=True, help_text="Certificado digital en formato .p12 o .pfx")
    clave_certificado = models.CharField(max_length=128, null=True, blank=True)
    software_id_dian = models.CharField(max_length=100, null=True, blank=True, help_text="ID del Software Propio en la DIAN")
    test_set_id_dian = models.CharField(max_length=100, null=True, blank=True, help_text="ID del Set de Pruebas de habilitación")

    municipio = models.ForeignKey(Municipio, on_delete=models.PROTECT, verbose_name="Municipio")
    ciiu_principal = models.ForeignKey(ActividadCIIU, on_delete=models.PROTECT, verbose_name="Actividad CIIU Principal")

    def __str__(self):
        return f"{self.razon_social} (NIT: {self.nit}-{self.dv})"
