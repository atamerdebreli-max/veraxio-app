"""
sayfa_envanter.py - AI Sistem Envanteri
Sirketin kullandigi tum AI sistemlerini tek yerde toplar.
"""
import streamlit as st
import auth
auth.giris_gerekli()

import db
from i18n import t
from datetime import datetime


st.title("📋 AI Envanterim")
st.markdown("**Şirketinizdeki tüm AI sistemlerini tek yerde yönetin.**")
st.markdown("---")

# Kullanici ve firma bilgisi
kullanici = auth.mevcut_kullanici()
firma_id = kullanici.get("firma_id") if kullanici else None

# ============================================================
# ISTATISTIK
# ============================================================
try:
    ist = db.envanter_istatistik(firma_id)
    col1, col2, col3 = st.columns(3)
    col1.metric("Toplam AI Sistemi", ist["toplam"])
    col2.metric("Riskli (Yüksek/Kritik)", ist["riskli"])
    col3.metric("Denetlenmiş", ist["denetlenmis"])
    st.markdown("---")
except Exception as e:
    st.warning("İstatistik yüklenemedi: " + str(e))

# ============================================================
# YENI SISTEM EKLEME FORMU
# ============================================================
with st.expander("➕ Yeni AI Sistemi Ekle", expanded=False):
    with st.form("envanter_ekle_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            sistem_adi = st.text_input("Sistem Adı *", placeholder="Örn: Müşteri Destek Chatbot")
            ai_tipi = st.selectbox("AI Tipi *", [
                "Chatbot / AI Asistan",
                "Görsel Üretimi (C2PA)",
                "Metin Denetimi (AI Tespiti)",
                "KVKK Uyum Denetimi",
                "AB Temsilcisi Kontrolü",
                "Shadow AI Taraması",
                "Kümülatif Yükümlülük Analizi",
                "Duygu Tanıma (Müşteri Tarafı)",
                "Duygu Tanıma (Çalışan Tarafı)",
                "Biyometrik Sınıflandırma",
                "Deepfake İçerik",
                "Kamu Yararı Metni",
                "Diğer",
            ])
            departman = st.text_input("Departman", placeholder="Örn: Pazarlama")
        with col2:
            sorumlu_kisi = st.text_input("Sorumlu Kişi", placeholder="Örn: Ahmet Yılmaz")
            amac = st.text_area("Kullanım Amacı", placeholder="Bu AI ne için kullanılıyor?", height=80)
            risk_seviyesi = st.selectbox("Risk Seviyesi", [
                "bilinmiyor", "minimal", "sinirli", "yuksek", "kritik"
            ])
        notlar = st.text_area("Notlar (opsiyonel)", height=60)

        submitted = st.form_submit_button("💾 Kaydet", type="primary", use_container_width=True)
        if submitted:
            if not sistem_adi:
                st.error("Sistem Adı zorunludur.")
            else:
                try:
                    db.envanter_ekle(
                        firma_id=firma_id,
                        sistem_adi=sistem_adi,
                        ai_tipi=ai_tipi,
                        departman=departman,
                        sorumlu_kisi=sorumlu_kisi,
                        amac=amac,
                        risk_seviyesi=risk_seviyesi,
                        notlar=notlar,
                    )
                    st.success("✅ Sistem eklendi: " + sistem_adi)
                    st.rerun()
                except Exception as e:
                    st.error("Kayıt hatası: " + str(e))

# ============================================================
# ENVANTER LISTESI
# ============================================================
st.subheader("📊 Sistem Listesi")

try:
    envanter = db.envanter_listele(firma_id=firma_id, sadece_aktif=True)
except Exception as e:
    st.error("Liste yüklenemedi: " + str(e))
    envanter = []

if not envanter:
    st.info("Henüz AI sistemi eklenmemiş. Yukarıdaki **➕ Yeni AI Sistemi Ekle** butonuna basarak başlayın.")
else:
    for sistem in envanter:
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            with col1:
                st.markdown("### " + sistem["sistem_adi"])
                st.caption("🏢 " + (sistem.get("departman") or "-") + " · 👤 " + (sistem.get("sorumlu_kisi") or "-"))
            with col2:
                st.caption("**AI Tipi:** " + (sistem.get("ai_tipi") or "-"))
                risk = sistem.get("risk_seviyesi", "bilinmiyor")
                if risk in ("yuksek", "kritik"):
                    st.error("🔴 Risk: " + risk.upper())
                elif risk == "sinirli":
                    st.warning("🟡 Risk: " + risk.upper())
                elif risk == "minimal":
                    st.success("🟢 Risk: " + risk.upper())
                else:
                    st.info("⚪ Risk: " + risk.upper())
            with col3:
                son_denetim = sistem.get("son_denetim")
                son_sonuc = sistem.get("son_denetim_sonuc")
                if son_denetim:
                    st.caption("**Son Denetim:** " + son_denetim[:10])
                    if son_sonuc == "UYUMLU":
                        st.success("✅ " + son_sonuc)
                    elif son_sonuc == "UYUMSUZ":
                        st.error("❌ " + son_sonuc)
                    else:
                        st.info("ℹ️ " + (son_sonuc or "-"))
                else:
                    st.caption("**Son Denetim:** Henüz yapılmadı")
                        with col4:
                if st.button("🔍", key="denetle_" + str(sistem["id"]), help="Denetle"):
                    st.session_state["envanter_denetle_id"] = sistem["id"]
                    st.session_state["envanter_denetle_tip"] = sistem.get("ai_tipi", "")
                    st.switch_page("sayfa_tek.py")
                if st.button("🗑️", key="sil_" + str(sistem["id"]), help="Sil"):
                    db.envanter_sil(sistem["id"])
                    st.rerun()
            st.markdown("---")
