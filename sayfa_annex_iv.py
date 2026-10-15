"""
sayfa_annex_iv.py - Annex IV Teknik Dokumantasyon Olusturucu
"""
import streamlit as st
import auth
auth.giris_gerekli()

import db
from i18n import t


st.title("📄 " + t("annex.baslik"))
st.markdown("**" + t("annex.alt_baslik") + "**")
st.markdown("---")

kullanici = auth.mevcut_kullanici()
firma_id = kullanici.get("firma_id") if kullanici else None


# ============================================================
# YENI DOKUMAN OLUSTUR
# ============================================================
st.subheader(t("annex.yeni_dokuman"))

# Envanterden sistem sec
envanter = []
try:
    envanter = db.envanter_listele(firma_id=firma_id, sadece_aktif=True)
except Exception:
    pass

envanter_secenekleri = [t("annex.manuel_gir")] + [e["sistem_adi"] for e in envanter]

col1, col2 = st.columns(2)
with col1:
    secili_sistem = st.selectbox(t("annex.envanterden_sec"), envanter_secenekleri)
    varsayilan_ad = "" if secili_sistem == t("annex.manuel_gir") else secili_sistem
    sistem_adi = st.text_input(t("annex.sistem_adi") + " *", value=varsayilan_ad)
with col2:
    ai_tipi = st.selectbox(t("annex.ai_tipi"), [
        t("ai_tipleri.chatbot"), t("ai_tipleri.gorsel"), t("ai_tipleri.metin"),
        t("ai_tipleri.duygu_musteri"), t("ai_tipleri.biyometrik"),
        t("ai_tipleri.deepfake"), t("ai_tipleri.kamu_metni"), "Diğer",
    ])
    versiyon = st.text_input(t("annex.versiyon"), value="1.0")

st.markdown("---")
st.markdown("### " + t("annex.bolumler"))

# BOLUM 1
with st.expander(t("annex.b1_baslik"), expanded=True):
    sys_amac = st.text_area(t("annex.b1_amac"), height=80)
    sys_kullanici = st.text_input(t("annex.b1_kullanici"))
    sys_etkilesim = st.text_area(t("annex.b1_etkilesim"), height=60)

# BOLUM 2
with st.expander(t("annex.b2_baslik"), expanded=False):
    sys_mimari = st.text_area(t("annex.b2_mimari"), height=80)
    sys_egitim = st.text_input(t("annex.b2_egitim"))
    sys_donanim = st.text_input(t("annex.b2_donanim"))

# BOLUM 3
with st.expander(t("annex.b3_baslik"), expanded=False):
    sys_dogruluk = st.text_input(t("annex.b3_dogruluk"))
    sys_yanlis_poz = st.text_input(t("annex.b3_yanlis_poz"))
    sys_test_verisi = st.text_input(t("annex.b3_test_verisi"))

# BOLUM 4
with st.expander(t("annex.b4_baslik"), expanded=False):
    sys_riskler = st.text_area(t("annex.b4_riskler"), height=100)
    sys_onlemler = st.text_area(t("annex.b4_onlemler"), height=80)

# BOLUM 5
with st.expander(t("annex.b5_baslik"), expanded=False):
    sys_veri_kaynak = st.text_input(t("annex.b5_kaynak"))
    sys_veri_kisisel = st.selectbox(t("annex.b5_kisisel"), ["Hayır", "Evet"])
    sys_veri_kvkk = st.text_input(t("annex.b5_kvkk"))

# BOLUM 6
with st.expander(t("annex.b6_baslik"), expanded=False):
    sys_robustluk = st.text_area(t("annex.b6_robustluk"), height=60)
    sys_siber = st.text_area(t("annex.b6_siber"), height=60)

# BOLUM 7
with st.expander(t("annex.b7_baslik"), expanded=False):
    sys_insan_gozetim = st.text_area(t("annex.b7_mekanizma"), height=80)
    sys_insan_sorumlu = st.text_input(t("annex.b7_sorumlu"))

# BOLUM 8
with st.expander(t("annex.b8_baslik"), expanded=False):
    sys_versiyon_politika = st.text_area(t("annex.b8_versiyon"), height=60)
    sys_izleme = st.text_area(t("annex.b8_izleme"), height=60)

st.markdown("---")

# ============================================================
# DOKUMAN OLUSTUR
# ============================================================
if st.button(t("annex.olustur_btn"), type="primary", use_container_width=True):
    if not sistem_adi:
        st.error(t("annex.sistem_zorunlu") if "sistem_zorunlu" in dir() else "Sistem Adı zorunludur.")
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
            st.success(t("annex.olusturuldu") + str(dok_id) + ")")
        except Exception as e:
            st.error(t("annex.kayit_hatasi") + str(e))

# ============================================================
# GECMIS DOKUMANLAR
# ============================================================
st.markdown("---")
st.subheader(t("annex.gecmis_baslik"))

try:
    gecmis = db.annex_iv_listele(firma_id=firma_id)
except Exception:
    gecmis = []

if not gecmis:
    st.info(t("annex.gecmis_bos"))
else:
    for d in gecmis:
        with st.expander("📄 " + d.get("sistem_adi", "-") + " — v" + d.get("versiyon", "1.0")):
            st.caption("**" + t("annex.tarih") + ":** " + (d.get("olusturma") or "-"))
            st.caption("**" + t("annex.ai_tipi") + ":** " + (d.get("ai_tipi") or "-"))
            col1, col2 = st.columns([4, 1])
            with col1:
                st.caption("ID: " + str(d.get("id")))
            with col2:
                if st.button("🗑️", key="annex_sil_" + str(d["id"]), help=t("annex.sil")):
                    db.annex_iv_sil(d["id"])
                    st.rerun()
