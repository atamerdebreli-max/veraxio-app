"""
sayfa_annex_iv.py - Annex IV Teknik Dokumantasyon Olusturucu
AI Act Madde 11 + Ek IV kapsaminda 8 bolumlu teknik dokuman uretir.
"""
import streamlit as st
import auth
auth.giris_gerekli()

import db
from datetime import datetime


st.title("📄 Annex IV Teknik Dokümantasyon")
st.markdown("**AI Act Madde 11 + Ek IV kapsamında 8 bölümlük teknik doküman oluşturun.**")
st.markdown("---")

kullanici = auth.mevcut_kullanici()
firma_id = kullanici.get("firma_id") if kullanici else None


# ============================================================
# YENI DOKUMAN OLUSTUR
# ============================================================
st.subheader("📝 Yeni Doküman Oluştur")

# Envanterden sistem seç (varsa)
envanter = []
try:
    envanter = db.envanter_listele(firma_id=firma_id, sadece_aktif=True)
except Exception:
    pass

envanter_secenekleri = ["-- Manuel gir --"] + [e["sistem_adi"] for e in envanter]

col1, col2 = st.columns(2)
with col1:
    secili_sistem = st.selectbox("Envanterden Seç", envanter_secenekleri)
    sistem_adi = st.text_input("Sistem Adı *", value="" if secili_sistem == "-- Manuel gir --" else secili_sistem)
with col2:
    ai_tipi = st.selectbox("AI Tipi", [
        "Chatbot / AI Asistan", "Görsel Üretimi", "Metin Üretimi",
        "Duygu Tanıma", "Biyometrik", "Deepfake", "Diğer"
    ])
    versiyon = st.text_input("Versiyon", value="1.0")

st.markdown("---")
st.markdown("### 📋 8 Bölümü Doldurun")

# BOLUM 1
with st.expander("1️⃣ Sistem Tanımı (Madde 11/1-a)", expanded=True):
    sys_amac = st.text_area("Sistemin genel amacı", placeholder="Bu AI sistemi ne yapıyor?", height=80)
    sys_kullanici = st.text_input("Kullanıcı / hedef kitle", placeholder="Kim kullanıyor?")
    sys_etkilesim = st.text_area("Diğer sistemlerle etkileşim", height=60)

# BOLUM 2
with st.expander("2️⃣ Tasarım Seçimleri (Madde 11/1-b)", expanded=False):
    sys_mimari = st.text_area("Sistem mimarisi", placeholder="Model tipi, katman sayısı, vb.", height=80)
    sys_egitim = st.text_input("Eğitim verisi kaynağı")
    sys_donanim = st.text_input("Donanım gereksinimleri")

# BOLUM 3
with st.expander("3️⃣ Test Sonuçları (Madde 11/1-c)", expanded=False):
    sys_dogruluk = st.text_input("Doğruluk oranı", placeholder="%94")
    sys_yanlis_poz = st.text_input("Yanlış pozitif oranı", placeholder="%3")
    sys_test_verisi = st.text_input("Test verisi boyutu", placeholder="10.000 örnek")

# BOLUM 4
with st.expander("4️⃣ Risk Yönetimi (Madde 11/1-d)", expanded=False):
    sys_riskler = st.text_area("Tanımlanan riskler", placeholder="Her risk bir satırda", height=100)
    sys_onlemler = st.text_area("Alınan önlemler", height=80)

# BOLUM 5
with st.expander("5️⃣ Veri Yönetişimi (Madde 11/1-e)", expanded=False):
    sys_veri_kaynak = st.text_input("Veri kaynakları")
    sys_veri_kisisel = st.selectbox("Kişisel veri var mı?", ["Hayır", "Evet"])
    sys_veri_kvkk = st.text_input("KVKK/GDPR uyum durumu", placeholder="Uyumlu")

# BOLUM 6
with st.expander("6️⃣ Doğruluk, Sağlamlık, Siber Güvenlik (Madde 11/1-f)", expanded=False):
    sys_robustluk = st.text_area("Sağlamlık testleri", height=60)
    sys_siber = st.text_area("Siber güvenlik önlemleri", height=60)

# BOLUM 7
with st.expander("7️⃣ İnsan Gözetimi (Madde 11/1-g)", expanded=False):
    sys_insan_gozetim = st.text_area("İnsan gözetimi mekanizması", height=80)
    sys_insan_sorumlu = st.text_input("Sorumlu kişi / rol")

# BOLUM 8
with st.expander("8️⃣ Değişiklik Yönetimi (Madde 11/1-h)", expanded=False):
    sys_versiyon_politika = st.text_area("Versiyon değişiklik politikası", height=60)
    sys_izleme = st.text_area("Sürekli izleme planı", height=60)

st.markdown("---")

# ============================================================
# DOKUMAN OLUSTUR
# ============================================================
if st.button("📄 Annex IV Dokümanı Oluştur", type="primary", use_container_width=True):
    if not sistem_adi:
        st.error("Sistem Adı zorunludur.")
    else:
        icerik = {
            "1_sistem_tanimi": {
                "amac": sys_amac,
                "kullanici": sys_kullanici,
                "etkilesim": sys_etkilesim,
            },
            "2_tasarim": {
                "mimari": sys_mimari,
                "egitim_verisi": sys_egitim,
                "donanim": sys_donanim,
            },
            "3_test_sonuclari": {
                "dogruluk": sys_dogruluk,
                "yanlis_pozitif": sys_yanlis_poz,
                "test_verisi": sys_test_verisi,
            },
            "4_risk_yonetimi": {
                "riskler": sys_riskler,
                "onlemler": sys_onlemler,
            },
            "5_veri_yonetimi": {
                "kaynak": sys_veri_kaynak,
                "kisisel_veri": sys_veri_kisisel,
                "kvkk": sys_veri_kvkk,
            },
            "6_robustluk_siber": {
                "robustluk": sys_robustluk,
                "siber": sys_siber,
            },
            "7_insan_gozetimi": {
                "mekanizma": sys_insan_gozetim,
                "sorumlu": sys_insan_sorumlu,
            },
            "8_degisiklik_yonetimi": {
                "versiyon_politika": sys_versiyon_politika,
                "izleme": sys_izleme,
            },
        }

        try:
            dok_id = db.annex_iv_kaydet(
                firma_id=firma_id,
                sistem_adi=sistem_adi,
                ai_tipi=ai_tipi,
                versiyon=versiyon,
                icerik=icerik,
            )
            st.success("✅ Annex IV dokümanı oluşturuldu! (ID: " + str(dok_id) + ")")
            st.info("Sayfayı yenileyerek geçmiş dokümanları görebilirsiniz.")
        except Exception as e:
            st.error("Kayıt hatası: " + str(e))

# ============================================================
# GECMIS DOKUMANLAR
# ============================================================
st.markdown("---")
st.subheader("📚 Geçmiş Dokümanlar")

try:
    gecmis = db.annex_iv_listele(firma_id=firma_id)
except Exception:
    gecmis = []

if not gecmis:
    st.info("Henüz Annex IV dokümanı oluşturulmadı.")
else:
    for d in gecmis:
        with st.expander("📄 " + d.get("sistem_adi", "-") + " — v" + d.get("versiyon", "1.0")):
            st.caption("**Tarih:** " + (d.get("olusturma") or "-"))
            st.caption("**AI Tipi:** " + (d.get("ai_tipi") or "-"))
            col1, col2 = st.columns([4, 1])
            with col1:
                st.caption("Doküman ID: " + str(d.get("id")))
            with col2:
                if st.button("🗑️", key="annex_sil_" + str(d["id"])):
                    db.annex_iv_sil(d["id"])
                    st.rerun()
