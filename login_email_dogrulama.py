"""
login.py'ye kayit sonrasi email dogrulama ekler.
- Kayit basarili olunca email gonder
- Otomatik giris KALDIR (email dogrulanmadan giremez)
- Kullanici dogrulama linkine tiklayinca giris yapabilir
"""
import shutil
from pathlib import Path
from datetime import datetime

KOK = Path(".")
HEDEF = KOK / "login.py"

icerik = HEDEF.read_text(encoding="utf-8")

if "email_dogrulama_gonder" in icerik:
    print("[i] Zaten eklenmis.")
    raise SystemExit(0)

zaman = datetime.now().strftime("%Y%m%d_%H%M%S")
yedek = KOK / f"login_emaildog_oncesi_{zaman}.py.bak"
shutil.copy2(HEDEF, yedek)
print(f"[+] Yedek: {yedek.name}")

# Eski blok: basarili olduktan sonraki trial + cache + mesaj + otomatik giris
# Bunu yeni bloga cevirecegiz: trial + cache + email gonder + mesaj (oto-giris YOK)

# Tipik blok:
# if basarili:
#     # Trial baslat
#     ...
#     # Cache temizle
#     ...
#     st.success(...)
#     st.info(t("login.firma_sonra_giris"))
#     # Otomatik giris ...

# Basta basit yol: "if basarili:" blogunun devamini gormemiz lazim
# Ama once email gonderimini ekleyelim

# Kayit basarisindan sonra email gonder
eski_kayit_basari = '''                if basarili:
                    # Trial baslat (7 gun ucretsiz)'''

yeni_kayit_basari = '''                if basarili:
                    # Email dogrulama gonder
                    try:
                        _dil = st.session_state.get("dil", "tr")
                        _email_sonuc = auth.email_dogrulama_gonder(yeni_kullanici, yeni_email, _dil)
                        if _email_sonuc.get("durum") == "OK":
                            st.info("📧 " + t("login.email_dogrulama_gonderildi").format(email=yeni_email))
                        else:
                            print(f"[Kayit] Email gonderilemedi: {_email_sonuc}")
                    except Exception as _e:
                        print(f"[Kayit] Email hatasi: {_e}")

                    # Trial baslat (7 gun ucretsiz)'''

if eski_kayit_basari in icerik:
    icerik = icerik.replace(eski_kayit_basari, yeni_kayit_basari, 1)
    print("[+] Email gonderimi eklendi.")

# Otomatik giris blogunu bul ve kaldir
eski_oto_giris = '''                    # Otomatik giris (opsiyonel, biraz daha iyi UX)
                    try:
                        giris_sonuc = auth.giris_yap(yeni_kullanici, yeni_sifre)
                        if giris_sonuc and giris_sonuc.get("durum") == "OK":
                            st.success("🎉 Otomatik giriş yapıldı! Yönlendiriliyorsunuz...")
                            import time
                            time.sleep(1)
                            st.rerun()
                    except Exception:
                        pass'''

yeni_oto_giris = '''                    # OTOMATIK GIRIS YOK - email dogrulanmasi gerekli
                    st.warning("⚠️ " + t("login.email_dogrulama_gerekli"))'''

if eski_oto_giris in icerik:
    icerik = icerik.replace(eski_oto_giris, yeni_oto_giris, 1)
    print("[+] Otomatik giris kaldirildi.")

HEDEF.write_text(icerik, encoding="utf-8")
print("[+] login.py guncellendi.")
print()
print("=" * 60)
print("SONRAKI: 5 dil cevirileri")
print("=" * 60)