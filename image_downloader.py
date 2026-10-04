"""
image_downloader.py - URL'den gorsel indirme modulu
"""

import os
import tempfile
import requests
from urllib.parse import urlparse


def _gecerli_url(url):
    """URL formatini kontrol eder."""
    if not url:
        return False
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


def _uzanti_bul(url, content_type=""):
    """URL veya content-type'tan uzanti bulur."""
    # URL'den uzanti
    path = urlparse(url).path.lower()
    for ext in [".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"]:
        if path.endswith(ext):
            return ext

    # Content-Type'dan uzanti
    ct_map = {
        "image/png": ".png",
        "image/jpeg": ".jpg",
        "image/jpg": ".jpg",
        "image/webp": ".webp",
        "image/gif": ".gif",
        "image/bmp": ".bmp",
    }
    for ct, ext in ct_map.items():
        if ct in content_type.lower():
            return ext

    return ".png"  # varsayilan


def gorsel_url_indir(url, timeout=15, max_size_mb=20):
    """
    URL'den gorsel indirir ve gecici dosyaya kaydeder.

    Args:
        url: Gorsel URL'si
        timeout: HTTP zaman asimi (saniye)
        max_size_mb: Maksimum dosya boyutu (MB)

    Returns:
        dict: {
            "durum": "OK" | "HATA",
            "dosya_yolu": str (gecici dosya),
            "boyut": int (byte),
            "uzanti": str,
            "hata": str (opsiyonel)
        }
    """
    sonuc = {
        "durum": "HATA",
        "dosya_yolu": None,
        "boyut": 0,
        "uzanti": "",
    }

    if not _gecerli_url(url):
        sonuc["hata"] = "Gecersiz URL. http:// veya https:// ile baslamali."
        return sonuc

    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        response = requests.get(url, headers=headers, timeout=timeout, stream=True)
        response.raise_for_status()

        # Content-Type kontrolu
        content_type = response.headers.get("Content-Type", "")
        if not content_type.startswith("image/") and "octet-stream" not in content_type:
            # Bazi sunucular content-type gondermez, uzanti kontrolu yapalim
            uzanti = _uzanti_bul(url, content_type)
            if uzanti not in [".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"]:
                sonuc["hata"] = f"URL bir gorsel degil (Content-Type: {content_type[:40]})"
                return sonuc

        # Boyut kontrolu
        max_bytes = max_size_mb * 1024 * 1024
        boyut = 0
        chunks = []

        for chunk in response.iter_content(chunk_size=8192):
            boyut += len(chunk)
            if boyut > max_bytes:
                sonuc["hata"] = f"Dosya cok buyuk (>{max_size_mb} MB)"
                return sonuc
            chunks.append(chunk)

        # Gecici dosyaya kaydet
        uzanti = _uzanti_bul(url, content_type)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=uzanti)
        for chunk in chunks:
            tmp.write(chunk)
        tmp.close()

        sonuc["durum"] = "OK"
        sonuc["dosya_yolu"] = tmp.name
        sonuc["boyut"] = boyut
        sonuc["uzanti"] = uzanti
        return sonuc

    except requests.exceptions.Timeout:
        sonuc["hata"] = "Zaman asimi. Sunucu yanit vermedi."
        return sonuc
    except requests.exceptions.RequestException as e:
        sonuc["hata"] = f"Baglanti hatasi: {str(e)[:80]}"
        return sonuc
    except Exception as e:
        sonuc["hata"] = f"Beklenmeyen hata: {str(e)[:80]}"
        return sonuc


def gecici_dosya_sil(dosya_yolu):
    """Gecici dosyayi siler."""
    try:
        if dosya_yolu and os.path.exists(dosya_yolu):
            os.unlink(dosya_yolu)
            return True
    except Exception:
        pass
    return False