import hashlib
import uuid
from decimal import Decimal

from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from django.utils import timezone

from core.models import Empresa


def generar_xml_factura(factura):
    """
    Genera el XML UBL 2.1 de la factura y lo almacena en factura.xml_dian.
    Retorna el string XML generado.
    """
    detalles = factura.detalles.select_related('item', 'bodega_origen').all()

    # Calcular impuesto por línea para el XML
    detalles_con_impuesto = []
    for detalle in detalles:
        detalle.impuesto_linea = detalle.subtotal * (detalle.item.porcentaje_iva / Decimal('100.00'))
        detalles_con_impuesto.append(detalle)

    # Obtener datos de la empresa emisora
    empresa = Empresa.objects.first()

    context = {
        'factura': factura,
        'detalles': detalles_con_impuesto,
        'empresa': empresa,
        'hora_emision': timezone.now().strftime('%H:%M:%S-05:00'),
    }

    xml_string = render_to_string('ventas/dian_ubl21.xml', context)

    # Guardar en el FileField del modelo
    filename = f"Factura_{factura.numero_factura}_DIAN.xml"
    factura.xml_dian.save(filename, ContentFile(xml_string.encode('utf-8')), save=False)

    return xml_string


def generar_cufe(factura):
    """
    Genera un CUFE simulado usando SHA-384.
    En producción, el CUFE real se compone de:
    NumFac + FecFac + HorFac + ValFac + CodImp1 + ValImp1 + ... + NitOFE + NumAdq + ClTec + TipoAmb
    """
    semilla = f"{factura.id}-{factura.numero_factura}-{factura.total}-{factura.fecha_emision}-{uuid.uuid4().hex}"
    cufe = hashlib.sha384(semilla.encode('utf-8')).hexdigest()
    return cufe


def generar_cadena_qr(factura):
    """
    Genera la cadena QR requerida por la DIAN.
    En producción, esta cadena incluye la URL de validación + CUFE.
    """
    qr_data = (
        f"NumFac: {factura.numero_factura}\n"
        f"FecFac: {factura.fecha_emision}\n"
        f"NitFac: EMPRESA_NIT\n"
        f"DocAdq: {factura.cliente.numero_identificacion}\n"
        f"ValFac: {factura.subtotal}\n"
        f"ValIva: {factura.impuestos}\n"
        f"ValTot: {factura.total}\n"
        f"CUFE: {factura.cufe}\n"
        f"QRCode: https://catalogo-vpfe.dian.gov.co/document/searchqr?documentkey={factura.cufe}"
    )
    return qr_data
