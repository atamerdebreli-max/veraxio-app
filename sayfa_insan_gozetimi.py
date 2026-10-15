"""
sayfa_insan_gozetimi.py - Insan Gozetimi Is Akisi
"""
import streamlit as st
import auth
auth.giris_gerekli()

import db
from i18n import t


st.title("👁️ " + t("gozetim.baslik"))
st.markdown("**" + t("gozetim.alt_baslik") + "**")
st.markdown("---")

kullanici = auth.mevcut_kullanici()
firma_id = kullanici.get("firma_id") if kullanici else None
kullanici_adi = kullanici.get("kullanici_adi") if kullanici else "?"

# ============================================================
# ISTATISTIK
# ============================================================
try:
    ist = db.gozetim_istatistik(firma_id)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(t("gozetim.toplam"), ist["toplam"])
    col2.metric(t("gozetim.bekleyen"), ist["bekleyen"])
    col3.metric(t("gozetim.onaylandi"), ist["onaylandi"])
    col4.metric(t("gozetim.reddedildi"), ist["reddedildi"])
    st.markdown("---")
except Exception as e:
    st.warning(t("gozetim.kayit_hatasi") + str(e))

# ============================================================
# YENI KARAR EKLE
# ============================================================
with st.expander(t("gozetim.yeni_karar"), expanded=False):
    with st.form("gozetim_ekle_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            sistem_adi = st.text_input(t("gozetim.sistem_adi") + " *", placeholder=t("gozetim.sistem_placeholder"))
            ai_tipi = st.selectbox(t("gozetim.ai_tipi"), [
                t("ai_tipleri.chatbot"), t("ai_tipleri.metin"), t("ai_tipleri.gorsel"),
                t("ai_tipleri.biyometrik"), t("ai_tipleri.deepfake"), "Diğer",
            ])
        with col2:
            risk_seviyesi = st.selectbox(t("gozetim.risk_seviyesi"), ["yuksek", "kritik", "sinirli"])

        karar_ozeti = st.text_area(t("gozetim.karar_ozeti") + " *", placeholder=t("gozetim.karar_placeholder"), height=80)
        ai_onerisi = st.text_area(t("gozetim.ai_onerisi"), placeholder=t("gozetim.oneri_placeholder"), height=60)

        if st.form_submit_button(t("gozetim.kaydet"), type="primary", use_container_width=True):
            if not sistem_adi or not karar_ozeti:
                st.error(t("gozetim.zorunlu"))
            else:
                try:
                    db.gozetim_kaydet(
                        firma_id=firma_id,
                        sistem_adi=sistem_adi,
                        ai_tipi=ai_tipi,
                        karar_ozeti=karar_ozeti,
                        ai_onerisi=ai_onerisi,
                        risk_seviyesi=risk_seviyesi,
                    )
                    st.success("✅ OK")
                    st.rerun()
                except Exception as e:
                    st.error(t("gozetim.kayit_hatasi") + str(e))

# ============================================================
# BEKLEYEN KARARLAR
# ============================================================
st.subheader(t("gozetim.bekleyen_baslik"))

try:
    bekleyen = db.gozetim_listele(firma_id=firma_id, durum="bekliyor")
except Exception:
    bekleyen = []

if not bekleyen:
    st.info(t("gozetim.bekleyen_bos"))
else:
    for k in bekleyen:
        with st.container():
            col1, col2 = st.columns([3, 2])
            with col1:
                st.markdown("### " + k.get("sistem_adi", "-"))
                st.caption(t("gozetim.ai_tipi") + ": " + (k.get("ai_tipi") or "-") + " · " + t("gozetim.risk_seviyesi") + ": " + (k.get("risk_seviyesi") or "-").upper())
                st.write("**" + t("gozetim.karar_ozeti_label") + ":** " + (k.get("karar_ozeti") or "-"))
                if k.get("ai_onerisi"):
                    st.info(t("gozetim.ai_onerisi_label") + ": " + k["ai_onerisi"])
            with col2:
                st.caption("**" + t("gozetim.tarih") + ":** " + (k.get("olusturma") or "-"))

                karar_notu = st.text_input(t("gozetim.not"), key="not_" + str(k["id"]))

                btn1, btn2, btn3 = st.columns(3)
                with btn1:
                    if st.button(t("gozetim.onayla"), key="onay_" + str(k["id"]), use_container_width=True):
                        db.gozetim_karar(k["id"], "onaylandi", kullanici_adi, karar_notu)
                        st.rerun()
                with btn2:
                    if st.button(t("gozetim.reddet"), key="red_" + str(k["id"]), use_container_width=True):
                        db.gozetim_karar(k["id"], "reddedildi", kullanici_adi, karar_notu)
                        st.rerun()
                with btn3:
                    if st.button(t("gozetim.incele"), key="incele_" + str(k["id"]), use_container_width=True):
                        db.gozetim_karar(k["id"], "inceleniyor", kullanici_adi, karar_notu)
                        st.rerun()
            st.markdown("---")

# ============================================================
# KARAR GECMISI
# ============================================================
st.subheader(t("gozetim.gecmis_baslik"))

try:
    gecmis = db.gozetim_listele(firma_id=firma_id)
    gecmis = [g for g in gecmis if g.get("durum") != "bekliyor"]
except Exception:
    gecmis = []

if not gecmis:
    st.info(t("gozetim.gecmis_bos"))
else:
    for g in gecmis:
        durum = g.get("durum", "-")
        emoji = {"onaylandi": "✅", "reddedildi": "❌", "inceleniyor": "🔍"}.get(durum, "⚪")
        with st.expander(f"{emoji} {g.get('sistem_adi', '-')} — {durum.upper()}"):
            st.caption("**" + t("gozetim.karar_tarih") + ":** " + (g.get("karar_tarih") or "-"))
            st.caption("**" + t("gozetim.onaylayan") + ":** " + (g.get("onaylayan") or "-"))
            st.write("**" + t("gozetim.karar_ozeti_label") + ":** " + (g.get("karar_ozeti") or "-"))
            if g.get("karar_notu"):
                st.write("**" + t("gozetim.not") + ":** " + g["karar_notu"])
            col1, col2 = st.columns([4, 1])
            with col2:
                if st.button("🗑️", key="sil_" + str(g["id"])):
                    db.gozetim_sil(g["id"])
                    st.rerun()
