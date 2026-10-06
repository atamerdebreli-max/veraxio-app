"""login.py'ye brute force deneme kaydi ekler."""
import shutil
from pathlib import Path
from datetime import datetime

KOK = Path(".")
HEDEF = KOK / "login.py"

icerik = HEDEF.read_text(encoding="utf-8")

if "giris_denemesi_kaydet" in icerik:
    print("[i] Zaten eklenmis.")
    raise SystemExit(0)

zaman = datetime.now().strftime("%Y%m%d_%H%M%S")
yedek = KOK / f"login_brute_oncesi_{zaman}.py.bak"
shutil.copy2(HEDEF, yedek)
print(f"[+] Yedek: {yedek.name}")

eski = '''                else:
                    # Normal giris
                    sonuc = auth.giris_yap(kullanici_adi, sifre)
                    if sonuc["durum"] == "OK":
                        st.success(t("login.giris_basarili"))
                        st.rerun()
                    else:
                        st.error(t("login.giris_hata"))'''

yeni = '''                else:
                    # Normal giris + brute force korumasi
                    _kilit = db.giris_kilitli_mi(kullanici_adi)
                    if _kilit.get("kilitli"):
                        _kalan = _kilit.get("kalan_dk", 0)
                        st.error(f"🔒 Hesabiniz gecici olarak kilitli. {_kalan} dakika sonra tekrar deneyin.")
                        st.stop()

                    sonuc = auth.giris_yap(kullanici_adi, sifre)
                    if sonuc["durum"] == "OK":
                        db.giris_denemesi_kaydet(kullanici_adi, basarili=True)
                        st.success(t("login.giris_basarili"))
                        st.rerun()
                    else:
                        db.giris_denemesi_kaydet(kullanici_adi, basarili=False)
                        _kalan_hak = db.kalan_deneme_hakki(kullanici_adi)
                        if _kalan_hak > 0:
                            st.error(t("login.giris_hata") + f" ({_kalan_hak} hakkiniz kaldi)")
                        else:
                            st.error("🔒 Hesabiniz 15 dakika kilitlendi. Lutfen sonra tekrar deneyin.")
                        st.stop()'''

if eski not in icerik:
    print("[!] Hedef blok bulunamadi.")
    raise SystemExit(1)

icerik = icerik.replace(eski, yeni, 1)
HEDEF.write_text(icerik, encoding="utf-8")
print("[+] login.py guncellendi.")