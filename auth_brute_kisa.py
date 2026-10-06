"""auth.py'ye brute force kilit kontrolu ekler."""
import shutil
from pathlib import Path
from datetime import datetime

KOK = Path(".")
HEDEF = KOK / "auth.py"

icerik = HEDEF.read_text(encoding="utf-8")

if "giris_kilitli_mi" in icerik:
    print("[i] Zaten eklenmis.")
    raise SystemExit(0)

zaman = datetime.now().strftime("%Y%m%d_%H%M%S")
yedek = KOK / f"auth_brute_oncesi_{zaman}.py.bak"
shutil.copy2(HEDEF, yedek)
print(f"[+] Yedek: {yedek.name}")

eski = "def giris_yap(kullanici_adi, sifre):"

if eski not in icerik:
    print("[!] giris_yap bulunamadi.")
    raise SystemExit(1)

yeni = '''def giris_yap(kullanici_adi, sifre):
    # BRUTE FORCE KILIT KONTROLU
    _kilit = db.giris_kilitli_mi(kullanici_adi)
    if _kilit.get("kilitli"):
        _kalan = _kilit.get("kalan_dk", 0)
        return {
            "durum": "HATA",
            "hata": f"Hesabiniz gecici olarak kilitli. {_kalan} dakika sonra tekrar deneyin.",
            "kod": "KILITLI",
            "kalan_dk": _kalan,
        }
'''

icerik = icerik.replace(eski, yeni, 1)
HEDEF.write_text(icerik, encoding="utf-8")
print("[+] auth.py guncellendi.")