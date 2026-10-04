"""
pdf_signer.py - PDF'e dijital imza ve zaman damgasi ekleme
pyhanko kutuphanesi kullanir.
"""
import os
from pathlib import Path
from datetime import datetime


from timestamp_client import ots_zaman_damgasi, rfc3161_zaman_damgasi


SERTIFIKA_KLASOR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "certificates")
SERTIFIKA_YOLU = os.path.join(SERTIFIKA_KLASOR, "test_cert.pem")
ANAHTAR_YOLU = os.path.join(SERTIFIKA_KLASOR, "test_key.pem")


def imza_ayarli_mi():
    """Sertifika dosyalari mevcut mu?"""
    return os.path.exists(SERTIFIKA_YOLU) and os.path.exists(ANAHTAR_YOLU)


def pdf_imzala(girdi_yolu, cikti_yolu=None):
    """
    PDF dosyasini dijital olarak imzalar.

    Args:
        girdi_yolu: Imzalanacak PDF
        cikti_yolu: Imzali PDF (None ise girdinin sonuna _imzali eklenir)

    Returns:
        dict: {"durum": "OK"|"HATA", "dosya": str, "hata": str}
    """
    if not imza_ayarli_mi():
        return {
            "durum": "HATA",
            "hata": "Sertifika bulunamadi. 'py sertifika_olustur.py' calistirin.",
        }

    if not os.path.exists(girdi_yolu):
        return {"durum": "HATA", "hata": f"Dosya bulunamadi: {girdi_yolu}"}

    if cikti_yolu is None:
        base, ext = os.path.splitext(girdi_yolu)
        cikti_yolu = f"{base}_imzali{ext}"

    try:
        from pyhanko.sign import signers
        from pyhanko.sign.fields import SigFieldSpec, append_signature_field
        from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter

        # Sertifikayi yukle
        imzaci = signers.SimpleSigner.load(
            key_file=ANAHTAR_YOLU,
            cert_file=SERTIFIKA_YOLU,
        )

        if imzaci is None:
            return {"durum": "HATA", "hata": "Sertifika yuklenemedi"}

        # PDF'i ac ve imzala
        with open(girdi_yolu, "rb") as f:
            w = IncrementalPdfFileWriter(f)

            # Son sayfa numarasini bul
            try:
                son_sayfa = len(w.root["/Pages"]["/Kids"]) - 1
            except Exception:
                son_sayfa = 0

            # Imza alani ekle (son sayfaya)
            append_signature_field(
                w,
                SigFieldSpec(
                    sig_field_name="Signature1",
                    on_page=son_sayfa,
                    box=(350, 50, 550, 100),
                ),
            )

            # Imzala
            meta = signers.PdfSignatureMetadata(field_name="Signature1")
            signers.sign_pdf(w, meta, signer=imzaci)

            # Dogru kullanim: writer'in kendi write metodu
            with open(cikti_yolu, "wb") as out_f:
                w.write(out_f)

        # Zaman damgasi ekle (imzali PDF'e)
        zaman_sonuc = {
            "ots": None,
            "tsa": None,
        }

        try:
            # OpenTimestamps
            ots = ots_zaman_damgasi(cikti_yolu)
            if ots.get("durum") == "OK":
                zaman_sonuc["ots"] = {
                    "dosya": ots.get("ots_dosya"),
                    "hash": ots.get("hash"),
                }

            # RFC 3161 TSA (hata olsa bile devam et)
            try:
                tsa = rfc3161_zaman_damgasi(cikti_yolu)
                if tsa.get("durum") == "OK":
                    zaman_sonuc["tsa"] = {
                        "dosya": tsa.get("tsr_dosya"),
                        "hash": tsa.get("hash"),
                        "tsa": tsa.get("tsa"),
                    }
            except Exception:
                pass
        except Exception:
            pass

        return {
            "durum": "OK",
            "dosya": cikti_yolu,
            "hata": None,
            "zaman_damgasi": zaman_sonuc,
        }

    except ImportError as e:
        return {"durum": "HATA", "hata": f"Kutuphane eksik: {str(e)[:80]}"}
    except Exception as e:
        return {"durum": "HATA", "hata": f"Imzalama hatasi: {str(e)[:120]}"}


def imza_bilgisi():
    """Sertifika bilgilerini dondurur."""
    if not imza_ayarli_mi():
        return {"durum": "YOK", "hata": "Sertifika bulunamadi"}

    try:
        from cryptography import x509
        from cryptography.hazmat.backends import default_backend

        with open(SERTIFIKA_YOLU, "rb") as f:
            cert = x509.load_pem_x509_certificate(f.read(), default_backend())

        return {
            "durum": "OK",
            "subject": cert.subject.rfc4514_string(),
            "issuer": cert.issuer.rfc4514_string(),
            "not_before": cert.not_valid_before_utc.strftime("%Y-%m-%d"),
            "not_after": cert.not_valid_after_utc.strftime("%Y-%m-%d"),
            "serial": hex(cert.serial_number),
        }
    except Exception as e:
        return {"durum": "HATA", "hata": str(e)[:100]}


if __name__ == "__main__":
    # Test
    print("=== IMZA MODULU TESTI ===")
    print(f"Imza ayarli mi?: {imza_ayarli_mi()}")
    print()
    print("Sertifika bilgisi:")
    bilgi = imza_bilgisi()
    for k, v in bilgi.items():
        print(f"  {k}: {v}")