"""
email_sender.py'deki 2 fonksiyonu HTML'e cevirir + Veraxio markasi ekler.
- deneme_emaili_gonder: HTML hos geldin email
- sifre_sifirlama_emaili_gonder: HTML sifre sifirlama email
"""
import shutil
from pathlib import Path
from datetime import datetime

KOK = Path(".")
HEDEF = KOK / "email_sender.py"

icerik = HEDEF.read_text(encoding="utf-8")

if "Veraxio HTML" in icerik:
    print("[i] Zaten cevrilmis.")
    raise SystemExit(0)

zaman = datetime.now().strftime("%Y%m%d_%H%M%S")
yedek = KOK / f"email_cevir_oncesi_{zaman}.py.bak"
shutil.copy2(HEDEF, yedek)
print(f"[+] Yedek: {yedek.name}")

# ============================================================
# 1) deneme_emaili_gonder -> HTML
# ============================================================
eski_deneme = '''def deneme_emaili_gonder(alici):
    """Test e-postasi gonderir."""
    return email_gonder(
        alici=alici,
        konu="AI Uyumluluk Kutusu - Test E-postasi",
        icerik=(
            "Merhaba,\\n\\n"
            "Bu bir test e-postasidir. AI Uyumluluk Kutusu "
            "otomatik rapor gonderim sistemi calisiyor.\\n\\n"
            "Saygilarimizla,\\n"
            "AI Uyumluluk Kutusu"
        ),
        pdf_yolu=None,
    )'''

yeni_deneme = '''def deneme_emaili_gonder(alici, kullanici_adi="Test", firma_adi="Veraxio", dil="tr"):
    """Test e-postasi gonderir (HTML - Veraxio HTML)."""
    html = hos_geldin_email(kullanici_adi, firma_adi, dil)
    return email_gonder(
        alici=alici,
        konu="Veraxio - Test E-postasi",
        icerik=html,
        pdf_yolu=None,
        html=True,
    )'''

if eski_deneme in icerik:
    icerik = icerik.replace(eski_deneme, yeni_deneme, 1)
    print("[+] deneme_emaili_gonder HTML'e cevrildi.")
else:
    print("[!] deneme_emaili_gonder bulunamadi.")

# ============================================================
# 2) sifre_sifirlama_emaili_gonder -> HTML
# ============================================================
# Fonksiyonun tam blogunu bul (karmasik, regex ile)
import re

# Fonksiyon baslangicini bul
idx_bas = icerik.find("def sifre_sifirlama_emaili_gonder(")
if idx_bas == -1:
    print("[!] sifre_sifirlama_emaili_gonder bulunamadi.")
else:
    # Bir sonraki def'e kadar ara
    idx_son = icerik.find("\ndef ", idx_bas + 10)
    if idx_son == -1:
        idx_son = len(icerik)

    eski_sifre_blok = icerik[idx_bas:idx_son]

    yeni_sifre_blok = '''def sifre_sifirlama_emaili_gonder(alici, kullanici_adi, token, dil="tr"):
    """Sifre sifirlama e-postasi gonderir (HTML - Veraxio HTML)."""
    # URL - Worker domain ile
    url = f"http://localhost:8501/?sifre_sifirla={token}"

    KONULAR = {
        "tr": "Veraxio - Sifre Sifirlama",
        "en": "Veraxio - Password Reset",
        "bg": "Veraxio - Нулиране на парола",
        "ro": "Veraxio - Resetare parola",
        "hr": "Veraxio - Ponistavanje lozinke",
    }
    konu = KONULAR.get(dil, KONULAR["tr"])

    html = sifre_sifirla_email(kullanici_adi, url, dil)

    return email_gonder(
        alici=alici,
        konu=konu,
        icerik=html,
        pdf_yolu=None,
        html=True,
    )

'''

    icerik = icerik[:idx_bas] + yeni_sifre_blok + icerik[idx_son:]
    print("[+] sifre_sifirlama_emaili_gonder HTML'e cevrildi.")

HEDEF.write_text(icerik, encoding="utf-8")
print("[+] email_sender.py kaydedildi.")
print()
print("=" * 60)
print("SONRAKI: Test")
print("  py -c \"import email_sender; print('OK')\"")
print("=" * 60)