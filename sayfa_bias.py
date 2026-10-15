"""
sayfa_bias.py - Bias ve Adillik Denetimi
"""
import streamlit as st
import auth
auth.giris_gerekli()

import db
import pandas as pd
from i18n import t


st.title("⚖️ " + t("bias.baslik"))
st.markdown("**" + t("bias.alt_baslik") + "**")
st.markdown("---")

kullanici = auth.mevcut_kullanici()
firma_id = kullanici.get("firma_id") if kullanici else None

# ============================================================
# ACIKLAMA
# ============================================================
st.info(t("bias.nasil_calisir"))

# ============================================================
# DOSYA YUKLE
# ============================================================
st.subheader(t("bias.dataset_yukle"))

col1, col2 = st.columns(2)
with col1:
    sistem_adi = st.text_input(t("bias.sistem_adi") + " *", placeholder=t("bias.sistem_placeholder"))
with col2:
    dataset_adi = st.text_input(t("bias.dataset_adi"), placeholder=t("bias.dataset_placeholder"))

dosya = st.file_uploader(t("bias.csv_yukle"), type=["csv"])

if dosya is not None:
    try:
        df = pd.read_csv(dosya)
        st.success(t("bias.yuklendi").format(satir=len(df), sutun=len(df.columns)))
        st.markdown(t("bias.ilk_satirlar"))
        st.dataframe(df.head())

        st.markdown("---")
        st.subheader(t("bias.ayarlar"))

        col1, col2 = st.columns(2)
        with col1:
            hassas_sutun = st.selectbox(t("bias.hassas_sutun"), df.columns.tolist())
            hassas_degerler = df[hassas_sutun].dropna().unique().tolist()
            st.caption(t("bias.bulunan_gruplar") + ", ".join([str(x) for x in hassas_degerler[:5]]))
        with col2:
            sonuc_sutun = st.selectbox(t("bias.sonuc_sutun"), df.columns.tolist())
            pozitif_deger = st.text_input(t("bias.pozitif_deger"), value="1")

        st.markdown("---")

        if st.button(t("bias.analiz_btn"), type="primary", use_container_width=True):
            if not sistem_adi:
                st.error(t("bias.sistem_adi_zorunlu"))
            elif not hassas_sutun or not sonuc_sutun:
                st.error(t("bias.sutun_zorunlu"))
            else:
                try:
                    df["_pozitif"] = df[sonuc_sutun].astype(str).str.lower() == str(pozitif_deger).lower()

                    oranlar = df.groupby(hassas_sutun)["_pozitif"].mean()
                    gruplar = oranlar.index.tolist()
                    oran_degerler = oranlar.values.tolist()

                    if len(gruplar) < 2:
                        st.warning("En az 2 grup gerekli.")
                    else:
                        min_oran = min(oran_degerler)
                        max_oran = max(oran_degerler)
                        fark = max_oran - min_oran
                        bias_skoru = round(fark * 100, 1)

                        if bias_skoru < 10:
                            risk_seviyesi = "dusuk"
                            emoji = "🟢"
                        elif bias_skoru < 20:
                            risk_seviyesi = "orta"
                            emoji = "🟡"
                        else:
                            risk_seviyesi = "yuksek"
                            emoji = "🔴"

                        st.markdown("---")
                        st.subheader(t("bias.sonuc_baslik"))

                        col1, col2, col3 = st.columns(3)
                        col1.metric(t("bias.bias_skoru"), f"%{bias_skoru}")
                        col2.metric(t("bias.en_yuksek"), f"%{round(max_oran*100, 1)}")
                        col3.metric(t("bias.en_dusuk"), f"%{round(min_oran*100, 1)}")

                        if risk_seviyesi == "yuksek":
                            st.error(f"{emoji} " + t("bias.yuksek_uyari"))
                        elif risk_seviyesi == "orta":
                            st.warning(f"{emoji} " + t("bias.orta_uyari"))
                        else:
                            st.success(f"{emoji} " + t("bias.dusuk_mesaj"))

                        st.markdown("### " + t("bias.gruplar_baslik"))
                        for g, o in zip(gruplar, oran_degerler):
                            st.markdown(f"- **{g}**: %{round(o*100, 1)}")

                        st.markdown("### " + t("bias.oneriler"))
                        if bias_skoru >= 20:
                            st.markdown("- Eğitim verisini yeniden dengeleyin")
                            st.markdown("- Hassas özellikleri modelden çıkarın veya maskeleyin")
                            st.markdown("- Fairness-aware algoritma kullanın")
                        elif bias_skoru >= 10:
                            st.markdown("- Azınlık grubun verisini artırın")
                            st.markdown("- Model performansını gruplara göre ayrı test edin")
                        else:
                            st.markdown("- Düzenli izlemeye devam edin")

                        detay = {
                            "gruplar": [{"grup": str(g), "oran": float(o)} for g, o in zip(gruplar, oran_degerler)],
                            "max_oran": float(max_oran),
                            "min_oran": float(min_oran),
                            "fark": float(fark),
                        }
                        try:
                            db.bias_kaydet(
                                firma_id=firma_id,
                                sistem_adi=sistem_adi,
                                dataset_adi=dataset_adi or dosya.name,
                                hassas_sutun=hassas_sutun,
                                sonuc_sutun=sonuc_sutun,
                                bias_skoru=bias_skoru,
                                risk_seviyesi=risk_seviyesi,
                                detay=detay,
                            )
                            st.success(t("bias.kaydedildi"))
                        except Exception as e:
                            st.warning(t("bias.kayit_hatasi") + str(e))

                except Exception as e:
                    st.error(t("bias.analiz_hatasi") + str(e))

    except Exception as e:
        st.error(t("bias.dosya_hatasi") + str(e))

# ============================================================
# GECMIS ANALIZLER
# ============================================================
st.markdown("---")
st.subheader(t("bias.gecmis_baslik"))

try:
    gecmis = db.bias_listele(firma_id=firma_id)
except Exception:
    gecmis = []

if not gecmis:
    st.info(t("bias.gecmis_bos"))
else:
    for g in gecmis:
        risk = g.get("risk_seviyesi", "-")
        emoji = {"dusuk": "🟢", "orta": "🟡", "yuksek": "🔴"}.get(risk, "⚪")
        with st.expander(f"{emoji} {g.get('sistem_adi', '-')} — %{g.get('bias_skoru', 0)}"):
            st.caption("**" + t("bias.tarih") + ":** " + (g.get("olusturma") or "-"))
            st.caption("**" + t("bias.dataset_adi") + ":** " + (g.get("dataset_adi") or "-"))
            st.caption("**" + t("bias.hassas_sutun") + ":** " + (g.get("hassas_sutun") or "-"))
            st.caption("**" + t("bias.sonuc_sutun") + ":** " + (g.get("sonuc_sutun") or "-"))
            col1, col2 = st.columns([4, 1])
            with col2:
                if st.button("🗑️", key="bias_sil_" + str(g["id"]), help=t("bias.sil")):
                    db.bias_sil(g["id"])
                    st.rerun()
