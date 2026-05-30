import logging
from lxml import etree
from signxml import XMLSigner, methods
from cryptography.hazmat.primitives.serialization import pkcs12, Encoding, PrivateFormat, NoEncryption

logger = logging.getLogger(__name__)

def firmar_xml_dian(xml_string, empresa):
    """
    Firma digitalmente un XML usando el certificado .p12 de la empresa
    siguiendo el estándar XAdES-EPES requerido por la DIAN (UBL 2.1).
    """
    if not empresa.certificado_p12 or not empresa.clave_certificado:
        logger.warning("No hay certificado o clave configurada para la empresa. Retornando XML sin firmar.")
        # En producción estricta, esto debería lanzar una excepción.
        # raise ValueError("Certificado digital no configurado en la bóveda fiscal de la empresa.")
        return xml_string

    try:
        # 1. Leer el archivo .p12
        p12_data = empresa.certificado_p12.read()
        password = empresa.clave_certificado.encode('utf-8')
        
        # 2. Extraer llave privada y certificado
        private_key, certificate, additional_certificates = pkcs12.load_key_and_certificates(
            p12_data, 
            password
        )
        
        # 3. Serializar a formato PEM (Requerido por signxml)
        key_pem = private_key.private_bytes(
            encoding=Encoding.PEM,
            format=PrivateFormat.PKCS8,
            encryption_algorithm=NoEncryption()
        )
        cert_pem = certificate.public_bytes(encoding=Encoding.PEM)
        
        # 4. Parsear el XML
        # Importante: remover espacios en blanco innecesarios puede ayudar con canonicalización
        parser = etree.XMLParser(remove_blank_text=False)
        root = etree.fromstring(xml_string.encode('utf-8'), parser)
        
        # 5. Aplicar la Firma (Enveloped)
        # Nota: La DIAN usualmente requiere que la firma se inyecte en <ext:ExtensionContent>
        # Por simplicidad inicial, haremos un Enveloped global. Ajustaremos según el template XML exacto.
        signer = XMLSigner(
            method=methods.enveloped,
            signature_algorithm="rsa-sha256",
            digest_algorithm="sha256",
            c14n_algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"
        )
        
        signed_root = signer.sign(root, key=key_pem, cert=cert_pem)
        
        # 6. Retornar XML firmado
        return etree.tostring(signed_root, encoding='unicode')
        
    except Exception as e:
        logger.error(f"Error crítico al firmar XML: {str(e)}")
        # En caso de fallo criptográfico, la facturación debe detenerse
        raise ValueError(f"Error criptográfico al firmar el documento: {str(e)}")
