"""
Toplu Denetim sayfasi - CSV'den birden fazla musteri
"""
import io
import json as _json

# Giris kontrolu
import auth
auth.giris_gerekli()

import streamlit as st
import db
from cache_utils import cache_temizle
from i18n import t

from toplu_denetim import (
    csv_sablonu_indir, csv_isle, ozet_istatistik,
    toplu_rapor_pdf_olustur, toplu_json_olustur, toplu_csv_olustur,
)
from sayfa_tek import (
    ai_bildirimi_var_mi, c2pa_kontrol, deepfake_kontrol,
    kamu_metni_kontrol, duygu_tanima_kontrol,
)

db.init_db()

st.title("📂 " + t("sayfa_toplu.baslik"))
st.markdown("**" + t("sayfa_toplu.aciklama") + "**")
st.markdown("---")

st.subheader(t("sayfa_toplu.csv_sablonu"))
st.caption(t("sayfa_toplu.csv_sablonu_aciklama"))
st.download_button(
    label=t("sayfa_toplu.csv_sablonu_btn"),
    data=csv_sablonu_indir(),
    file_name="toplu_denetim_sablonu.csv",
    mime="text/csv",
    use_container_width=True,
)

st.markdown("---")
st.subheader(t("sayfa_toplu.csv_yukle"))
csv_dosya = st.file_uploader(t("sayfa_toplu.csv_sec"), type=["csv"])

st.markdown("---")
st.subheader(t("sayfa_toplu.denetci_baslik"))
toplu_denetci = st.text_input(t("sayfa_toplu.denetci_adi"), value="Tamer")

st.markdown("---")

if st.button(t("sayfa_toplu.toplu_denetle_btn"), type="primary", use_container_width=True):
    if not csv_dosya:
        st.error(t("sayfa_toplu.csv_hata"))
    elif not toplu_denetci:
        st.error(t("sayfa_toplu.denetci_hata"))
    else:
        with st.spinner(t("sayfa_toplu.spinner")):
            icerik = csv_dosya.read()
            sonuclar = csv_isle(
                icerik, ai_bildirimi_var_mi, c2pa_kontrol,
                deepfake_kontrol, kamu_metni_kontrol, duygu_tanima_kontrol,
            )
            istatistik = ozet_istatistik(sonuclar)
            pdf, toplu_rapor_no = toplu_rapor_pdf_olustur(sonuclar, toplu_denetci, istatistik)

            st.markdown("---")
            st.subheader(t("sayfa_toplu.ozet_baslik"))

            col1, col2, col3, col4 = st.columns(4)
            col1.metric(t("sayfa_toplu.toplam"), istatistik["toplam"])
            col2.metric(t("sayfa_toplu.uyumlu"), istatistik["uyumlu"])
            col3.metric(t("sayfa_toplu.uyumsuz"), istatistik["uyumsuz"])
            col4.metric(t("sayfa_toplu.uyum_orani"), f"%{istatistik['uyum_orani']}")

            st.markdown("---")
            st.subheader(t("sayfa_toplu.detay_baslik"))
            st.dataframe(sonuclar, use_container_width=True)

            st.markdown("---")
            st.subheader(t("sayfa_toplu.rapor_indir_baslik"))

            # JSON icerik
            json_veri = toplu_json_olustur(sonuclar, istatistik, toplu_denetci, toplu_rapor_no)
            json_bytes = _json.dumps(json_veri, ensure_ascii=False, indent=2).encode("utf-8")

            # CSV icerik
            csv_bytes = toplu_csv_olustur(sonuclar)

            # 3 sutun
            col_pdf, col_json, col_csv = st.columns(3)

            with col_pdf:
                pdf_bytes_toplu = bytes(pdf.output())
                st.download_button(
                    label="📥 PDF",
                    data=pdf_bytes_toplu,
                    file_name="toplu_rapor_" + toplu_rapor_no + ".pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )

            with col_json:
                st.download_button(
                    label="📥 JSON",
                    data=json_bytes,
                    file_name="toplu_rapor_" + toplu_rapor_no + ".json",
                    mime="application/json",
                    use_container_width=True,
                )

            with col_csv:
                st.download_button(
                    label="📥 CSV",
                    data=csv_bytes,
                    file_name="toplu_rapor_" + toplu_rapor_no + ".csv",
                    mime="text/csv",
                    use_container_width=True,
                )

            # Otomatik veritabani kaydi
            db.kaydet(
                rapor_no=toplu_rapor_no,
                modul="Toplu Denetim",
                musteri=f"{istatistik['toplam']} musteri",
                sektor="",
                ai_tipi="Karisik",
                denetci=toplu_denetci,
                genel_sonuc=f"Uyumlu: {istatistik['uyumlu']} / Uyumsuz: {istatistik['uyumsuz']}",
                karar="TOPLU",
                kanit_id=toplu_rapor_no,
                ceza_riski="",
                json_veri=json_veri,
                firma_id=auth.firma_id(),
            )

            # Cache temizle - yeni kayit aninda gorunsun
            try:
                from cache_utils import cache_temizle
                cache_temizle()
            except Exception:
                pass


            st.caption("Rapor No: " + toplu_rapor_no)