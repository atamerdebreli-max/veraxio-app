"""
i18n - Cok dilli destek modulu (hizli versiyon)
Tum ceviriler bellege yuklenir, disk okuma yok.
"""
import json
import os
import streamlit as st


DILLER = {
    "tr": {"ad": "Türkçe", "bayrak": "🇹🇷"},
    "en": {"ad": "English", "bayrak": "🇬🇧"},
    "bg": {"ad": "Български", "bayrak": "🇧🇬"},
    "ro": {"ad": "Română", "bayrak": "🇷🇴"},
    "hr": {"ad": "Hrvatski", "bayrak": "🇭🇷"},
}

LOCALES_KLASOR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "locales")

# ============================================================
# TUM CEVIRILERI BELLEGE YUKLE (modul import edildiginde bir kez)
# ============================================================
_CEVIRILER = {}


def _tum_dilleri_yukle():
    """Tum dil dosyalarini bellege yukler (bir kez)."""
    global _CEVIRILER
    for dil in DILLER.keys():
        dosya = os.path.join(LOCALES_KLASOR, f"{dil}.json")
        try:
            with open(dosya, encoding="utf-8") as f:
                _CEVIRILER[dil] = json.load(f)
        except Exception:
            _CEVIRILER[dil] = {}


# Modul import edildiginde bir kez yukle
_tum_dilleri_yukle()


def t(anahtar, **kwargs):
    """
    Ceviri anahtarini mevcut dile gore dondurur.
    Bellekten okur, disk erisimi YOK.
    """
    dil = st.session_state.get("dil", "tr")
    ceviriler = _CEVIRILER.get(dil, {})

    # Nokta notasyonu ile ic ice anahtar cozumleme
    deger = ceviriler
    for parca in anahtar.split("."):
        if isinstance(deger, dict) and parca in deger:
            deger = deger[parca]
        else:
            # Fallback: Turkce'ye don
            tr_ceviriler = _CEVIRILER.get("tr", {})
            deger_tr = tr_ceviriler
            for p in anahtar.split("."):
                if isinstance(deger_tr, dict) and p in deger_tr:
                    deger_tr = deger_tr[p]
                else:
                    return anahtar
            deger = deger_tr
            break

    if not isinstance(deger, str):
        return anahtar

    if kwargs:
        try:
            return deger.format(**kwargs)
        except (KeyError, IndexError):
            return deger
    return deger


def dil_secici():
    """Sidebar'da dil secici gosterir."""
    with st.sidebar:
        st.markdown("---")
        secili = st.selectbox(
            "🌐 Dil / Language",
            options=list(DILLER.keys()),
            format_func=lambda k: f"{DILLER[k]['bayrak']} {DILLER[k]['ad']}",
            index=list(DILLER.keys()).index(st.session_state.get("dil", "tr")),
            key="dil_secici_widget",
        )
        if secili != st.session_state.get("dil", "tr"):
            st.session_state["dil"] = secili
            st.rerun()