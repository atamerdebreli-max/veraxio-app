"""
Gecmis Denetimler sayfasi
"""
import json

# Giris kontrolu
import auth
auth.giris_gerekli()

import streamlit as st
from datetime import datetime, timedelta
import db
from cache_utils import istatistik_cached
from i18n import t



st.title(t("sayfa_gecmis.baslik"))
st.markdown("**" + t("sayfa_gecmis.aciklama") + "**")
st.markdown("---")

# Veritabani init
db.init_db()

# ============================================================
# ISTATISTIK
# ============================================================
istat = istatistik_cached(firma_id=auth.firma_id())

col1, col2, col3, col4 = st.columns(4)
col1.metric(t("sayfa_gecmis.toplam_denetim"), istat["toplam"])
col2.metric(t("sayfa_gecmis.uyumlu"), istat["uyumlu"])
col3.metric(t("sayfa_gecmis.uyumsuz"), istat["uyumsuz"])
col4.metric(t("sayfa_gecmis.diger"), istat["diger"])

st.markdown("---")

# ============================================================
# FILTRELER
# ============================================================
st.subheader(t("sayfa_gecmis.filtreler"))

col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    filtre_musteri = st.text_input(t("sayfa_gecmis.musteri_filtre"), "")
    SONUC_ANAHTARLARI = {
        "Tümü": "sayfa_gecmis.tumu",
        "UYUMLU": "sonuc.uyumlu",
        "UYUMSUZ": "sonuc.uyumsuz",
    }
    filtre_sonuc = st.selectbox(
        t("sayfa_gecmis.sonuc_filtre"),
        ["Tümü", "UYUMLU", "UYUMSUZ"],
        format_func=lambda x: t(SONUC_ANAHTARLARI.get(x, x)),
    )

with col_f2:
    AI_TIPI_ANAHTARLARI = {
        "Tümü": "sayfa_gecmis.tumu",
        "Chatbot / AI Asistan": "ai_tipleri.chatbot",
        "Gorsel Uretimi (C2PA)": "ai_tipleri.gorsel",
        "Duygu Tanima (Musteri Tarafi)": "ai_tipleri.duygu_musteri",
        "Duygu Tanima (Calisan Tarafi)": "ai_tipleri.duygu_calisan",
        "Biyometrik Siniflandirma": "ai_tipleri.biyometrik",
        "Deepfake Icerik": "ai_tipleri.deepfake",
        "Kamu Yarari Metni": "ai_tipleri.kamu_metni",
    }
    filtre_ai_tipi = st.selectbox(
        t("sayfa_gecmis.ai_tipi_filtre"),
        ["Tümü", "Chatbot / AI Asistan", "Gorsel Uretimi (C2PA)",
         "Duygu Tanima (Musteri Tarafi)", "Duygu Tanima (Calisan Tarafi)",
         "Biyometrik Siniflandirma", "Deepfake Icerik", "Kamu Yarari Metni"],
        format_func=lambda x: t(AI_TIPI_ANAHTARLARI.get(x, x)),
    )

with col_f3:
    filtre_tarih_bas = st.date_input(t("sayfa_gecmis.tarih_bas"), value=None)
    filtre_tarih_son = st.date_input(t("sayfa_gecmis.tarih_son"), value=None)

# Filtre uygula
kwargs = {}
if filtre_musteri:
    kwargs["filtre_musteri"] = filtre_musteri
if filtre_sonuc != "Tümü":
    kwargs["filtre_sonuc"] = filtre_sonuc
if filtre_ai_tipi != "Tümü":
    kwargs["filtre_ai_tipi"] = filtre_ai_tipi
if filtre_tarih_bas:
    kwargs["filtre_tarih_bas"] = filtre_tarih_bas.strftime("%Y-%m-%d")
if filtre_tarih_son:
    kwargs["filtre_tarih_son"] = filtre_tarih_son.strftime("%Y-%m-%d")

kwargs["filtre_firma_id"] = auth.firma_id()
kayitlar = db.listele(**kwargs)

st.markdown("---")
st.subheader(f"📋 {t('sayfa_gecmis.kayitlar')} ({len(kayitlar)})")

if not kayitlar:
    st.info(t("sayfa_gecmis.kayit_yok"))
else:
    # Tablo için sadece gösterilecek sütunlar
    goster = []
    for k in kayitlar:
        goster.append({
            "Rapor No": k["rapor_no"],
            "Tarih": k["tarih"],
            "Modül": k["modul"],
            "Müşteri": k["musteri"],
            "AI Tipi": k["ai_tipi"],
            "Sonuç": k["genel_sonuc"],
            "Denetçi": k["denetci"],
        })

    st.dataframe(goster, use_container_width=True, hide_index=True)

    # ============================================================
    # DISA AKTARMA
    # ============================================================
    st.markdown("---")
    st.subheader(t("sayfa_gecmis.disa_aktar"))

    col_pdf, col_json, col_csv = st.columns(3)

    with col_json:
        json_bytes = json.dumps(kayitlar, ensure_ascii=False, indent=2, default=str).encode("utf-8")
        st.download_button(
            label="📥 JSON",
            data=json_bytes,
            file_name="denetim_gecmisi_" + datetime.now().strftime("%Y%m%d_%H%M") + ".json",
            mime="application/json",
            use_container_width=True,
        )

    with col_csv:
        import io
        import csv as _csv
        buf = io.StringIO()
        if kayitlar:
            w = _csv.DictWriter(buf, fieldnames=list(kayitlar[0].keys()))
            w.writeheader()
            for k in kayitlar:
                w.writerow(k)
        csv_bytes = buf.getvalue().encode("utf-8-sig")
        st.download_button(
            label="📥 CSV",
            data=csv_bytes,
            file_name="denetim_gecmisi_" + datetime.now().strftime("%Y%m%d_%H%M") + ".csv",
            mime="text/csv",
            use_container_width=True,
        )

    # ============================================================
    # DETAY GORUNTULEME VE SILME
    # ============================================================
    st.markdown("---")
    st.subheader(t("sayfa_gecmis.detay_silme"))

    secenekler = [f"{k['rapor_no']} | {k['musteri']} | {k['tarih']}" for k in kayitlar]
    secili = st.selectbox(t("sayfa_gecmis.kayit_sec"), [t("sayfa_gecmis.seciniz")] + secenekler)

    if secili != "Seçiniz...":
        rapor_no = secili.split(" | ")[0]
        kayit = next((k for k in kayitlar if k["rapor_no"] == rapor_no), None)

        if kayit:
            with st.expander(t("sayfa_gecmis.detay_goster"), expanded=True):
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    st.write(f"**{t('sayfa_gecmis.rapor_no')}:** {kayit['rapor_no']}")
                    st.write(f"**{t('sayfa_gecmis.tarih')}:** {kayit['tarih']}")
                    st.write(f"**{t('sayfa_gecmis.modul')}:** {kayit['modul']}")
                    st.write(f"**{t('sayfa_gecmis.musteri')}:** {kayit['musteri']}")
                    st.write(f"**{t('sayfa_gecmis.sektor')}:** {kayit['sektor']}")
                with col_d2:
                    st.write(f"**{t('sayfa_gecmis.ai_tipi')}:** {kayit['ai_tipi']}")
                    st.write(f"**{t('sayfa_gecmis.sonuc')}:** {kayit['genel_sonuc']}")
                    st.write(f"**{t('sayfa_gecmis.karar')}:** {kayit['karar']}")
                    st.write(f"**{t('sayfa_gecmis.kanit_id')}:** {kayit['kanit_id']}")
                    st.write(f"**{t('sayfa_gecmis.denetci')}:** {kayit['denetci']}")

                if kayit.get("json_veri"):
                    with st.expander(t("sayfa_gecmis.tam_json")):
                        st.json(json.loads(kayit["json_veri"]))

            if st.button(t("sayfa_gecmis.kaydi_sil"), type="secondary"):
                db.sil(rapor_no)
                st.success(f"{t('sayfa_gecmis.kayit_silindi')}: {rapor_no}")
                st.rerun()