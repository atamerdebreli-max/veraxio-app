"""
sayfa_envanter.py - AI Sistem Envanteri
"""
import streamlit as st
import auth
auth.giris_gerekli()

import db
from i18n import t


st.title("📋 " + t("envanter.baslik"))
st.markdown("**" + t("envanter.alt_baslik") + "**")
st.markdown("---")

kullanici = auth.mevcut_kullanici()
firma_id = kullanici.get("firma_id") if kullanici else None

# ============================================================
# ISTATISTIK
# ============================================================
try:
    ist = db.envanter_istatistik(firma_id)
    col1, col2, col3 = st.columns(3)
    col1.metric(t("envanter.toplam"), ist["toplam"])
    col2.metric(t("envanter.riskli"), ist["riskli"])
    col3.metric(t("envanter.denetlenmis"), ist["denetlenmis"])
    st.markdown("---")
except Exception as e:
    st.warning(t("envanter.kayit_hatasi") + str(e))

# ============================================================
# YENI SISTEM EKLEME FORMU
# ============================================================
with st.expander(t("envanter.yeni_ekle"), expanded=False):
    with st.form("envanter_ekle_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            sistem_adi = st.text_input(t("envanter.sistem_adi") + " *", placeholder=t("envanter.sistem_adi_placeholder"))
            ai_tipi = st.selectbox(t("envanter.ai_tipi") + " *", [
                t("ai_tipleri.chatbot"), t("ai_tipleri.gorsel"), t("ai_tipleri.metin"),
                t("ai_tipleri.kvkk"), t("ai_tipleri.ab_temsilcisi"), t("ai_tipleri.shadow_ai"),
                t("ai_tipleri.kumulatif"), t("ai_tipleri.duygu_musteri"), t("ai_tipleri.duygu_calisan"),
                t("ai_tipleri.biyometrik"), t("ai_tipleri.deepfake"), t("ai_tipleri.kamu_metni"),
                "Diğer",
            ])
            departman = st.text_input(t("envanter.departman"), placeholder=t("envanter.departman_placeholder"))
        with col2:
            sorumlu_kisi = st.text_input(t("envanter.sorumlu_kisi"), placeholder=t("envanter.sorumlu_placeholder"))
            amac = st.text_area(t("envanter.amac"), placeholder=t("envanter.amac_placeholder"), height=80)
            risk_seviyesi = st.selectbox(t("envanter.risk_seviyesi"), [
                t("envanter.risk_bilinmiyor"), t("envanter.risk_dusuk"),
                t("envanter.risk_orta"), t("envanter.risk_yuksek"), t("envanter.risk_kritik"),
            ])
        notlar = st.text_area(t("envanter.notlar"), height=60)

        submitted = st.form_submit_button(t("envanter.kaydet"), type="primary", use_container_width=True)
        if submitted:
            if not sistem_adi:
                st.error(t("envanter.sistem_adi_zorunlu"))
            else:
                try:
                    risk_map = {
                        t("envanter.risk_bilinmiyor"): "bilinmiyor",
                        t("envanter.risk_dusuk"): "minimal",
                        t("envanter.risk_orta"): "sinirli",
                        t("envanter.risk_yuksek"): "yuksek",
                        t("envanter.risk_kritik"): "kritik",
                    }
                    db.envanter_ekle(
                        firma_id=firma_id,
                        sistem_adi=sistem_adi,
                        ai_tipi=ai_tipi,
                        departman=departman,
                        sorumlu_kisi=sorumlu_kisi,
                        amac=amac,
                        risk_seviyesi=risk_map.get(risk_seviyesi, "bilinmiyor"),
                        notlar=notlar,
                    )
                    st.success(t("envanter.sistem_eklendi") + sistem_adi)
                    st.rerun()
                except Exception as e:
                    st.error(t("envanter.kayit_hatasi") + str(e))

# ============================================================
# ENVANTER LISTESI
# ============================================================
st.subheader(t("envanter.sistem_listesi"))

try:
    envanter = db.envanter_listele(firma_id=firma_id, sadece_aktif=True)
except Exception as e:
    st.error(t("envanter.kayit_hatasi") + str(e))
    envanter = []

if not envanter:
    st.info(t("envanter.bos_mesaj"))
else:
    for sistem in envanter:
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            with col1:
                st.markdown("### " + sistem["sistem_adi"])
                st.caption("🏢 " + (sistem.get("departman") or "-") + " · 👤 " + (sistem.get("sorumlu_kisi") or "-"))
            with col2:
                st.caption("**" + t("envanter.ai_tipi") + ":** " + (sistem.get("ai_tipi") or "-"))
                risk = sistem.get("risk_seviyesi", "bilinmiyor")
                if risk in ("yuksek", "kritik"):
                    st.error("🔴 " + t("envanter.risk_seviyesi") + ": " + t("envanter.risk_" + ("yuksek" if risk == "yuksek" else "kritik")))
                elif risk == "sinirli":
                    st.warning("🟡 " + t("envanter.risk_seviyesi") + ": " + t("envanter.risk_orta"))
                elif risk == "minimal":
                    st.success("🟢 " + t("envanter.risk_seviyesi") + ": " + t("envanter.risk_dusuk"))
                else:
                    st.info("⚪ " + t("envanter.risk_seviyesi") + ": " + t("envanter.risk_bilinmiyor"))
            with col3:
                son_denetim = sistem.get("son_denetim")
                son_sonuc = sistem.get("son_denetim_sonuc")
                if son_denetim:
                    st.caption("**" + t("envanter.son_denetim") + ":** " + son_denetim[:10])
                    if son_sonuc == "UYUMLU":
                        st.success("✅ " + son_sonuc)
                    elif son_sonuc == "UYUMSUZ":
                        st.error("❌ " + son_sonuc)
                    else:
                        st.info("ℹ️ " + (son_sonuc or "-"))
                else:
                    st.caption("**" + t("envanter.son_denetim") + ":** " + t("envanter.yapilmadi"))
            with col4:
                if st.button("🔍", key="denetle_" + str(sistem["id"]), help=t("envanter.denetle")):
                    st.session_state["envanter_denetle_id"] = sistem["id"]
                    st.session_state["envanter_denetle_tip"] = sistem.get("ai_tipi", "")
                    st.session_state["envanter_denetle_ad"] = sistem.get("sistem_adi", "")
                    st.switch_page("sayfa_tek.py")
                if st.button("🗑️", key="sil_" + str(sistem["id"]), help=t("envanter.sil")):
                    db.envanter_sil(sistem["id"])
                    st.rerun()
            st.markdown("---")
