"""
sayfa_izleme.py - Surekli Izleme ve Trend Analizi
"""
import streamlit as st
import auth
auth.giris_gerekli()

import db
import pandas as pd
from i18n import t


st.title("📈 " + t("izleme.baslik"))
st.markdown("**" + t("izleme.alt_baslik") + "**")
st.markdown("---")

kullanici = auth.mevcut_kullanici()
firma_id = kullanici.get("firma_id") if kullanici else None

# ============================================================
# ALARMLAR
# ============================================================
st.subheader(t("izleme.aktif_alarmlar"))

try:
    alarmlar = db.alarm_kontrol(firma_id)
except Exception as e:
    alarmlar = []
    st.warning(t("izleme.kayit_hatasi") + str(e) if "kayit_hatasi" in dir() else str(e))

if not alarmlar:
    st.success(t("izleme.alarm_yok"))
else:
    for a in alarmlar:
        seviye = a.get("seviye", "uyari")
        if seviye == "kritik":
            st.error(f"🔴 **{a['baslik']}** — {a['mesaj']}")
        elif seviye == "uyari":
            st.warning(f"🟡 **{a['baslik']}** — {a['mesaj']}")
        else:
            st.info(f"🔵 **{a['baslik']}** — {a['mesaj']}")

st.markdown("---")

# ============================================================
# GENEL TREND
# ============================================================
st.subheader(t("izleme.genel_trend"))

try:
    t30 = db.trend_analizi(firma_id, gun=30)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(t("izleme.son_30"), t30["toplam"])
    col2.metric(t("izleme.uyumlu"), t30["uyumlu"])
    col3.metric(t("izleme.uyumsuz"), t30["uyumsuz"])
    col4.metric(t("izleme.uyum_orani"), f"%{t30['uyum_orani']}")
except Exception as e:
    st.error(t("izleme.kayit_hatasi") + str(e) if "kayit_hatasi" in dir() else str(e))

st.markdown("---")

# ============================================================
# HAFTALIK TREND GRAFIGI
# ============================================================
st.subheader(t("izleme.haftalik_trend"))

try:
    haftalik = db.haftalik_trend(firma_id, hafta=8)

    if haftalik:
        df_h = pd.DataFrame(haftalik)
        df_h = df_h.rename(columns={
            "hafta": "Hafta",
            "toplam": t("izleme.toplam") if "toplam" in dir() else "Toplam",
            "uyumlu": t("izleme.uyumlu"),
            "uyum_orani": t("izleme.uyum_orani"),
        })
        st.dataframe(df_h[["Hafta", "Toplam", t("izleme.uyumlu"), t("izleme.uyum_orani")]], use_container_width=True)

        try:
            import plotly.express as px
            fig = px.line(
                df_h,
                x="Hafta",
                y=t("izleme.uyum_orani"),
                markers=True,
                title=t("izleme.haftalik_trend"),
            )
            fig.update_layout(
                plot_bgcolor="#0a0a0a",
                paper_bgcolor="#0a0a0a",
                font_color="#fafafa",
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception:
            st.bar_chart(df_h.set_index("Hafta")[t("izleme.uyum_orani")])
    else:
        st.info(t("izleme.yeterli_veri_yok"))
except Exception as e:
    st.error(t("izleme.kayit_hatasi") + str(e) if "kayit_hatasi" in dir() else str(e))

st.markdown("---")

# ============================================================
# AI TIPI DAGILIMI
# ============================================================
st.subheader(t("izleme.ai_tipi_dagilimi"))

try:
    dagilim = db.ai_tipi_dagilimi(firma_id, gun=30)
    if dagilim:
        df_d = pd.DataFrame(dagilim)
        df_d = df_d.rename(columns={"ai_tipi": t("envanter.ai_tipi"), "n": t("izleme.toplam") if "toplam" in dir() else "Adet"})
        st.dataframe(df_d, use_container_width=True)

        try:
            import plotly.express as px
            fig2 = px.pie(
                df_d,
                names=t("envanter.ai_tipi"),
                values=df_d.columns[1],
                title=t("izleme.ai_tipi_dagilimi"),
            )
            fig2.update_layout(
                plot_bgcolor="#0a0a0a",
                paper_bgcolor="#0a0a0a",
                font_color="#fafafa",
            )
            st.plotly_chart(fig2, use_container_width=True)
        except Exception:
            st.bar_chart(df_d.set_index(t("envanter.ai_tipi"))[df_d.columns[1]])
    else:
        st.info(t("izleme.denetim_yok"))
except Exception as e:
    st.error(t("izleme.kayit_hatasi") + str(e) if "kayit_hatasi" in dir() else str(e))

# ============================================================
# OZET
# ============================================================
st.markdown("---")
st.subheader(t("izleme.yorumlar"))

try:
    if t30["toplam"] == 0:
        st.info(t("izleme.denetim_yok_yorum"))
    elif t30["uyum_orani"] >= 80:
        st.success(t("izleme.yuksek_uyum"))
    elif t30["uyum_orani"] >= 50:
        st.warning(t("izleme.orta_uyum"))
    else:
        st.error(t("izleme.dusuk_uyum"))
except Exception:
    pass
