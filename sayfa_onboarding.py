"""
Onboarding sayfasi - Yeni kullanici icin 5 adimli rehber
"""
import streamlit as st

import auth
auth.giris_gerekli()

import db
from i18n import t

db.init_db()

kullanici = auth.mevcut_kullanici()
kullanici_adi = kullanici.get("kullanici_adi", "-")

# ============================================================
# DURUM
# ============================================================
if "onboarding_adim" not in st.session_state:
    st.session_state["onboarding_adim"] = 0

adim = st.session_state["onboarding_adim"]

# ============================================================
# ATLA
# ============================================================
if adim == -1:
    st.success("✅ " + t("onboarding.atlandi"))
    st.session_state["onboarding_gosterildi"] = True
    if st.button("→ " + t("onboarding.devam_et"), type="primary"):
        st.switch_page("sayfa_dashboard.py")
    st.stop()

# ============================================================
# TAMAMLA
# ============================================================
if adim >= 5:
    st.balloons()
    st.success("🎉 " + t("onboarding.tamamlandi"))
    st.markdown(t("onboarding.tamamlandi_aciklama"))

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 " + t("onboarding.dashboard_git"), type="primary", use_container_width=True):
            st.session_state["onboarding_gosterildi"] = True
            st.switch_page("sayfa_dashboard.py")
    with col2:
        if st.button("🔍 " + t("onboarding.tek_denetim_git"), use_container_width=True):
            st.session_state["onboarding_gosterildi"] = True
            st.switch_page("sayfa_tek.py")
    st.stop()

# ============================================================
# BAŞLIK + İLERLEME
# ============================================================
st.title("👋 " + t("onboarding.baslik"))
st.markdown(t("onboarding.alt_baslik").format(ad=kullanici.get("ad_soyad") or kullanici_adi))
st.markdown("---")

# İlerleme
st.progress((adim) / 5)
st.caption(f"{t('onboarding.adim')} {adim + 1} / 5")
st.markdown("")

# ============================================================
# ADIMLAR
# ============================================================
ADIMLAR = [
    {
        "ikon": "🎯",
        "baslik": t("onboarding.adim1_baslik"),
        "aciklama": t("onboarding.adim1_aciklama"),
        "ipucu": t("onboarding.adim1_ipucu"),
    },
    {
        "ikon": "🤖",
        "baslik": t("onboarding.adim2_baslik"),
        "aciklama": t("onboarding.adim2_aciklama"),
        "ipucu": t("onboarding.adim2_ipucu"),
    },
    {
        "ikon": "📄",
        "baslik": t("onboarding.adim3_baslik"),
        "aciklama": t("onboarding.adim3_aciklama"),
        "ipucu": t("onboarding.adim3_ipucu"),
    },
    {
        "ikon": "⏰",
        "baslik": t("onboarding.adim4_baslik"),
        "aciklama": t("onboarding.adim4_aciklama"),
        "ipucu": t("onboarding.adim4_ipucu"),
    },
    {
        "ikon": "📊",
        "baslik": t("onboarding.adim5_baslik"),
        "aciklama": t("onboarding.adim5_aciklama"),
        "ipucu": t("onboarding.adim5_ipucu"),
    },
]

aktif = ADIMLAR[adim]

# Kart
st.markdown(f"## {aktif['ikon']} {aktif['baslik']}")
st.markdown(f"### {aktif['aciklama']}")

st.info("💡 **" + t("onboarding.ipucu") + ":** " + aktif["ipucu"])

st.markdown("---")

# ============================================================
# BUTONLAR
# ============================================================
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    if st.button("← " + t("onboarding.geri"), disabled=(adim == 0), use_container_width=True):
        st.session_state["onboarding_adim"] = max(0, adim - 1)
        st.rerun()

with col2:
    if st.button("→ " + t("onboarding.ileri"), type="primary", use_container_width=True):
        st.session_state["onboarding_adim"] = adim + 1
        st.rerun()

with col3:
    if st.button("⏭️ " + t("onboarding.atla"), use_container_width=True):
        st.session_state["onboarding_adim"] = -1
        st.rerun()

st.markdown("")

# Adım noktaları
noktalar = ""
for i in range(5):
    if i < adim:
        noktalar += "🟢 "
    elif i == adim:
        noktalar += "🔵 "
    else:
        noktalar += "⚪ "
st.caption(noktalar)