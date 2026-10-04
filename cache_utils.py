"""
Cache yardimcisi - Streamlit @st.cache_data sarmalayicilari

Kullanim:
    from cache_utils import istatistik_cached, listele_cached, cache_temizle

    ist = istatistik_cached(firma_id=1)          # 60 sn cache
    kayitlar = listele_cached(firma_id=1)        # 60 sn cache

Yeni kayit eklendiginde:
    cache_temizle()
"""
import streamlit as st
import db


# ============================================================
# CACHE SURELERI (saniye)
# ============================================================
TTL_KISA = 60     # 1 dk - sik degisen (denetimler)
TTL_UZUN = 300    # 5 dk - nadir degisen (firma/kullanici listesi)


# ============================================================
# CACHE'LI SORGULAR
# ============================================================
@st.cache_data(ttl=TTL_KISA, show_spinner=False)
def istatistik_cached(firma_id=None):
    """Denetim istatistikleri (60 sn cache)."""
    return db.istatistik(firma_id=firma_id)


@st.cache_data(ttl=TTL_KISA, show_spinner=False)
def listele_cached(limit=None, firma_id=None, musteri=None, ai_tipi=None,
                   sonuc=None, tarih_bas=None, tarih_son=None):
    """Denetim kayitlari (60 sn cache)."""
    return db.listele(
        limit=limit,
        filtre_musteri=musteri,
        filtre_ai_tipi=ai_tipi,
        filtre_sonuc=sonuc,
        filtre_tarih_bas=tarih_bas,
        filtre_tarih_son=tarih_son,
        filtre_firma_id=firma_id,
    )


@st.cache_data(ttl=TTL_UZUN, show_spinner=False)
def firma_listele_cached(aktif_only=True):
    """Firma listesi (5 dk cache)."""
    return db.firma_listele(aktif_only=aktif_only)


@st.cache_data(ttl=TTL_UZUN, show_spinner=False)
def kullanicilari_listele_cached():
    """Kullanici listesi (5 dk cache)."""
    return db.kullanicilari_listele()


@st.cache_data(ttl=TTL_UZUN, show_spinner=False)
def firma_kullanicilari_cached(firma_id):
    """Firma kullanicilari (5 dk cache)."""
    return db.firma_kullanicilari(firma_id)


# ============================================================
# CACHE TEMIZLEME
# ============================================================
def cache_temizle():
    """
    Tum cache'leri temizler.
    Yeni kayit eklendiginde / silindiginde cagrilmali.
    """
    istatistik_cached.clear()
    listele_cached.clear()
    firma_listele_cached.clear()
    kullanicilari_listele_cached.clear()
    firma_kullanicilari_cached.clear()


def cache_sadece_denetim_temizle():
    """Sadece denetim cache'lerini temizler (firma/kullanici dokunulmaz)."""
    istatistik_cached.clear()
    listele_cached.clear()