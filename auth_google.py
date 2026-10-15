"""
auth_google.py - Google OAuth 2.0 ile SSO
"""
import streamlit as st
from authlib.integrations.requests_client import OAuth2Session


def _client_id():
    return st.secrets.get("GOOGLE_CLIENT_ID", "")


def _client_secret():
    return st.secrets.get("GOOGLE_CLIENT_SECRET", "")


def _redirect_uri():
    return st.secrets.get("GOOGLE_REDIRECT_URI", "https://veraxio-app.streamlit.app/")


def google_giris_url():
    """Google yetkilendirme URL'i olusturur."""
    if not _client_id() or not _client_secret():
        return None
    try:
        client = OAuth2Session(
            client_id=_client_id(),
            client_secret=_client_secret(),
            redirect_uri=_redirect_uri(),
            scope="openid email profile",
        )
        uri, state = client.create_authorization_url(
            "https://accounts.google.com/o/oauth2/v2/auth",
            access_type="offline",
            prompt="consent",
        )
        st.session_state["google_oauth_state"] = state
        return uri
    except Exception as e:
        print(f"[auth_google] URL hatasi: {e}")
        return None


def google_callback(code):
    """Google'dan donen code ile token alir ve kullaniciyi kaydeder."""
    if not _client_id() or not _client_secret():
        return {"durum": "HATA", "mesaj": "Google OAuth yapilandirmasi eksik."}

    try:
        import db
        client = OAuth2Session(
            client_id=_client_id(),
            client_secret=_client_secret(),
            redirect_uri=_redirect_uri(),
        )
        token = client.fetch_token(
            "https://oauth2.googleapis.com/token",
            code=code,
        )
        # Kullanici bilgisini al
        resp = client.get("https://www.googleapis.com/oauth2/v2/userinfo")
        if resp.status_code != 200:
            return {"durum": "HATA", "mesaj": "Kullanici bilgisi alinamadi."}
        bilgi = resp.json()
        email = bilgi.get("email", "")
        ad_soyad = bilgi.get("name", "")
        if not email:
            return {"durum": "HATA", "mesaj": "E-posta alinamadi."}

        # Kullanici var mi?
        kullanici = db.kullanici_bul(email)
        if not kullanici:
            # Yeni kullanici olustur
            import secrets
            sifre_hash = "GOOGLE_SSO_" + secrets.token_hex(16)
            db.kullanici_ekle(
                kullanici_adi=email,
                sifre_hash=sifre_hash,
                ad_soyad=ad_soyad,
                eposta=email,
                rol="user",
            )
            kullanici = db.kullanici_bul(email)
            if not kullanici:
                return {"durum": "HATA", "mesaj": "Kullanici olusturulamadi."}

        return {"durum": "OK", "kullanici": kullanici}
    except Exception as e:
        return {"durum": "HATA", "mesaj": "Google giris hatasi: " + str(e)}
