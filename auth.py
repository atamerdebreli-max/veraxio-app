"""
auth.py - Kimlik dogrulama modulu
bcrypt ile sifre hash'leme, oturum yonetimi
"""
import bcrypt
import streamlit as st
import db
from i18n import t


def sifre_kontrol(sifre):
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


def sifre_hashle(sifre):
    """Sifreyi bcrypt ile hash'ler."""
    return bcrypt.hashpw(sifre.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def sifre_dogrula(sifre, sifre_hash):
    """Sifreyi hash ile dogrular."""
    try:
        return bcrypt.checkpw(sifre.encode("utf-8"), sifre_hash.encode("utf-8"))
    except Exception:
        return False


def giris_yap(kullanici_adi, sifre):
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

    """
    Kullanici girisi yapar.
    Returns:
        dict: {"durum": "OK" | "HATA", "kullanici": {...}, "hata": "..."}
    """
    if not kullanici_adi or not sifre:
        return {"durum": "HATA", "hata": "Kullanici adi ve sifre zorunlu"}

    kullanici = db.kullanici_bul(kullanici_adi)
    if not kullanici:
        try:
            db.audit_kaydet(
                eylem="giris_basarisiz",
                kullanici_adi=kullanici_adi,
                detay="Kullanici bulunamadi",
                basarili=False,
            )
        except Exception:
            pass
        return {"durum": "HATA", "hata": "Kullanici adi veya sifre hatali"}

    if not sifre_dogrula(sifre, kullanici["sifre_hash"]):
        try:
            db.audit_kaydet(
                eylem="giris_basarisiz",
                kullanici_adi=kullanici_adi,
                firma_id=kullanici.get("firma_id"),
                detay="Yanlis sifre",
                basarili=False,
            )
        except Exception:
            pass
        return {"durum": "HATA", "hata": "Kullanici adi veya sifre hatali"}

    # EMAIL DOGRULAMA KONTROLU (sadece admin degilse)
    _rol = kullanici.get("rol", "user")
    _email_dogrulandi = kullanici.get("email_dogrulandi", 1)  # None ise 1 varsay

    if _rol != "admin" and not _email_dogrulandi:
        try:
            db.audit_kaydet(
                eylem="giris_email_dogrulanmadi",
                kullanici_adi=kullanici_adi,
                firma_id=kullanici.get("firma_id"),
                detay="Email dogrulanmamis",
                basarili=False,
            )
        except Exception:
            pass
        return {
            "durum": "HATA",
            "hata": "E-posta adresiniz dogrulanmamis. Lutfen e-postaniza gelen dogrulama linkine tiklayin.",
            "kod": "DOGRULANMADI",
        }

    # Son giris guncelle
    db.kullanici_giris_guncelle(kullanici_adi)

    # Audit log - basarili giris
    try:
        db.audit_kaydet(
            eylem="giris_basarili",
            kullanici_adi=kullanici["kullanici_adi"],
            firma_id=kullanici.get("firma_id"),
            detay=f"Rol: {kullanici.get('rol', 'user')}",
            basarili=True,
        )
    except Exception:
        pass

    # Firma bilgisini al
    firma_id = kullanici.get("firma_id")
    firma = db.firma_bul(firma_id) if firma_id else None

    # Admin icin varsayilan firma adi
    rol = kullanici.get("rol", "user")
    if rol == "admin" and not firma:
        firma_adi_goster = "Sistem Yonetimi (Admin)"
    else:
        firma_adi_goster = firma["firma_adi"] if firma else "-"

    # Session'a kaydet
    st.session_state["user"] = {
        "kullanici_adi": kullanici["kullanici_adi"],
        "ad_soyad": kullanici.get("ad_soyad", ""),
        "eposta": kullanici.get("eposta", ""),
        "rol": rol,
        "firma_id": firma_id,
        "firma_rol": kullanici.get("firma_rol", "user"),
        "firma_adi": firma_adi_goster,
    }

    return {"durum": "OK", "kullanici": st.session_state["user"]}


def cikis_yap():
    """Oturumu kapatir."""
    if "user" in st.session_state:
        try:
            kullanici = st.session_state["user"]
            db.audit_kaydet(
                eylem="cikis",
                kullanici_adi=kullanici.get("kullanici_adi"),
                firma_id=kullanici.get("firma_id"),
                detay="Kullanici cikis yapti",
            )
        except Exception:
            pass
        del st.session_state["user"]


def giris_yapildi_mi():
    """Kullanici giris yapmis mi kontrol eder."""
    return "user" in st.session_state and st.session_state["user"] is not None


def mevcut_kullanici():
    """Mevcut kullaniciyi dondurur."""
    return st.session_state.get("user")


def admin_mi():
    """Kullanici sistem admini mi?"""
    user = mevcut_kullanici()
    return user and user.get("rol") == "admin"


def firma_id():
    """Mevcut kullanicinin firma ID'sini dondurur."""
    user = mevcut_kullanici()
    return user.get("firma_id") if user else None


def firma_adi():
    """Mevcut kullanicinin firma adini dondurur."""
    user = mevcut_kullanici()
    return user.get("firma_adi", "") if user else ""


def firma_admin_mi():
    """Kullanici firma admini mi?"""
    user = mevcut_kullanici()
    return user and user.get("firma_rol") in ["admin", "owner"]


def firma_yoneticisi_mi():
    """Kullanici firma yoneticisi veya sistem admini mi?"""
    return admin_mi() or firma_admin_mi()


def firma_gerekli():
    """
    Firma gerektiren sayfalar icin.
    Firma yoksa uyari gosterir.
    """
    if not firma_id():
        st.warning(t("auth.firma_gerekli"))
        st.info(t("auth.firma_yonlendir"))
        st.stop()


def davet_kabul_et_ve_kayit_ol(token, kullanici_adi, sifre, ad_soyad=""):
    """
    Davet token'i ile kayit olur.
    Returns:
        dict: {"durum": "OK" | "HATA", "hata": "..."}
    """
    davet = db.davet_bul(token)
    if not davet:
        return {"durum": "HATA", "hata": "Gecersiz veya suresi dolmus davet"}

    # Kullanici adi kontrolu
    if db.kullanici_bul(kullanici_adi):
        return {"durum": "HATA", "hata": "Bu kullanici adi zaten alinmis"}

    # Kullanici olustur
    sifre_h = sifre_hashle(sifre)
    basarili = db.kullanici_ekle_firma(
        kullanici_adi=kullanici_adi,
        sifre_hash=sifre_h,
        ad_soyad=ad_soyad,
        eposta=davet["eposta"],
        firma_id=davet["firma_id"],
        firma_rol=davet["rol"],
        rol="user",
    )

    if not basarili:
        return {"durum": "HATA", "hata": "Kullanici olusturulamadi"}

    # Daveti kabul edildi olarak isaretle
    db.davet_kabul_et(token)

    return {"durum": "OK"}


def giris_gerekli():
    """
    Giris gerektiren sayfalarin basinda cagrilir.
    Giris yapilmamissa login sayfasina yonlendirir.
    """
    if not giris_yapildi_mi():
        st.warning(t("auth.giris_gerekli"))
        st.info(t("auth.giris_yonlendir"))
        st.stop()


def ilk_kullanici_olustur():
    """
    Ilk admin kullanicisini olusturur (eger hic kullanici yoksa).
    Kullanici adi: admin, Sifre: admin123
    """
    kullanicilar = db.kullanicilari_listele()
    if not kullanicilar:
        sifre_h = sifre_hashle("admin123")
        db.kullanici_ekle(
            kullanici_adi="admin",
            sifre_hash=sifre_h,
            ad_soyad="Sistem Yoneticisi",
            eposta="admin@veraxio.ai",
            rol="admin",
        )
        return True
    return False

# ============================================================
# SIFRE SIFIRLAMA
# ============================================================
def sifre_sifirlama_baslat(kullanici_adi_veya_email, dil="tr"):
    """
    Sifre sifirlama surecini baslatir.
    Token olusturur ve e-posta gonderir.
    """
    from email_sender import sifre_sifirlama_emaili_gonder

    # Kullanici adi veya e-posta ile bul
    kullanici = db.kullanici_bul(kullanici_adi_veya_email)
    if not kullanici:
        # E-posta ile ara
        for k in db.kullanicilari_listele():
            if k.get("eposta") == kullanici_adi_veya_email:
                kullanici = db.kullanici_bul(k["kullanici_adi"])
                break

    if not kullanici:
        # Guvenlik icin ayni mesaji goster
        return {"durum": "OK", "mesaj": "Eger bu bilgiler kayitliysa, sifre sifirlama e-postasi gonderildi."}

    # Token olustur
    token = db.token_olustur(
        kullanici_adi=kullanici["kullanici_adi"],
        eposta=kullanici.get("eposta", ""),
        tip="sifre_sifirlama",
        sure_saat=24,
    )

    # E-posta gonder
    sonuc = sifre_sifirlama_emaili_gonder(
        alici=kullanici.get("eposta", ""),
        kullanici_adi=kullanici["kullanici_adi"],
        token=token,
        dil=dil,
    )

    return {
        "durum": "OK",
        "mesaj": "Sifre sifirlama e-postasi gonderildi.",
        "email_sonuc": sonuc,
    }


def sifre_sifirla(token, yeni_sifre):
    """
    Token ile sifre sifirlar.
    """
    # Token'i bul
    token_kayit = db.token_bul(token, tip="sifre_sifirlama")
    if not token_kayit:
        return {"durum": "HATA", "hata": "Gecersiz veya suresi dolmus token"}

    if len(yeni_sifre) < 6:
        return {"durum": "HATA", "hata": "Sifre en az 6 karakter olmali"}

    # Sifreyi guncelle
    sifre_h = sifre_hashle(yeni_sifre)
    db.sifre_guncelle(token_kayit["kullanici_adi"], sifre_h)

    # Token'i kullanildi olarak isaretle
    db.token_kullanildi(token)

    # Audit log
    try:
        db.audit_kaydet(
            eylem="sifre_sifirlandi",
            kullanici_adi=token_kayit["kullanici_adi"],
            detay="Sifre sifirlama ile degistirildi",
        )
    except Exception:
        pass

    return {"durum": "OK", "kullanici_adi": token_kayit["kullanici_adi"]}


# ============================================================
# EMAIL DOGRULAMA
# ============================================================
def email_dogrulama_gonder(kullanici_adi, eposta, dil="tr"):
    """Email dogrulama linki gonderir."""
    from email_sender import email_dogrulama_gonder as _email_gonder

    token = db.token_olustur(
        kullanici_adi=kullanici_adi,
        eposta=eposta,
        tip="email_dogrulama",
        sure_saat=48,
    )

    sonuc = _email_gonder(
        alici=eposta,
        kullanici_adi=kullanici_adi,
        token=token,
        dil=dil,
    )

    return sonuc


def email_dogrula(token):
    """Email dogrulama token'ini isler."""
    token_kayit = db.token_bul(token, tip="email_dogrulama")
    if not token_kayit:
        return {"durum": "HATA", "hata": "Gecersiz veya suresi dolmus token"}

    # Kullaniciyi dogrula
    db.kullanici_dogrula(token_kayit["kullanici_adi"])

    # Token'i kullanildi olarak isaretle
    db.token_kullanildi(token)

    return {"durum": "OK", "kullanici_adi": token_kayit["kullanici_adi"]}
