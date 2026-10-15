"""
sayfa_risk.py - AI Act Risk Siniflandirma Sihirbazi
"""
import streamlit as st
import auth
auth.giris_gerekli()

import db
from i18n import t


st.title("🎯 " + t("risk.baslik"))
st.markdown("**" + t("risk.alt_baslik") + "**")
st.markdown("---")

kullanici = auth.mevcut_kullanici()
firma_id = kullanici.get("firma_id") if kullanici else None

# ============================================================
# SIHIRBAZ FORMU
# ============================================================
st.subheader(t("risk.sistem_bilgi"))

col1, col2 = st.columns(2)
with col1:
    sistem_adi = st.text_input(t("risk.sistem_adi") + " *", placeholder=t("risk.sistem_adi_placeholder"))
with col2:
    ai_tipi = st.selectbox(t("risk.ai_tipi"), [
        t("ai_tipleri.chatbot"), t("ai_tipleri.gorsel"), t("ai_tipleri.metin"),
        t("ai_tipleri.duygu_musteri"), t("ai_tipleri.biyometrik"),
        t("ai_tipleri.deepfake"), t("ai_tipleri.kamu_metni"), "Diğer",
    ])

st.markdown("---")
st.subheader(t("risk.degerlendirme"))

# YASAK KONTROLU (Madde 5)
st.markdown("##### " + t("risk.yasak_baslik"))
yasak_sosyal_skor = st.checkbox(t("risk.yasak_sosyal"))
yasak_manipulasyon = st.checkbox(t("risk.yasak_manipulasyon"))
yasak_savunmasiz = st.checkbox(t("risk.yasak_savunmasiz"))
yasak_biyometrik_uzak = st.checkbox(t("risk.yasak_biyometrik"))
yasak_duygu_isyeri = st.checkbox(t("risk.yasak_duygu_isyeri"))
yasak_kategori = st.checkbox(t("risk.yasak_kategori"))

# YUKSEK RISK KONTROLU (Madde 6 + Ek III)
st.markdown("##### " + t("risk.yuksek_baslik"))
yuksek_kritik_altyapi = st.checkbox(t("risk.yuksek_kritik"))
yuksek_egitim = st.checkbox(t("risk.yuksek_egitim"))
yuksek_istihdam = st.checkbox(t("risk.yuksek_istihdam"))
yuksek_kredi = st.checkbox(t("risk.yuksek_kredi"))
yuksek_saglik = st.checkbox(t("risk.yuksek_saglik"))
yuksek_hukuk = st.checkbox(t("risk.yuksek_hukuk"))
yuksek_goc = st.checkbox(t("risk.yuksek_goc"))
yuksek_biyometrik = st.checkbox(t("risk.yuksek_biyometrik"))

# SINIRLI RISK (Madde 50)
st.markdown("##### " + t("risk.sinirli_baslik"))
sinirli_chatbot = st.checkbox(t("risk.sinirli_chatbot"))
sinirli_icerik = st.checkbox(t("risk.sinirli_icerik"))
sinirli_deepfake = st.checkbox(t("risk.sinirli_deepfake"))
sinirli_duygu = st.checkbox(t("risk.sinirli_duygu"))

# KAPSAM
st.markdown("##### " + t("risk.kapsam_baslik"))
kapsam_ab = st.checkbox(t("risk.kapsam_ab"))

st.markdown("---")

# ============================================================
# DEGERLENDIR
# ============================================================
if st.button(t("risk.belirle_btn"), type="primary", use_container_width=True):
    if not sistem_adi:
        st.error(t("risk.sistem_zorunlu"))
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
        elif sinirli_listesi:
            risk_seviyesi = "SINIRLI"
            gerekce = "AI Act Madde 50 kapsamında şeffaflık yükümlülüğü olan AI sistemi."
            yukumlulukler = sinirli_listesi
        else:
            risk_seviyesi = "MINIMAL"
            gerekce = "AI Act kapsamında özel yükümlülük tespit edilmedi."
            yukumlulukler = ["Gönüllü etik kurallar önerilir."]

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
            st.warning(t("risk.kayit_hatasi") + str(e))

        # Sonucu goster
        st.markdown("---")
        st.subheader(t("risk.sonuc_baslik"))

        if risk_seviyesi == "YASAK":
            st.error("## 🚫 " + t("risk.yasak") + ": " + t("risk.yasak"))
            st.error("**Bu AI sistemi AI Act Madde 5 kapsamında YASAKTIR. Derhal durdurulmalıdır.**")
        elif risk_seviyesi == "YUKSEK":
            st.warning("## ⚠️ " + t("risk.yuksek"))
            st.warning("**Bu AI sistemi AI Act Madde 6 + Ek III kapsamında YÜKSEK RİSKLİDİR. Ağır yükümlülükler vardır.**")
        elif risk_seviyesi == "SINIRLI":
            st.info("## 📢 " + t("risk.sinirli"))
            st.info("**Bu AI sistemi AI Act Madde 50 kapsamında şeffaflık yükümlülüğüne tabidir.**")
        else:
            st.success("## ✅ " + t("risk.minimal"))
            st.success("**Bu AI sistemi AI Act kapsamında özel yükümlülük gerektirmez.**")

        st.markdown("### " + t("risk.gerekce"))
        st.write(gerekce)

        st.markdown("### " + t("risk.yukumlulukler"))
        for y in yukumlulukler:
            st.markdown("- " + y)

        # CTA
        st.markdown("---")
        st.markdown("### " + t("risk.sonraki_adim"))
        st.info(t("risk.sonraki_aciklama"))
        if st.button(t("risk.denetime_git"), type="primary", use_container_width=True, key="risk_denetime_git"):
            st.session_state["envanter_denetle_tip"] = ai_tipi
            st.session_state["envanter_denetle_ad"] = sistem_adi
            st.switch_page("sayfa_tek.py")

# ============================================================
# GECMIS DEGERLENDIRMELER
# ============================================================
st.markdown("---")
st.subheader(t("risk.gecmis_baslik"))

try:
    gecmis = db.risk_listele(firma_id=firma_id)
except Exception:
    gecmis = []

if not gecmis:
    st.info(t("risk.gecmis_bos"))
else:
    for r in gecmis:
        risk = r.get("risk_seviyesi", "-")
        emoji = {"YASAK": "🚫", "YUKSEK": "⚠️", "SINIRLI": "📢", "MINIMAL": "✅"}.get(risk, "⚪")
        with st.expander(f"{emoji} {r.get('sistem_adi', '-')} — {risk}"):
            st.caption("**" + t("genel.tarih") + ":** " + (r.get("olusturma") or "-"))
            st.caption("**" + t("risk.ai_tipi") + ":** " + (r.get("ai_tipi") or "-"))
            st.write("**" + t("risk.gerekce") + ":** " + (r.get("gerekce") or "-"))
