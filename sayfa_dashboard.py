"""
Dashboard sayfasi - Grafikler, istatistikler, risk analizi, PDF export
"""
from utils import tr_to_ascii
import streamlit as st
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import uuid

import auth
auth.giris_gerekli()

import db
from cache_utils import istatistik_cached, listele_cached
from i18n import t
import plotly.graph_objects as go
from fpdf import FPDF

db.init_db()

# ============================================================
# SABITLER
# ============================================================
RENK_UYUMLU = "#22c55e"
RENK_UYUMSUZ = "#ef4444"
RENK_DIGER = "#94a3b8"
RENK_PALET = ["#3b82f6", "#8b5cf6", "#f59e0b", "#06b6d4", "#ec4899", "#10b981", "#f97316"]

AI_TIPI_KISA = {
    "Chatbot / AI Asistan": "Chatbot",
    "Gorsel Uretimi (C2PA)": "Gorsel",
    "Duygu Tanima (Musteri Tarafi)": "Duygu (Musteri)",
    "Duygu Tanima (Calisan Tarafi)": "Duygu (Calisan)",
    "Biyometrik Siniflandirma": "Biyometrik",
    "Deepfake Icerik": "Deepfake",
    "Kamu Yarari Metni": "Kamu Yarari",
    "Karisik": "Karisik",
}




def _pdf_olustur(ist, kayitlar, firma_adi, ay_kars, risk_veri, tarih_aralik_str):
    """Dashboard PDF raporu olusturur."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "AI UYUMLULUK DASHBOARD RAPORU", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    pdf.set_font("Helvetica", "B", 10)
    rapor_no = "DASH-" + datetime.now().strftime("%Y%m%d") + "-" + str(uuid.uuid4())[:6].upper()
    pdf.cell(0, 6, "Rapor No: " + rapor_no, new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, "Firma: " + tr_to_ascii(firma_adi or "Bilinmiyor"), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, "Tarih: " + datetime.now().strftime("%Y-%m-%d %H:%M"), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, "Aralik: " + tr_to_ascii(tarih_aralik_str), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # Metrikler
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "GENEL METRIKLER", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=11)
    toplam = ist["toplam"]
    uyumlu = ist["uyumlu"]
    uyumsuz = ist["uyumsuz"]
    diger = ist["diger"]
    oran = round((uyumlu / toplam * 100), 1) if toplam > 0 else 0.0
    pdf.cell(0, 7, "  Toplam Denetim: " + str(toplam), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "  Uyumlu: " + str(uyumlu), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "  Uyumsuz: " + str(uyumsuz), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "  Diger: " + str(diger), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "  Uyum Orani: %" + str(oran), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # Aylik karsilastirma
    if ay_kars:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "AYLIK KARSILASTIRMA", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", size=11)
        pdf.cell(0, 7, "  Bu Ay Toplam: " + str(ay_kars["bu_ay_toplam"]), new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 7, "  Gecen Ay Toplam: " + str(ay_kars["gecen_ay_toplam"]), new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 7, "  Degisim: " + str(ay_kars["toplam_delta"]), new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 7, "  Bu Ay Uyum Orani: %" + str(ay_kars["bu_ay_oran"]), new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 7, "  Gecen Ay Uyum Orani: %" + str(ay_kars["gecen_ay_oran"]), new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 7, "  Oran Degisimi: " + str(ay_kars["oran_delta"]), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

    # Risk analizi
    if risk_veri:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "RISK ANALIZI - EN COK UYUMSUZ MUSTERILER", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", size=11)
        for m, v in risk_veri["musteri_top"][:5]:
            pdf.cell(0, 7, "  - " + tr_to_ascii(m) + ": " + str(v) + " uyumsuz", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "RISK ANALIZI - EN COK UYUMSUZ AI TIPLERI", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", size=11)
        for a, v in risk_veri["ai_top"][:5]:
            pdf.cell(0, 7, "  - " + tr_to_ascii(a) + ": " + str(v) + " uyumsuz", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

    # Son aktiviteler
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "SON 20 AKTIVITE", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=9)
    for k in kayitlar[:20]:
        satir = (tr_to_ascii(k.get("tarih", "")[:16]) + " | "
                 + tr_to_ascii(k.get("musteri", "-"))[:25] + " | "
                 + tr_to_ascii(AI_TIPI_KISA.get(k.get("ai_tipi"), k.get("ai_tipi", "-")))[:15] + " | "
                 + tr_to_ascii(k.get("genel_sonuc", "-")))
        pdf.cell(0, 6, satir, new_x="LMARGIN", new_y="NEXT")

    return pdf, rapor_no


# ============================================================
# VERI CEK
# ============================================================
firma_id = auth.firma_id()
firma_adi_str = auth.firma_adi() or ""
ist = istatistik_cached(firma_id=firma_id)
kayitlar = listele_cached(limit=1000, firma_id=firma_id)

# ============================================================
# BASLIK
# ============================================================
st.title("📊 " + t("dashboard.baslik"))
st.markdown(t("dashboard.aciklama"))
st.markdown("---")

if ist["toplam"] == 0:
    st.info("ℹ️ " + t("dashboard.veri_yok"))
    st.caption(t("dashboard.veri_yok_aciklama"))
    st.stop()

# ============================================================
# METRIK KARTLARI
# ============================================================
toplam = ist["toplam"]
uyumlu = ist["uyumlu"]
uyumsuz = ist["uyumsuz"]
diger = ist["diger"]
oran = round((uyumlu / toplam * 100), 1) if toplam > 0 else 0.0

c1, c2, c3, c4 = st.columns(4)
c1.metric(t("dashboard.toplam"), toplam)
c2.metric(t("dashboard.uyumlu"), uyumlu)
c3.metric(t("dashboard.uyumsuz"), uyumsuz)
c4.metric(t("dashboard.uyum_orani"), f"%{oran}")

st.markdown("---")

# ============================================================
# AYLIK KARSILASTIRMA
# ============================================================
def _ay_araligi(yil, ay):
    baslangic = datetime(yil, ay, 1)
    if ay == 12:
        sonraki = datetime(yil + 1, 1, 1)
    else:
        sonraki = datetime(yil, ay + 1, 1)
    return baslangic, sonraki


simdi = datetime.now()
bu_ay_bas, bu_ay_son = _ay_araligi(simdi.year, simdi.month)
onceki_ay_bas = _ay_araligi(simdi.year - 1, 12)[0] if simdi.month == 1 else _ay_araligi(simdi.year, simdi.month - 1)[0]
onceki_ay_son = bu_ay_bas

bu_ay_kayitlar = []
gecen_ay_kayitlar = []
for k in kayitlar:
    try:
        kt = datetime.strptime((k.get("tarih") or "")[:19], "%Y-%m-%d %H:%M:%S")
        if bu_ay_bas <= kt < bu_ay_son:
            bu_ay_kayitlar.append(k)
        elif onceki_ay_bas <= kt < onceki_ay_son:
            gecen_ay_kayitlar.append(k)
    except Exception:
        pass

def _oran(lst):
    if not lst:
        return 0.0
    u = sum(1 for x in lst if x.get("genel_sonuc") == "UYUMLU")
    return round(u / len(lst) * 100, 1)

bu_ay_toplam = len(bu_ay_kayitlar)
gecen_ay_toplam = len(gecen_ay_kayitlar)
bu_ay_oran = _oran(bu_ay_kayitlar)
gecen_ay_oran = _oran(gecen_ay_kayitlar)

def _delta_str(yeni, eski):
    if eski == 0 and yeni == 0:
        return "0"
    if eski == 0:
        return f"+{yeni}"
    fark = yeni - eski
    if fark > 0:
        return f"+{fark}"
    elif fark < 0:
        return f"{fark}"
    return "0"

def _delta_yuzde(yeni, eski):
    if eski == 0 and yeni == 0:
        return "0%"
    if eski == 0:
        return "+100%"
    fark = round((yeni - eski) / eski * 100, 1)
    if fark > 0:
        return f"+{fark}%"
    elif fark < 0:
        return f"{fark}%"
    return "0%"

toplam_delta = _delta_str(bu_ay_toplam, gecen_ay_toplam)
oran_delta = _delta_str(bu_ay_oran, gecen_ay_oran)
toplam_yuzde = _delta_yuzde(bu_ay_toplam, gecen_ay_toplam)
oran_yuzde = _delta_yuzde(bu_ay_oran, gecen_ay_oran)

st.subheader("📅 " + t("dashboard.aylik_karsilastirma"))
ca, cb, cc, cd = st.columns(4)
ca.metric(t("dashboard.bu_ay"), bu_ay_toplam, delta=toplam_delta)
cb.metric(t("dashboard.gecen_ay"), gecen_ay_toplam)
cc.metric(t("dashboard.bu_ay_oran"), f"%{bu_ay_oran}", delta=oran_delta)
cd.metric(t("dashboard.degisim"), toplam_yuzde, delta=oran_yuzde)

ay_kars = {
    "bu_ay_toplam": bu_ay_toplam,
    "gecen_ay_toplam": gecen_ay_toplam,
    "toplam_delta": toplam_delta,
    "bu_ay_oran": bu_ay_oran,
    "gecen_ay_oran": gecen_ay_oran,
    "oran_delta": oran_delta,
}

st.markdown("---")

# ============================================================
# FILTRE - Tarih araligi
# ============================================================
col_f1, _ = st.columns([1, 3])
with col_f1:
    aralik = st.selectbox(
        t("dashboard.tarih_aralik"),
        ["tum", "7", "30", "90"],
        format_func=lambda x: t("dashboard.tum_zamanlar") if x == "tum" else t(f"dashboard.son_{x}"),
        key="dash_aralik",
    )

aralik_str = t("dashboard.tum_zamanlar") if aralik == "tum" else t(f"dashboard.son_{aralik}")

if aralik == "tum":
    kayitlar_f = kayitlar
else:
    gun = int(aralik)
    sinir = datetime.now() - timedelta(days=gun)
    kayitlar_f = []
    for k in kayitlar:
        try:
            tarih_str = k.get("tarih", "") or ""
            kt = datetime.strptime(tarih_str[:19], "%Y-%m-%d %H:%M:%S")
            if kt >= sinir:
                kayitlar_f.append(k)
        except Exception:
            kayitlar_f.append(k)

# ============================================================
# GRAFIK 1 + 2
# ============================================================
col_g1, col_g2 = st.columns(2)

with col_g1:
    st.subheader(t("dashboard.sonuclar_baslik"))
    fig = go.Figure(data=[go.Pie(
        labels=[t("dashboard.uyumlu"), t("dashboard.uyumsuz"), t("dashboard.diger")],
        values=[uyumlu, uyumsuz, diger],
        hole=0.55,
        marker=dict(colors=[RENK_UYUMLU, RENK_UYUMSUZ, RENK_DIGER]),
        textinfo="label+percent",
        textposition="outside",
    )])
    fig.update_layout(showlegend=False, margin=dict(l=10, r=10, t=10, b=10), height=380)
    st.plotly_chart(fig, use_container_width=True)

with col_g2:
    st.subheader(t("dashboard.ai_tipi_baslik"))
    ai_sayac = Counter(k.get("ai_tipi", "?") for k in kayitlar_f)
    if ai_sayac:
        etiketler = [AI_TIPI_KISA.get(k, k) for k in ai_sayac.keys()]
        degerler = list(ai_sayac.values())
        fig = go.Figure(data=[go.Bar(
            x=etiketler, y=degerler,
            marker_color=RENK_PALET[:len(etiketler)],
            text=degerler, textposition="outside",
        )])
        fig.update_layout(showlegend=False, margin=dict(l=10, r=10, t=10, b=10), height=380)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.caption(t("dashboard.veri_yok"))

st.markdown("---")

# ============================================================
# GRAFIK 3: Zaman serisi
# ============================================================
st.subheader(t("dashboard.trend_baslik"))

gun_sayisi = 30
bugun = datetime.now().date()
gun_listesi = [(bugun - timedelta(days=i)) for i in range(gun_sayisi - 1, -1, -1)]

gun_toplam, gun_uyumlu, gun_uyumsuz = defaultdict(int), defaultdict(int), defaultdict(int)

for k in kayitlar:
    try:
        tarih_str = k.get("tarih", "") or ""
        kt = datetime.strptime(tarih_str[:10], "%Y-%m-%d").date()
        if kt in gun_listesi:
            gun_toplam[kt] += 1
            if k.get("genel_sonuc") == "UYUMLU":
                gun_uyumlu[kt] += 1
            elif k.get("genel_sonuc") == "UYUMSUZ":
                gun_uyumsuz[kt] += 1
    except Exception:
        pass

x_labels = [g.strftime("%d %b") for g in gun_listesi]
fig = go.Figure()
fig.add_trace(go.Scatter(x=x_labels, y=[gun_toplam[g] for g in gun_listesi],
    mode="lines+markers", name=t("dashboard.toplam"),
    line=dict(color="#3b82f6", width=3)))
fig.add_trace(go.Scatter(x=x_labels, y=[gun_uyumlu[g] for g in gun_listesi],
    mode="lines+markers", name=t("dashboard.uyumlu"),
    line=dict(color=RENK_UYUMLU, width=2)))
fig.add_trace(go.Scatter(x=x_labels, y=[gun_uyumsuz[g] for g in gun_listesi],
    mode="lines+markers", name=t("dashboard.uyumsuz"),
    line=dict(color=RENK_UYUMSUZ, width=2)))
fig.update_layout(
    height=380, margin=dict(l=10, r=10, t=10, b=10), hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ============================================================
# RISK ANALIZI
# ============================================================
st.subheader("⚠️ " + t("dashboard.risk_baslik"))

uyumsuz_kayitlar = [k for k in kayitlar_f if k.get("genel_sonuc") == "UYUMSUZ"]

if not uyumsuz_kayitlar:
    st.success("✅ " + t("dashboard.risk_yok"))
    risk_veri = None
else:
    musteri_sayac = Counter(k.get("musteri", "?") for k in uyumsuz_kayitlar)
    ai_sayac = Counter(k.get("ai_tipi", "?") for k in uyumsuz_kayitlar)

    cr1, cr2 = st.columns(2)

    with cr1:
        st.markdown("**" + t("dashboard.risk_musteri") + "**")
        for m, v in musteri_sayac.most_common(5):
            st.write(f"🔴 **{m}** — {v} " + t("dashboard.risk_uyumsuz"))

    with cr2:
        st.markdown("**" + t("dashboard.risk_ai_tipi") + "**")
        for a, v in ai_sayac.most_common(5):
            st.write(f"🔴 **{AI_TIPI_KISA.get(a, a)}** — {v} " + t("dashboard.risk_uyumsuz"))

    risk_veri = {
        "musteri_top": musteri_sayac.most_common(5),
        "ai_top": ai_sayac.most_common(5),
    }

st.markdown("---")

# ============================================================
# HEATMAP - Musteri x AI Tipi
# ============================================================
st.subheader("🔥 " + t("dashboard.heatmap_baslik"))

# Son 10 musteri
musteri_listesi = list(dict.fromkeys([k.get("musteri", "?") for k in kayitlar_f]))[:10]
ai_listesi = list(dict.fromkeys([k.get("ai_tipi", "?") for k in kayitlar_f]))[:8]

if musteri_listesi and ai_listesi:
    # Heatmap verisi: uyum orani (%)
    z = []
    for m in musteri_listesi:
        satir = []
        for a in ai_listesi:
            ilgili = [k for k in kayitlar_f if k.get("musteri") == m and k.get("ai_tipi") == a]
            if not ilgili:
                satir.append(None)
            else:
                u = sum(1 for k in ilgili if k.get("genel_sonuc") == "UYUMLU")
                satir.append(round(u / len(ilgili) * 100, 1))
        z.append(satir)

    fig = go.Figure(data=go.Heatmap(
        z=z,
        x=[AI_TIPI_KISA.get(a, a) for a in ai_listesi],
        y=musteri_listesi,
        colorscale=[[0, RENK_UYUMSUZ], [0.5, "#fbbf24"], [1, RENK_UYUMLU]],
        zmin=0, zmax=100,
        text=[[("" if v is None else f"%{v}") for v in row] for row in z],
        texttemplate="%{text}",
        textfont={"size": 11},
        hovertemplate="Musteri: %{y}<br>AI Tipi: %{x}<br>Uyum: %{text}<extra></extra>",
        colorbar=dict(title="%"),
    ))
    fig.update_layout(
        height=100 + len(musteri_listesi) * 45,
        margin=dict(l=10, r=10, t=10, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("🟢 Yüksek uyum (%100) — 🟡 Orta — 🔴 Düşük uyum (%0)")
else:
    st.caption(t("dashboard.veri_yok"))

st.markdown("---")

# ============================================================
# TABLO: Son aktivite
# ============================================================
st.subheader(t("dashboard.son_aktivite"))
son_kayitlar = kayitlar_f[:20]

if son_kayitlar:
    satirlar = [{
        t("dashboard.tablo_rapor_no"): k.get("rapor_no", "-"),
        t("dashboard.tablo_musteri"): k.get("musteri", "-"),
        t("dashboard.tablo_ai_tipi"): AI_TIPI_KISA.get(k.get("ai_tipi"), k.get("ai_tipi", "-")),
        t("dashboard.tablo_denetci"): k.get("denetci", "-"),
        t("dashboard.tablo_sonuc"): k.get("genel_sonuc", "-"),
        t("dashboard.tablo_tarih"): (k.get("tarih") or "-")[:16],
    } for k in son_kayitlar]
    st.dataframe(satirlar, use_container_width=True, hide_index=True)
else:
    st.info(t("dashboard.kayit_yok"))

st.markdown("---")

# ============================================================
# PDF EXPORT
# ============================================================
st.subheader("📄 " + t("dashboard.pdf_baslik"))
st.caption(t("dashboard.pdf_aciklama"))

if st.button("📥 " + t("dashboard.pdf_btn"), type="primary", use_container_width=True):
    with st.spinner(t("dashboard.pdf_olusturuluyor")):
        try:
            pdf, pdf_rapor_no = _pdf_olustur(
                ist, kayitlar_f, firma_adi_str, ay_kars, risk_veri, aralik_str
            )
            pdf_bytes = bytes(pdf.output())
            st.download_button(
                label="📥 " + t("dashboard.pdf_indir"),
                data=pdf_bytes,
                file_name=f"dashboard_{pdf_rapor_no}.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="pdf_download_btn",
            )
            st.success("✅ " + t("dashboard.pdf_hazir") + " — " + pdf_rapor_no)
        except Exception as e:
            st.error("❌ " + t("dashboard.pdf_hata") + ": " + str(e))