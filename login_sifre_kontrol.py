"""
login.py'deki sifre kontrollerini auth.sifre_kontrol() ile guclendirir.
- Kayit formu
- Sifre sifirlama formu
- Sifre gucluluk gostergesi (opsiyonel)
"""
import shutil
from pathlib import Path
from datetime import datetime

KOK = Path(".")
HEDEF = KOK / "login.py"

icerik = HEDEF.read_text(encoding="utf-8")

zaman = datetime.now().strftime("%Y%m%d_%H%M%S")
yedek = KOK / f"login_sifre_oncesi_{zaman}.py.bak"
shutil.copy2(HEDEF, yedek)
print(f"[+] Yedek: {yedek.name}")

# ============================================================
# 1) Kayit formunda: len(yeni_sifre) < 6 -> auth.sifre_kontrol
# ============================================================
sayi = 0

# Kayit sekmesindeki 3 kontrolu degistir
eski_kayit = '''            if not firma_adi or not yeni_kullanici or not yeni_sifre:
                st.error(t("login.firma_zorunlu"))
            elif len(yeni_sifre) < 6:
                st.error(t("login.sifre_kisa"))
            elif yeni_sifre != yeni_sifre2:
                st.error(t("login.sifre_eslesmiyor"))
            else:'''

yeni_kayit = '''            if not firma_adi or not yeni_kullanici or not yeni_sifre:
                st.error(t("login.firma_zorunlu"))
            else:
                _sk = auth.sifre_kontrol(yeni_sifre)
                if _sk["durum"] != "OK":
                    st.error("❌ " + _sk["hata"])
                    st.stop()
                if yeni_sifre != yeni_sifre2:
                    st.error(t("login.sifre_eslesmiyor"))
                    st.stop()'''

if eski_kayit in icerik:
    icerik = icerik.replace(eski_kayit, yeni_kayit, 1)
    sayi += 1
    print("[+] Kayit formu guncellendi.")

# Kayit formunun devami
eski_kayit2 = '''                firma_id = db.firma_ekle('''
yeni_kayit2 = '''                firma_id = db.firma_ekle('''

# Ikinci bir kontrol (firma olustur blogunda)
# Bu bloktaki sifre kontrolu zaten eskiden beri var

# Davet kabul formu
eski_davet = '''                    if not dav_kullanici or not dav_sifre:
                        st.error(t("login.zorunlu"))
                    elif len(dav_sifre) < 6:
                        st.error(t("login.sifre_kisa"))
                    elif dav_sifre != dav_sifre2:
                        st.error(t("login.sifre_eslesmiyor"))
                    else:'''

yeni_davet = '''                    if not dav_kullanici or not dav_sifre:
                        st.error(t("login.zorunlu"))
                    else:
                        _sk2 = auth.sifre_kontrol(dav_sifre)
                        if _sk2["durum"] != "OK":
                            st.error("❌ " + _sk2["hata"])
                            st.stop()
                        if dav_sifre != dav_sifre2:
                            st.error(t("login.sifre_eslesmiyor"))
                            st.stop()'''

if eski_davet in icerik:
    icerik = icerik.replace(eski_davet, yeni_davet, 1)
    sayi += 1
    print("[+] Davet kabul formu guncellendi.")

# Sifre sifirlama formu
eski_sifre_sifirla = '''            if not yeni_sifre:
                    st.error(t("login.zorunlu"))
                elif len(yeni_sifre) < 6:
                    st.error(t("login.sifre_kisa"))
                elif yeni_sifre != yeni_sifre2:
                    st.error(t("login.sifre_eslesmiyor"))
                else:'''

# Alternatif format
eski_ss_alt = '''            if not yeni_sifre:
                    st.error(t("login.zorunlu"))
                elif len(yeni_sifre) < 6:
                    st.error(t("login.sifre_kisa"))
                elif yeni_sifre != yeni_sifre2:
                    st.error(t("login.sifre_eslesmiyor"))'''

if eski_ss_alt in icerik:
    # Sadece kontrol satirlarini degistir
    icerik = icerik.replace(
        'elif len(yeni_sifre) < 6:\n                    st.error(t("login.sifre_kisa"))',
        'elif auth.sifre_kontrol(yeni_sifre)["durum"] != "OK":\n                    st.error("❌ " + auth.sifre_kontrol(yeni_sifre)["hata"])'
    )
    sayi += 1
    print("[+] Sifre sifirlama formu guncellendi.")

HEDEF.write_text(icerik, encoding="utf-8")
print(f"[+] {sayi} form guncellendi.")
print()
print("=" * 60)
print("TEST: Streamlit -> R tusuna bas")
print("=" * 60)