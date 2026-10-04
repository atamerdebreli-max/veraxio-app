"""
auth_2fa.py - Iki Faktorlu Dogrulama (2FA) modulu
TOTP (Time-based One-Time Password) kullanir.
Google Authenticator, Microsoft Authenticator, Authy uyumlu.
"""
import io
import base64
import pyotp
import qrcode
import streamlit as st
import db


UYGULAMA_ADI = "AI Uyumluluk Kutusu"


def secret_olustur():
    """Yeni bir TOTP secret olusturur."""
    return pyotp.random_base32()


def qr_kodu_olustur(kullanici_adi, secret):
    """
    QR kod olusturur (base64 PNG).

    Args:
        kullanici_adi: Kullanici adi
        secret: TOTP secret

    Returns:
        str: Base64 encoded PNG data URL
    """
    try:
        # TOTP URI olustur
        totp = pyotp.TOTP(secret)
        uri = totp.provisioning_uri(
            name=kullanici_adi,
            issuer_name=UYGULAMA_ADI,
        )

        # QR kod olustur
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Base64'e cevir
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        img_base64 = base64.b64encode(buffer.getvalue()).decode()

        return f"data:image/png;base64,{img_base64}"
    except Exception as e:
        return None


def kod_dogrula(secret, kod):
    """
    Girilen 6 haneli kodu dogrular.

    Args:
        secret: TOTP secret
        kod: Kullanicinin girdigi 6 haneli kod

    Returns:
        bool: True ise kod gecerli
    """
    if not secret or not kod:
        return False

    try:
        kod = str(kod).strip().replace(" ", "")
        if len(kod) != 6 or not kod.isdigit():
            return False

        totp = pyotp.TOTP(secret)
        # valid_window=1: 30 saniye once/sonra da kabul et
        return totp.verify(kod, valid_window=1)
    except Exception:
        return False


def iki_fa_baslat(kullanici_adi):
    """
    Yeni 2FA kurulumu baslatir.
    Secret olusturur ve QR kod dondurur.

    Returns:
        dict: {"secret": str, "qr_data_url": str}
    """
    secret = secret_olustur()

    # Secret'i gecici olarak session_state'e kaydet
    st.session_state["2fa_setup_secret"] = secret
    st.session_state["2fa_setup_kullanici"] = kullanici_adi

    qr_data = qr_kodu_olustur(kullanici_adi, secret)

    return {
        "secret": secret,
        "qr_data_url": qr_data,
    }


def iki_fa_dogrula_ve_aktiflestir(kullanici_adi, kod):
    """
    Girilen kodu dogrular ve 2FA'yi aktiflestirir.

    Returns:
        dict: {"durum": "OK" | "HATA", "hata": str}
    """
    secret = st.session_state.get("2fa_setup_secret")

    if not secret:
        return {"durum": "HATA", "hata": "Once 2FA kurulumunu baslatin."}

    if not kod_dogrula(secret, kod):
        return {"durum": "HATA", "hata": "Kod gecersiz. Tekrar deneyin."}

    # Secret'i kaydet
    db.totp_secret_guncelle(kullanici_adi, secret)
    db.totp_aktiflestir(kullanici_adi)

    # Audit log
    try:
        db.audit_kaydet(
            eylem="2fa_aktiflestirildi",
            kullanici_adi=kullanici_adi,
            detay="Iki faktorlu dogrulama aktif edildi",
        )
    except Exception:
        pass

    # Session temizle
    if "2fa_setup_secret" in st.session_state:
        del st.session_state["2fa_setup_secret"]
    if "2fa_setup_kullanici" in st.session_state:
        del st.session_state["2fa_setup_kullanici"]

    return {"durum": "OK"}


def iki_fa_gerekli_mi(kullanici_adi):
    """Kullanicinin 2FA aktif mi?"""
    bilgi = db.totp_bilgisi(kullanici_adi)
    return bilgi.get("totp_aktif", False)


def iki_fa_kapat(kullanici_adi, sifre):
    """
    2FA'yi kapatir. Sifre dogrulamasi gerektirir.
    """
    # Sifre kontrolu
    kullanici = db.kullanici_bul(kullanici_adi)
    if not kullanici:
        return {"durum": "HATA", "hata": "Kullanici bulunamadi"}

    # Sifre hash kontrolu (auth modulunden import edilecek)
    import auth
    if not auth.sifre_dogrula(sifre, kullanici["sifre_hash"]):
        return {"durum": "HATA", "hata": "Sifre yanlis"}

    db.totp_devre_disi_birak(kullanici_adi)

    # Audit log
    try:
        db.audit_kaydet(
            eylem="2fa_kapatildi",
            kullanici_adi=kullanici_adi,
            detay="Iki faktorlu dogrulama kapatildi",
        )
    except Exception:
        pass

    return {"durum": "OK"}


def iki_fa_dogrula_giris(kullanici_adi, kod):
    """
    Giris sirasinda 2FA kodunu dogrular.
    """
    bilgi = db.totp_bilgisi(kullanici_adi)
    secret = bilgi.get("totp_secret")

    if not secret:
        return {"durum": "HATA", "hata": "2FA ayarlanmamis"}

    if not kod_dogrula(secret, kod):
        # Basarisiz deneme audit
        try:
            db.audit_kaydet(
                eylem="2fa_basarisiz",
                kullanici_adi=kullanici_adi,
                detay="Yanlis 2FA kodu",
                basarili=False,
            )
        except Exception:
            pass
        return {"durum": "HATA", "hata": "Kod gecersiz"}

    return {"durum": "OK"}