"""
auth.giris_yap() fonksiyonuna email dogrulama zorunlulugu ekler.
- email_dogrulandi = 0 ise giriş YASAK
- Admin muaf (rol='admin')
"""
import shutil
from pathlib import Path
from datetime import datetime

KOK = Path(".")
HEDEF = KOK / "auth.py"

icerik = HEDEF.read_text(encoding="utf-8")

if "email_dogrulandi" in icerik and "DOGRULANMADI" in icerik:
    print("[i] Zaten eklenmis.")
    raise SystemExit(0)

zaman = datetime.now().strftime("%Y%m%d_%H%M%S")
yedek = KOK / f"auth_emailsiz_oncesi_{zaman}.py.bak"
shutil.copy2(HEDEF, yedek)
print(f"[+] Yedek: {yedek.name}")

# giris_yap fonksiyonunda sifre dogrulama sonrasi, basarili giriş oncesi ekle
# Tipki yer: sifre_dogrula(sifre, kullanici["sifre_hash"]) sonrasi
eski = "def giris_yap(kullanici_adi, sifre):"
if eski not in icerik:
    print("[!] giris_yap bulunamadi.")
    raise SystemExit(1)

# Fonksiyonun basina kilit kontrolu var mi?
# Email kontrolu: kullanici bilgisi alindiktan sonra

# Sifre kontrolunden sonra ekleyecegiz - mevcut sifre_dogrula cagrisini bulalim
eski_parola_kontrol = 'if not sifre_dogrula(sifre, kullanici["sifre_hash"]):'

if eski_parola_kontrol not in icerik:
    print("[!] sifre_dogrula cagrisi bulunamadi.")
    raise SystemExit(1)

# Sonrasina email kontrolu ekle - ancak bu kontrol BASARILI ise uygulanmali
# Yani sifre dogruysa VE email dogrulanmamissa hata

# Once sifre_dogrula blogunu bulalim
idx = icerik.find(eski_parola_kontrol)
if idx == -1:
    print("[!] Konum bulunamadi.")
    raise SystemExit(1)

# Bu blokta return varsa bulmamiz lazim
# Tipik yapi:
# if not sifre_dogrula(sifre, kullanici["sifre_hash"]):
#     return {"durum": "HATA", "hata": "..."}
# 
# Devaminda baska kontroller ve basarili giris

# Su an sadece basit hali:
# if not sifre_dogrula(sifre, kullanici["sifre_hash"]):
#     return {"durum": "HATA", "hata": "..."}

# Bulunduğu satırdan itibaren 10 satır alalim
satirlar = icerik[idx:].split("\n")[:12]
print("[i] Bulunan sifre kontrol blogu:")
for s in satirlar[:8]:
    print(f"    {s}")

# Sifre kontrol blogunun bitisini bul - "return" satirindan sonra
# En basit: "if not sifre_dogrula" satirini bul ve o blogun tamamini al
# Ama return sonrasi degisebilir, o yuzden sabit bir blok ariyoruz

eski_blok = '''if not sifre_dogrula(sifre, kullanici["sifre_hash"]):
        return {"durum": "HATA", "hata": "Kullanici adi veya sifre yanlis"}'''

if eski_blok not in icerik:
    # Belki farkli hata mesaji
    # Regex ile ara
    import re
    pattern = r'if not sifre_dogrula\(sifre, kullanici\["sifre_hash"\]\):\n\s*return \{"durum": "HATA", "hata": "[^"]+"\}'
    m = re.search(pattern, icerik)
    if m:
        eski_blok = m.group(0)
        print(f"[i] Regex ile bulundu: {eski_blok[:60]}...")
    else:
        print("[!] Sifre kontrol blogu bulunamadi.")
        raise SystemExit(1)

yeni_blok = eski_blok + '''

    # EMAIL DOGRULAMA KONTROLU (sadece admin degilse)
    _rol = kullanici.get("rol", "user")
    _email_dogrulandi = kullanici.get("email_dogrulandi", 1)  # None ise 1 varsay (eski kayitlar)

    if _rol != "admin" and not _email_dogrulandi:
        return {
            "durum": "HATA",
            "hata": "E-posta adresiniz dogrulanmamis. Lutfen e-postaniza gelen dogrulama linkine tiklayin.",
            "kod": "DOGRULANMADI",
        }'''

icerik = icerik.replace(eski_blok, yeni_blok, 1)
HEDEF.write_text(icerik, encoding="utf-8")
print("[+] auth.py guncellendi (email dogrulama zorunlulugu).")