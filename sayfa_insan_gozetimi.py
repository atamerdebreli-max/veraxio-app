"""
sayfa_insan_gozetimi.py - Insan Gozetimi Is Akisi
AI Act Madde 14 - Yuksek riskli AI sistemleri icin insan onay mekanizmasi.
"""
import streamlit as st
import auth
auth.giris_gerekli()

import db
from datetime import datetime


st.title("👁️ İnsan Gözetimi")
st.markdown("**AI Act Madde 14 — Yüksek riskli AI kararlarında insan onayı mekanizması.**")
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
    col1.metric("Toplam Karar", ist["toplam"])
    col2.metric("Bekleyen", ist["bekleyen"])
    col3.metric("Onaylandı", ist["onaylandi"])
    col4.metric("Reddedildi", ist["reddedildi"])
    st.markdown("---")
except Exception as e:
    st.warning("İstatistik yüklenemedi: " + str(e))

# ============================================================
# YENI KARAR EKLE
# ============================================================
with st.expander("➕ Yeni AI Kararı Ekle (Onay Bekleyecek)", expanded=False):
    with st.form("gozetim_ekle_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            sistem_adi = st.text_input("Sistem Adı *", placeholder="Örn: Kredi Skorlama Modeli")
            ai_tipi = st.selectbox("AI Tipi", [
                "Chatbot / AI Asistan", "Kredi Skorlama", "İşe Alım",
                "Sağlık Teşhis", "Biyometrik", "Diğer"
            ])
        with col2:
            risk_seviyesi = st.selectbox("Risk Seviyesi", ["yuksek", "kritik", "sinirli"])

        karar_ozeti = st.text_area("AI Karar Özeti *", placeholder="AI ne karar verdi?", height=80)
        ai_onerisi = st.text_area("AI'nın Önerisi", placeholder="AI ne öneriyor? (Onayla/Reddet/İncele)", height=60)

        if st.form_submit_button("💾 Kaydet", type="primary", use_container_width=True):
            if not sistem_adi or not karar_ozeti:
                st.error("Sistem Adı ve Karar Özeti zorunludur.")
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
                    st.success("✅ Karar eklendi, onay bekliyor.")
                    st.rerun()
                except Exception as e:
                    st.error("Kayıt hatası: " + str(e))

# ============================================================
# BEKLEYEN KARARLAR
# ============================================================
st.subheader("⏳ Onay Bekleyen Kararlar")

try:
    bekleyen = db.gozetim_listele(firma_id=firma_id, durum="bekliyor")
except Exception:
    bekleyen = []

if not bekleyen:
    st.info("Onay bekleyen karar yok.")
else:
    for k in bekleyen:
        with st.container():
            col1, col2 = st.columns([3, 2])
            with col1:
                st.markdown("### " + k.get("sistem_adi", "-"))
                st.caption("AI Tipi: " + (k.get("ai_tipi") or "-") + " · Risk: " + (k.get("risk_seviyesi") or "-").upper())
                st.write("**Karar Özeti:** " + (k.get("karar_ozeti") or "-"))
                if k.get("ai_onerisi"):
                    st.info("🤖 AI Önerisi: " + k["ai_onerisi"])
            with col2:
                st.caption("**Tarih:** " + (k.get("olusturma") or "-"))

                karar_notu = st.text_input("Not (opsiyonel)", key="not_" + str(k["id"]))

                btn1, btn2, btn3 = st.columns(3)
                with btn1:
                    if st.button("✅ Onayla", key="onay_" + str(k["id"]), use_container_width=True):
                        db.gozetim_karar(k["id"], "onaylandi", kullanici_adi, karar_notu)
                        st.rerun()
                with btn2:
                    if st.button("❌ Reddet", key="red_" + str(k["id"]), use_container_width=True):
                        db.gozetim_karar(k["id"], "reddedildi", kullanici_adi, karar_notu)
                        st.rerun()
                with btn3:
                    if st.button("🔍 İncele", key="incele_" + str(k["id"]), use_container_width=True):
                        db.gozetim_karar(k["id"], "inceleniyor", kullanici_adi, karar_notu)
                        st.rerun()
            st.markdown("---")

# ============================================================
# KARAR GECMISI
# ============================================================
st.subheader("📜 Karar Geçmişi")

try:
    gecmis = db.gozetim_listele(firma_id=firma_id)
    gecmis = [g for g in gecmis if g.get("durum") != "bekliyor"]
except Exception:
    gecmis = []

if not gecmis:
    st.info("Henüz karara bağlanmış kayıt yok.")
else:
    for g in gecmis:
        durum = g.get("durum", "-")
        emoji = {"onaylandi": "✅", "reddedildi": "❌", "inceleniyor": "🔍"}.get(durum, "⚪")
        with st.expander(f"{emoji} {g.get('sistem_adi', '-')} — {durum.upper()}"):
            st.caption("**Karar Tarihi:** " + (g.get("karar_tarih") or "-"))
            st.caption("**Onaylayan:** " + (g.get("onaylayan") or "-"))
            st.write("**Karar Özeti:** " + (g.get("karar_ozeti") or "-"))
            if g.get("karar_notu"):
                st.write("**Not:** " + g["karar_notu"])
            col1, col2 = st.columns([4, 1])
            with col2:
                if st.button("🗑️", key="sil_" + str(g["id"])):
                    db.gozetim_sil(g["id"])
                    st.rerun()
