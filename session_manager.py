"""
Session Timeout Yoneticisi
- Belirli sure hareketsizlik sonrasi otomatik cikis
- Kalan sureyi gosterir
- Test icin TIMEOUT_DAKIKA degistirilebilir
"""
import streamlit as st
from datetime import datetime, timedelta

import auth
from i18n import t


# ============================================================
# AYARLAR
# ============================================================
TIMEOUT_DAKIKA = 30          # Uretim: 30 dk
UYARI_DAKIKA = 5             # Son 5 dk kala uyari
TEST_MODU = True          # Test icin True yap


def _simdi():
    return datetime.now()


def session_baslat():
    """Yeni oturum baslatildiginda cagrilir (giris sonrasi)."""
    st.session_state["session_baslangic"] = _simdi()
    st.session_state["session_son_aktivite"] = _simdi()


def session_guncelle():
    """Her sayfa cagrisinda son aktiviteyi gunceller."""
    if "session_son_aktivite" in st.session_state:
        st.session_state["session_son_aktivite"] = _simdi()


def session_kontrol():
    """
    Timeout kontrolu yapar. Sure dolmussa cikis yapar.

    Returns:
        True: Session gecerli
        False: Cikis yapildi (st.stop cagrildi)
    """
    # Giris yapilmamis mi?
    if not auth.giris_yapildi_mi():
        return True

    # Session baslatilmamis mi?
    if "session_son_aktivite" not in st.session_state:
        session_baslat()
        return True

    # Timeout dakika
    timeout = 1 if TEST_MODU else TIMEOUT_DAKIKA
    uyari = 0.5 if TEST_MODU else UYARI_DAKIKA

    # Kalan sure
    son = st.session_state["session_son_aktivite"]
    gecen = (_simdi() - son).total_seconds() / 60  # dakika
    kalan = timeout - gecen

    # Timeout doldu mu?
    if kalan <= 0:
        _cikis_yap()
        return False

    # Uyari goster (son X dk)
    if kalan <= uyari:
        kalan_dk = int(kalan)
        st.session_state["session_uyari_goster"] = kalan_dk

    # SESSION_FIX - Timer login'den sayilir, her render'da sifirlanmaz
    # session_guncelle() KALDIRILDI
    return True


def _cikis_yap():
    """Session timeout nedeniyle cikis yapar."""
    try:
        auth.cikis_yap()
    except Exception:
        pass

    # Session state temizle
    for k in list(st.session_state.keys()):
        if k.startswith("session_"):
            del st.session_state[k]

    st.session_state["session_timeout_oldu"] = True
    st.rerun()


def kalan_sure_goster():
    """Sidebar'da kalan sureyi gosterir."""
    if not auth.giris_yapildi_mi():
        return

    if "session_son_aktivite" not in st.session_state:
        return

    timeout = 1 if TEST_MODU else TIMEOUT_DAKIKA

    son = st.session_state["session_son_aktivite"]
    gecen = (_simdi() - son).total_seconds() / 60
    kalan = max(0, timeout - gecen)

    if kalan > 5:
        st.sidebar.caption(f"⏱️ {t('session.kalan')}: {int(kalan)} {t('session.dk')}")
    elif kalan > 0:
        st.sidebar.warning(f"⚠️ {t('session.son')}: {int(kalan)} {t('session.dk')}")
    else:
        st.sidebar.error(f"🚫 {t('session.doldu')}")


def timeout_mesaji_goster():
    """Timeout sonrasi giris sayfasinda uyari gosterir."""
    if st.session_state.get("session_timeout_oldu"):
        st.warning(t("session.timeout_mesaj"))
        del st.session_state["session_timeout_oldu"]