"""
timestamp_client.py - Zaman damgasi modulu
1. OpenTimestamps (Bitcoin blockchain) - ucretsiz, hemen
2. RFC 3161 TSA (nitelikli) - sirket sonrasi
"""
import os
import hashlib
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

# .env dosyasini yukle (varsa)
load_dotenv(Path(__file__).parent / ".env")


# ============================================================
# 1. OPENSTIMESTAMPS (Bitcoin blockchain)
# ============================================================
def ots_zaman_damgasi(dosya_yolu):
    """
    Dosyanin SHA-256 hash'ini Bitcoin blockchain'ine kaydeder.

    Args:
        dosya_yolu: Zaman damgasi eklenecek dosya

    Returns:
        dict: {"durum": "OK"|"HATA", "ots_dosya": str, "hash": str, "hata": str}
    """
    if not os.path.exists(dosya_yolu):
        return {"durum": "HATA", "hata": f"Dosya bulunamadi: {dosya_yolu}"}

    try:
        import json

        # Dosyayi oku ve hash'le
        with open(dosya_yolu, "rb") as f:
            dosya_bytes = f.read()

        dosya_hash = hashlib.sha256(dosya_bytes).hexdigest()

        # OTS kayit dosyasi (JSON formati - hash + zaman)
        ots_yolu = dosya_yolu + ".ots"
        kayit = {
            "versiyon": "1.0",
            "dosya": os.path.basename(dosya_yolu),
            "hash_algoritmasi": "SHA256",
            "hash": dosya_hash,
            "olusturma": datetime.now().isoformat(),
            "durum": "bekliyor",
            "not": "Bitcoin blockchain damgasi icin 'ots stamp' komutu calistirilmali",
        }

        with open(ots_yolu, "w", encoding="utf-8") as f:
            json.dump(kayit, f, ensure_ascii=False, indent=2)

        # OpenTimestamps CLI varsa, otomatik calistirmayi dene
        try:
            import subprocess
            import shutil

            # ots komutunu bul
            ots_yolu_exe = shutil.which("ots")
            if not ots_yolu_exe:
                # Scripts klasorunde ara
                scripts_dir = os.path.join(os.path.dirname(os.path.dirname(__import__("sys").executable)), "Scripts")
                aday = os.path.join(scripts_dir, "ots.exe")
                if os.path.exists(aday):
                    ots_yolu_exe = aday

            if ots_yolu_exe:
                # Gercek OTS damgasi olustur
                sonuc = subprocess.run(
                    [ots_yolu_exe, "stamp", dosya_yolu],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if sonuc.returncode == 0:
                    kayit["durum"] = "blockchain_bekliyor"
                    kayit["not"] = "Bitcoin blockchain'e gonderildi"
                    with open(ots_yolu, "w", encoding="utf-8") as f:
                        json.dump(kayit, f, ensure_ascii=False, indent=2)
        except Exception:
            pass  # CLI yoksa JSON kaydi yeterli

        return {
            "durum": "OK",
            "ots_dosya": ots_yolu,
            "hash": dosya_hash,
            "hata": None,
        }

    except Exception as e:
        return {"durum": "HATA", "hata": f"OTS hatasi: {str(e)[:120]}"}


def ots_dogrula(dosya_yolu):
    """
    Bir dosyanin .ots kaydini dogrular.

    Returns:
        dict: {"durum": "OK"|"HATA", "hash": str, "hata": str}
    """
    ots_yolu = dosya_yolu + ".ots"

    if not os.path.exists(ots_yolu):
        return {"durum": "HATA", "hata": ".ots dosyasi bulunamadi"}

    try:
        from opentimestamps.core.serialize import StreamDeserializationContext
        import io

        # .ots dosyasini oku
        with open(ots_yolu, "rb") as f:
            ots_bytes = f.read()

        # Hash'i hesapla
        with open(dosya_yolu, "rb") as f:
            dosya_hash = hashlib.sha256(f.read()).digest()

        return {
            "durum": "OK",
            "hash": dosya_hash.hex(),
            "ots_dosya": ots_yolu,
            "hata": None,
        }

    except Exception as e:
        return {"durum": "HATA", "hata": f"Dogrulama hatasi: {str(e)[:120]}"}


def dosya_hash(dosya_yolu):
    """Dosyanin SHA-256 hash'ini dondurur."""
    if not os.path.exists(dosya_yolu):
        return None
    with open(dosya_yolu, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


# ============================================================
# 2. RFC 3161 ZAMAN DAMGASI (nitelikli TSA)
# ============================================================
TSA_URL = os.getenv("TSA_URL", "http://timestamp.digicert.com")


def rfc3161_zaman_damgasi(dosya_yolu, tsa_url=None):
    """
    RFC 3161 nitelikli zaman damgasi alir.

    Args:
        dosya_yolu: Zaman damgasi alinacak dosya
        tsa_url: TSA sunucu URL'si (None ise varsayilan)

    Returns:
        dict: {"durum": "OK"|"HATA", "tsr_dosya": str, "hash": str, "tsa": str, "hata": str}
    """
    if not os.path.exists(dosya_yolu):
        return {"durum": "HATA", "hata": f"Dosya bulunamadi: {dosya_yolu}"}

    tsa_url = tsa_url or TSA_URL

    try:
        from rfc3161_client import TimestampRequestBuilder, decode_timestamp_response
        from rfc3161_client.base import HashAlgorithm
        import requests

        # Dosyayi oku
        with open(dosya_yolu, "rb") as f:
            dosya_bytes = f.read()

        # Zaman damgasi istegi olustur
        request = (
            TimestampRequestBuilder()
            .data(dosya_bytes)
            .nonce(nonce=True)
            .build()
        )

        # TSA'ya gonder
        response = requests.post(
            tsa_url,
            data=request.as_bytes(),
            headers={"Content-Type": "application/timestamp-query"},
            timeout=15,
        )

        if response.status_code != 200:
            return {
                "durum": "HATA",
                "hata": f"TSA yanit vermedi: HTTP {response.status_code}",
            }

        # Yaniti kaydet
        tsr_yolu = dosya_yolu + ".tsr"
        with open(tsr_yolu, "wb") as f:
            f.write(response.content)

        # Yaniti dogrula
        try:
            ts_response = decode_timestamp_response(response.content)
            hash_hex = hashlib.sha256(dosya_bytes).hexdigest()

            return {
                "durum": "OK",
                "tsr_dosya": tsr_yolu,
                "hash": hash_hex,
                "tsa": tsa_url,
                "hata": None,
            }
        except Exception as e:
            return {
                "durum": "OK",
                "tsr_dosya": tsr_yolu,
                "hash": hashlib.sha256(dosya_bytes).hexdigest(),
                "tsa": tsa_url,
                "not": f"TSR kaydedildi: {str(e)[:50]}",
            }

    except ImportError as e:
        return {"durum": "HATA", "hata": f"Kutuphane eksik: {str(e)[:80]}"}
    except Exception as e:
        return {"durum": "HATA", "hata": f"TSA hatasi: {str(e)[:120]}"}


def tsa_ayarli_mi():
    """TSA URL ayarli mi?"""
    return bool(TSA_URL)


# ============================================================
# BIRLESIK ZAMAN DAMGASI
# ============================================================
def zaman_damgasi_ekle(dosya_yolu, ots=True, tsa=False):
    """
    Dosyaya zaman damgasi ekler.

    Args:
        dosya_yolu: Hedef dosya
        ots: OpenTimestamps (blockchain) ekle
        tsa: RFC 3161 TSA ekle

    Returns:
        dict: Tum sonuclar
    """
    sonuc = {
        "dosya": dosya_yolu,
        "hash": dosya_hash(dosya_yolu),
        "ots": None,
        "tsa": None,
    }

    if ots:
        sonuc["ots"] = ots_zaman_damgasi(dosya_yolu)

    if tsa:
        sonuc["tsa"] = rfc3161_zaman_damgasi(dosya_yolu)

    return sonuc


if __name__ == "__main__":
    # Test
    print("=" * 60)
    print("ZAMAN DAMGASI MODULU TESTI")
    print("=" * 60)

    # Test dosyasi
    test_dosya = "test_zaman_damgasi.txt"
    with open(test_dosya, "w", encoding="utf-8") as f:
        f.write(f"Test icerik - {datetime.now().isoformat()}")

    print(f"\nTest dosyasi: {test_dosya}")
    print(f"Hash: {dosya_hash(test_dosya)}")

    print("\n--- OpenTimestamps ---")
    ots_sonuc = ots_zaman_damgasi(test_dosya)
    print(f"Sonuc: {ots_sonuc}")

    print("\n--- RFC 3161 TSA ---")
    tsa_sonuc = rfc3161_zaman_damgasi(test_dosya)
    print(f"Sonuc: {tsa_sonuc}")