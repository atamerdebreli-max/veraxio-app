"""
auth.py'ye sifre_karmaşıklık kontrolu ekler.
- En az 8 karakter
- En az 1 buyuk harf
- En az 1 kucuk harf
- En az 1 rakam
"""
import shutil
from pathlib import Path
from datetime import datetime

KOK = Path(".")
HEDEF = KOK / "auth.py"

icerik = HEDEF.read_text(encoding="utf-8")

if "def sifre_kontrol" in icerik:
    print("[i] sifre_kontrol zaten var.")
    raise SystemExit(0)

zaman = datetime.now().strftime("%Y%m%d_%H%M%S")
yedek = KOK / f"auth_sifre_oncesi_{zaman}.py.bak"
shutil.copy2(HEDEF, yedek)
print(f"[+] Yedek: {yedek.name}")

# sifre_hashle fonksiyonundan once ekle
anchor = "def sifre_hashle(sifre):"

if anchor not in icerik:
    print("[!] 'def sifre_hashle' bulunamadi.")
    raise SystemExit(1)

BLOK = '''def sifre_kontrol(sifre):
    """
    Sifre karmasiklik kurallarini kontrol eder.
    Donus: {"durum": "OK"} | {"durum": "HATA", "hata": "...", "kod": "..."}
    """
    if not sifre:
        return {"durum": "HATA", "kod": "BOS", "hata": "Sifre bos olamaz"}

    if len(sifre) < 8:
        return {"durum": "HATA", "kod": "KISA", "hata": "En az 8 karakter olmali"}

    if len(sifre) > 128:
        return {"durum": "HATA", "kod": "UZUN", "hata": "En fazla 128 karakter olmali"}

    if not any(c.isupper() for c in sifre):
        return {"durum": "HATA", "kod": "BUYUK_HARF", "hata": "En az 1 buyuk harf olmali"}

    if not any(c.islower() for c in sifre):
        return {"durum": "HATA", "kod": "KUCUK_HARF", "hata": "En az 1 kucuk harf olmali"}

    if not any(c.isdigit() for c in sifre):
        return {"durum": "HATA", "kod": "RAKAM", "hata": "En az 1 rakam olmali"}

    return {"durum": "OK"}


def sifre_gucu(sifre):
    """
    Sifre gucunu 0-100 arasi puanlar.
    Donus: {"puan": int, "seviye": "ZAYIF"|"ORTA"|"GUCLU"|"COK_GUCLU", "renk": "..."}
    """
    puan = 0

    # Uzunluk
    if len(sifre) >= 8:
        puan += 20
    if len(sifre) >= 12:
        puan += 15
    if len(sifre) >= 16:
        puan += 10

    # Karakter cesitliligi
    if any(c.isupper() for c in sifre):
        puan += 15
    if any(c.islower() for c in sifre):
        puan += 15
    if any(c.isdigit() for c in sifre):
        puan += 10
    if any(not c.isalnum() for c in sifre):
        puan += 15

    seviye = "ZAYIF"
    renk = "#ef4444"  # kirmizi
    if puan >= 80:
        seviye = "COK_GUCLU"
        renk = "#22c55e"  # yesil
    elif puan >= 60:
        seviye = "GUCLU"
        renk = "#22c55e"
    elif puan >= 40:
        seviye = "ORTA"
        renk = "#f59e0b"  # amber
    else:
        seviye = "ZAYIF"
        renk = "#ef4444"

    return {"puan": min(puan, 100), "seviye": seviye, "renk": renk}


'''

icerik = icerik.replace(anchor, BLOK + anchor, 1)
HEDEF.write_text(icerik, encoding="utf-8")
print("[+] auth.py guncellendi (sifre_kontrol + sifre_gucu).")
print()
print("=" * 60)
print("TEST: py -c \"import auth; print(auth.sifre_kontrol('abc12345'))\"")
print("=" * 60)