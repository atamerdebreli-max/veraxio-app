"""
sayfa_risk.py - AI Act Risk Siniflandirma Sihirbazi
Kullanicinin AI sistemini AI Act'e gore siniflandirir.
"""
import streamlit as st
import auth
auth.giris_gerekli()

import db
from datetime import datetime


st.title("🎯 Risk Sınıflandırma Sihirbazı")
st.markdown("**AI sisteminizin AI Act'e göre risk seviyesini belirleyin.**")
st.markdown("---")

kullanici = auth.mevcut_kullanici()
firma_id = kullanici.get("firma_id") if kullanici else None

# ============================================================
# SIHIRBAZ FORMU
# ============================================================
st.subheader("📝 Sistem Bilgileri")

col1, col2 = st.columns(2)
with col1:
    sistem_adi = st.text_input("Sistem Adı *", placeholder="Örn: Müşteri Destek Chatbot")
with col2:
    ai_tipi = st.selectbox("AI Tipi", [
        "Chatbot / AI Asistan",
        "Görsel Üretimi",
        "Metin Üretimi",
        "Duygu Tanıma",
        "Biyometrik Sınıflandırma",
        "Deepfake İçerik",
        "Kamu Yararı Metni",
        "Diğer",
    ])

st.markdown("---")
st.subheader("❓ Değerlendirme Soruları")

# YASAK KONTROLU (Madde 5)
st.markdown("##### 🚫 Yasak Kullanım Kontrolü (Madde 5)")
yasak_sosyal_skor = st.checkbox("Sosyal skorlama / genel amaçlı vatandaş puanlama yapıyor mu?")
yasak_manipulasyon = st.checkbox("İnsan davranışını bilinçaltı manipüle ediyor mu?")
yasak_savunmasiz = st.checkbox("Yaş, engellilik nedeniyle savunmasız grupları hedefliyor mu?")
yasak_biyometrik_uzak = st.checkbox("Uzak biyometrik tanımlama (kamuya açık alan) yapıyor mu?")
yasak_duygu_isyeri = st.checkbox("İş yerinde çalışan duygularını analiz ediyor mu?")
yasak_kategori = st.checkbox("Irk, siyasi görüş, din, cinsel yönelim sınıflandırması yapıyor mu?")

# YUKSEK RISK KONTROLU (Madde 6 + Ek III)
st.markdown("##### ⚠️ Yüksek Risk Kontrolü (Madde 6 + Ek III)")
yuksek_kritik_altyapi = st.checkbox("Kritik altyapı (enerji, su, ulaşım) yönetimi?")
yuksek_egitim = st.checkbox("Eğitim / sınav değerlendirmesi?")
yuksek_istihdam = st.checkbox("İşe alım / terfi / işten çıkarma kararı?")
yuksek_kredi = st.checkbox("Kredi skorlama / kredi kararı?")
yuksek_saglik = st.checkbox("Sağlık teşhis / tedavi kararı?")
yuksek_hukuk = st.checkbox("Hukuki karar / yargı desteği?")
yuksek_goc = st.checkbox("Göç / sığınma / vize kararı?")
yuksek_biyometrik = st.checkbox("Biyometrik tanımlama / doğrulama?")

# SINIRLI RISK (Madde 50)
st.markdown("##### 📢 Sınırlı Risk / Şeffaflık (Madde 50)")
sinirli_chatbot = st.checkbox("Kullanıcı ile doğrudan etkileşim (chatbot)?")
sinirli_icerik = st.checkbox("AI üretimi içerik (metin, görsel, ses, video)?")
sinirli_deepfake = st.checkbox("Deepfake / sentetik medya üretimi?")
sinirli_duygu = st.checkbox("Duygu tanıma / biyometrik kategorizasyon?")

# KAPSAM
st.markdown("##### 🌍 Coğrafi Kapsam")
kapsam_ab = st.checkbox("AB'de kullanıcı / müşteri / ofis var mı?")

st.markdown("---")

# ============================================================
# DEGERLENDIR
# ============================================================
if st.button("🎯 Risk Seviyesini Belirle", type="primary", use_container_width=True):
    if not sistem_adi:
        st.error("Sistem Adı zorunludur.")
    else:
        # YASAK kontrolu
        yasak_listesi = []
        if yasak_sosyal_skor: yasak_listesi.append("Sosyal skorlama (Madde 5(1)(c))")
        if yasak_manipulasyon: yasak_listesi.append("Bilinçaltı manipülasyon (Madde 5(1)(a))")
        if yasak_savunmasiz: yasak_listesi.append("Savunmasız grup hedefleme (Madde 5(1)(b))")
        if yasak_biyometrik_uzak: yasak_listesi.append("Uzak biyometrik tanımlama (Madde 5(1)(h))")
        if yasak_duygu_isyeri: yasak_listesi.append("İş yeri duygu analizi (Madde 5(1)(f))")
        if yasak_kategori: yasak_listesi.append("Hassas kategori sınıflandırma (Madde 5(1)(g))")

        # YUKSEK RISK kontrolu
        yuksek_listesi = []
        if yuksek_kritik_altyapi: yuksek_listesi.append("Kritik altyapı (Ek III/2)")
        if yuksek_egitim: yuksek_listesi.append("Eğitim (Ek III/3)")
        if yuksek_istihdam: yuksek_listesi.append("İstihdam (Ek III/4)")
        if yuksek_kredi: yuksek_listesi.append("Kredi skorlama (Ek III/5b)")
        if yuksek_saglik: yuksek_listesi.append("Sağlık (Ek III/5c)")
        if yuksek_hukuk: yuksek_listesi.append("Hukuk (Ek III/8)")
        if yuksek_goc: yuksek_listesi.append("Göç (Ek III/7)")
        if yuksek_biyometrik: yuksek_listesi.append("Biyometrik tanımlama (Ek III/1)")

        # SINIRLI RISK
        sinirli_listesi = []
        if sinirli_chatbot: sinirli_listesi.append("Chatbot şeffaflığı (Madde 50(1))")
        if sinirli_icerik: sinirli_listesi.append("AI içerik işaretleme (Madde 50(2))")
        if sinirli_deepfake: sinirli_listesi.append("Deepfake bildirimi (Madde 50(4))")
        if sinirli_duygu: sinirli_listesi.append("Duygu tanıma bildirimi (Madde 50(3))")

        # KARAR MANTIGI
        if yasak_listesi:
            risk_seviyesi = "YASAK"
            gerekce = "AI Act Madde 5 kapsamında yasaklı kullanım tespit edildi."
            yukumlulukler = yasak_listesi
            renk = "error"
        elif yuksek_listesi:
            risk_seviyesi = "YUKSEK"
            gerekce = "AI Act Madde 6 + Ek III kapsamında yüksek riskli AI sistemi."
            yukumlulukler = yuksek_listesi + [
                "Risk yönetim sistemi kur (Madde 9)",
                "Veri yönetişimi (Madde 10)",
                "Teknik dokümantasyon (Madde 11)",
                "Kayıt tutma (Madde 12)",
                "Şeffaflık ve kullanıcı bilgilendirme (Madde 13)",
                "İnsan gözetimi (Madde 14)",
                "Doğruluk, sağlamlık, siber güvenlik (Madde 15)",
            ]
            renk = "warning"
        elif sinirli_listesi:
            risk_seviyesi = "SINIRLI"
            gerekce = "AI Act Madde 50 kapsamında şeffaflık yükümlülüğü olan AI sistemi."
            yukumlulukler = sinirli_listesi
            renk = "info"
        else:
            risk_seviyesi = "MINIMAL"
            gerekce = "AI Act kapsamında özel yükümlülük tespit edilmedi."
            yukumlulukler = ["Gönüllü etik kurallar önerilir."]
            renk = "success"

        # Kaydet
        try:
            db.risk_kaydet(
                firma_id=firma_id,
                sistem_adi=sistem_adi,
                ai_tipi=ai_tipi,
                cevaplar={
                    "yasak": yasak_listesi,
                    "yuksek": yuksek_listesi,
                    "sinirli": sinirli_listesi,
                    "kapsam_ab": kapsam_ab,
                },
                risk_seviyesi=risk_seviyesi,
                gerekce=gerekce,
                yukumlulukler=yukumlulukler,
            )
        except Exception as e:
            st.warning("Kayıt hatası: " + str(e))

        # Sonucu goster
        st.markdown("---")
        st.subheader("📊 Risk Değerlendirme Sonucu")

        if risk_seviyesi == "YASAK":
            st.error("## 🚫 RİSK SEVİYESİ: YASAK")
            st.error("**Bu AI sistemi AI Act Madde 5 kapsamında YASAKTIR. Derhal durdurulmalıdır.**")
        elif risk_seviyesi == "YUKSEK":
            st.warning("## ⚠️ RİSK SEVİYESİ: YÜKSEK")
            st.warning("**Bu AI sistemi AI Act Madde 6 + Ek III kapsamında YÜKSEK RİSKLİDİR. Ağır yükümlülükler vardır.**")
        elif risk_seviyesi == "SINIRLI":
            st.info("## 📢 RİSK SEVİYESİ: SINIRLI")
            st.info("**Bu AI sistemi AI Act Madde 50 kapsamında şeffaflık yükümlülüğüne tabidir.**")
        else:
            st.success("## ✅ RİSK SEVİYESİ: MİNİMAL")
            st.success("**Bu AI sistemi AI Act kapsamında özel yükümlülük gerektirmez.**")

        st.markdown("### 📋 Gerekçe")
        st.write(gerekce)

        st.markdown("### 📌 Uygulanacak Yükümlülükler")
        for y in yukumlulukler:
            st.markdown("- " + y)

        # CTA
        st.markdown("---")
        st.markdown("### 🔍 Sonraki Adım")
        st.info("Şimdi bu sistem için detaylı denetim yapabilirsiniz.")
        if st.button("🔍 Detaylı Denetime Git", type="primary", use_container_width=True, key="risk_denetime_git"):
            st.session_state["envanter_denetle_tip"] = ai_tipi
            st.session_state["envanter_denetle_ad"] = sistem_adi
            st.switch_page("sayfa_tek.py")

# ============================================================
# GECMIS DEGERLENDIRMELER
# ============================================================
st.markdown("---")
st.subheader("📜 Geçmiş Değerlendirmeler")

try:
    gecmis = db.risk_listele(firma_id=firma_id)
except Exception:
    gecmis = []

if not gecmis:
    st.info("Henüz risk değerlendirmesi yapılmadı.")
else:
    for r in gecmis:
        risk = r.get("risk_seviyesi", "-")
        emoji = {"YASAK": "🚫", "YUKSEK": "⚠️", "SINIRLI": "📢", "MINIMAL": "✅"}.get(risk, "⚪")
        with st.expander(f"{emoji} {r.get('sistem_adi', '-')} — {risk}"):
            st.caption("**Tarih:** " + (r.get("olusturma") or "-"))
            st.caption("**AI Tipi:** " + (r.get("ai_tipi") or "-"))
            st.write("**Gerekçe:** " + (r.get("gerekce") or "-"))
