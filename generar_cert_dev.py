import datetime
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography import x509
from cryptography.x509.oid import NameOID

def generar_certificado():
    # 1. Generate Private Key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # 2. Generate Certificate
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"CO"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Antioquia"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"Medellín"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Dobladora FM Pruebas"),
        x509.NameAttribute(NameOID.COMMON_NAME, u"dobladora-fm-pruebas.com"),
    ])

    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.utcnow()
    ).not_valid_after(
        # Valid for 1 year
        datetime.datetime.utcnow() + datetime.timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([x509.DNSName(u"localhost")]),
        critical=False,
    ).sign(private_key, hashes.SHA256())

    # 3. Export to PKCS12 (.p12)
    p12_data = pkcs12.serialize_key_and_certificates(
        name=b"dobladora_fm",
        key=private_key,
        cert=cert,
        cas=None,
        encryption_algorithm=serialization.BestAvailableEncryption(b"12345")
    )

    # 4. Save to file
    with open("certificado_dev.p12", "wb") as f:
        f.write(p12_data)

    print("Certificado de desarrollo 'certificado_dev.p12' generado con éxito (Contraseña: 12345).")

if __name__ == "__main__":
    generar_certificado()
