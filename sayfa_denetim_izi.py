"""
sayfa_denetim_izi.py - Denetim Izi ve Degisiklik Gecmisi
"""
import streamlit as st
import auth
auth.giris_gerekli()

import db
import pandas as pd
import csv as _csv
import io as _io
from i18n import t
from datetime import datetime, timedelta


st.title("📜 " + t("denetim_izi.baslik"))
st.markdown("**" + t("denetim_izi.alt_baslik") + "**")
st.markdown("---")

kullanici = auth.mevcut_kullanici()
firma_id = kullanici.get("firma_id") if kullanici else None

# ============================================================
# ISTATISTIK
# ============================================================
try:
    ozet = db.audit_ozet(firma_id)
    col1, col2, col3 = st.columns(3)
    col1.metric(t("denetim_izi.toplam"), ozet["toplam"])
    col2.metric(t("denetim_izi.basarili"), ozet["basarili"])
    col3.metric(t("denetim_izi.basarisiz"), ozet["basarisiz"])
    st.markdown("---")
except Exception as e:
    st.warning(t("denetim_izi.kayit_hatasi") + str(e))

# ============================================================
# EYLEM DAGILIMI
# ============================================================
try:
    dagilim = db.audit_eylem_dagilimi(firma_id)
    if dagilim:
        st.subheader(t("denetim_izi.eylem_dagilimi"))
        for d in dagilim[:10]:
            eylem = d.get("eylem", "-")
            sayi = d.get("n", 0)
            st.markdown(f"- **{eylem}**: {sayi}")
        st.markdown("---")
except Exception:
    pass

# ============================================================
# FILTRELER
# ============================================================
st.subheader(t("denetim_izi.filtrele"))

col1, col2, col3 = st.columns(3)
with col1:
    filtre_kullanici = st.text_input(t("denetim_izi.kullanici"), placeholder="admin")
with col2:
    filtre_eylem = st.text_input(t("denetim_izi.eylem"), placeholder="denetim_yapildi")
with col3:
    gun_secenekleri = [
        t("denetim_izi.son_7"),
        t("denetim_izi.son_30"),
        t("denetim_izi.son_90"),
        t("denetim_izi.tumu"),
    ]
    gun_secimi = st.selectbox(t("denetim_izi.tarih_aralik"), gun_secenekleri)

tarih_bas = None
if gun_secimi == t("denetim_izi.son_7"):
    tarih_bas = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
elif gun_secimi == t("denetim_izi.son_30"):
    tarih_bas = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
elif gun_secimi == t("denetim_izi.son_90"):
    tarih_bas = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")

# ============================================================
# KAYITLAR
# ============================================================
st.markdown("---")
st.subheader(t("denetim_izi.kayitlar"))

try:
    kayitlar = db.audit_filtrele(
        firma_id=firma_id,
        kullanici_adi=filtre_kullanici or None,
        eylem=filtre_eylem or None,
        tarih_bas=tarih_bas,
        limit=500,
    )
except Exception as e:
    st.error(t("denetim_izi.kayit_hatasi") + str(e))
    kayitlar = []

if not kayitlar:
    st.info(t("denetim_izi.kayit_yok"))
else:
    st.caption(t("denetim_izi.kayit_bulundu").format(sayi=len(kayitlar)))

    goster = []
    for k in kayitlar:
        goster.append({
            t("denetim_izi.tarih"): k.get("tarih", "-"),
            t("denetim_izi.kullanici"): k.get("kullanici_adi") or "-",
            t("denetim_izi.eylem"): k.get("eylem", "-"),
            "Detay": (k.get("detay") or "")[:80],
            t("denetim_izi.basarili_kolon"): "✅" if k.get("basarili") == 1 else "❌",
            "IP": k.get("ip_adresi") or "-",
        })
    df_goster = pd.DataFrame(goster)
    st.dataframe(df_goster, use_container_width=True)

    # CSV indir
    csv_buf = _io.StringIO()
    writer = _csv.writer(csv_buf)
    writer.writerow([t("denetim_izi.tarih"), t("denetim_izi.kullanici"), t("denetim_izi.eylem"), "Detay", t("denetim_izi.basarili_kolon"), "IP"])
    for k in kayitlar:
        writer.writerow([
            k.get("tarih", ""),
            k.get("kullanici_adi", ""),
            k.get("eylem", ""),
            k.get("detay", ""),
            "Evet" if k.get("basarili") == 1 else "Hayir",
            k.get("ip_adresi", ""),
        ])
    csv_bytes = csv_buf.getvalue().encode("utf-8-sig")

    st.download_button(
        label=t("denetim_izi.csv_indir"),
        data=csv_bytes,
        file_name="denetim_izi_" + datetime.now().strftime("%Y%m%d") + ".csv",
        mime="text/csv",
        use_container_width=True,
    )
