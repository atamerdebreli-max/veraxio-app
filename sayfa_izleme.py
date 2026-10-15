"""
sayfa_izleme.py - Surekli Izleme ve Trend Analizi
"""
import streamlit as st
import auth
auth.giris_gerekli()

import db
from datetime import datetime
import pandas as pd


st.title("📈 Sürekli İzleme")
st.markdown("**AI sistemlerinizin zaman içindeki uyumluluk trendi ve alarmlar.**")
st.markdown("---")

kullanici = auth.mevcut_kullanici()
firma_id = kullanici.get("firma_id") if kullanici else None

# ============================================================
# ALARMLAR
# ============================================================
st.subheader("🚨 Aktif Alarmlar")

try:
    alarmlar = db.alarm_kontrol(firma_id)
except Exception as e:
    alarmlar = []
    st.warning("Alarm kontrolu yapilamadi: " + str(e))

if not alarmlar:
    st.success("✅ Su anda aktif alarm yok. Her sey yolunda!")
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
st.subheader("📊 Genel Trend")

try:
    t30 = db.trend_analizi(firma_id, gun=30)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Son 30 Gün", t30["toplam"])
    col2.metric("Uyumlu", t30["uyumlu"])
    col3.metric("Uyumsuz", t30["uyumsuz"])
    col4.metric("Uyum Oranı", f"%{t30['uyum_orani']}")
except Exception as e:
    st.error("Trend yuklenemedi: " + str(e))

st.markdown("---")

# ============================================================
# HAFTALIK TREND GRAFIGI
# ============================================================
st.subheader("📅 Haftalık Uyum Trendi (Son 8 Hafta)")

try:
    haftalik = db.haftalik_trend(firma_id, hafta=8)

    if haftalik:
        df_h = pd.DataFrame(haftalik)
        df_h = df_h.rename(columns={
            "hafta": "Hafta",
            "toplam": "Toplam",
            "uyumlu": "Uyumlu",
            "uyum_orani": "Uyum %",
        })
        st.dataframe(df_h[["Hafta", "Toplam", "Uyumlu", "Uyum %"]], use_container_width=True)

        # Basit grafik
        try:
            import plotly.express as px
            fig = px.line(
                df_h,
                x="Hafta",
                y="Uyum %",
                markers=True,
                title="Haftalik Uyum Orani (%)",
            )
            fig.update_layout(
                plot_bgcolor="#0a0a0a",
                paper_bgcolor="#0a0a0a",
                font_color="#fafafa",
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception:
            st.bar_chart(df_h.set_index("Hafta")["Uyum %"])
    else:
        st.info("Henuz yeterli veri yok.")
except Exception as e:
    st.error("Haftalik trend yuklenemedi: " + str(e))

st.markdown("---")

# ============================================================
# AI TIPI DAGILIMI
# ============================================================
st.subheader("🤖 AI Tipi Dağılımı (Son 30 Gün)")

try:
    dagilim = db.ai_tipi_dagilimi(firma_id, gun=30)
    if dagilim:
        df_d = pd.DataFrame(dagilim)
        df_d = df_d.rename(columns={"ai_tipi": "AI Tipi", "n": "Denetim Sayısı"})
        st.dataframe(df_d, use_container_width=True)

        try:
            import plotly.express as px
            fig2 = px.pie(
                df_d,
                names="AI Tipi",
                values="Denetim Sayısı",
                title="AI Tipi Dagilimi",
            )
            fig2.update_layout(
                plot_bgcolor="#0a0a0a",
                paper_bgcolor="#0a0a0a",
                font_color="#fafafa",
            )
            st.plotly_chart(fig2, use_container_width=True)
        except Exception:
            st.bar_chart(df_d.set_index("AI Tipi")["Denetim Sayısı"])
    else:
        st.info("Son 30 gunde denetim yapilmadi.")
except Exception as e:
    st.error("Dagilim yuklenemedi: " + str(e))

# ============================================================
# OZET
# ============================================================
st.markdown("---")
st.subheader("💡 Yorum ve Oneriler")

try:
    if t30["toplam"] == 0:
        st.info("Henuz denetim yapilmadi. Denetim yaptikca trend burada gorunecek.")
    elif t30["uyum_orani"] >= 80:
        st.success("🎉 Uyum oraniniz yuksek! Duzenli denetimlerle bunu koruyun.")
    elif t30["uyum_orani"] >= 50:
        st.warning("⚠️ Uyum oraniniz orta seviyede. Iyilestirme alanlarina odaklanin.")
    else:
        st.error("🚨 Uyum oraniniz dusuk. Derhal aksiyon alin.")
except Exception:
    pass
