"""Test sertifikasi olustur (self-signed)"""
import os
from datetime import datetime, timedelta
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def sertifika_olustur():
    # Klasor olustur
    os.makedirs("certificates", exist_ok=True)

    # RSA anahtari olustur
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
    )

    # Sertifika bilgileri
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "TR"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Istanbul"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Istanbul"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "AI Uyumluluk Kutusu"),
        x509.NameAttribute(NameOID.COMMON_NAME, "test.aiuyumluluk.com"),
    ])

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.utcnow())
        .not_valid_after(datetime.utcnow() + timedelta(days=365))
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=True,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .sign(key, hashes.SHA256())
    )

    # Private key kaydet
    with open("certificates/test_key.pem", "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ))

    # Certificate kaydet
    with open("certificates/test_cert.pem", "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    print("BASARILI: Sertifika olusturuldu.")
    print("  - certificates/test_key.pem")
    print("  - certificates/test_cert.pem")
    print(f"  - Gecerlilik: 365 gun")
    print(f"  - CN: test.aiuyumluluk.com")


if __name__ == "__main__":
    sertifika_olustur()