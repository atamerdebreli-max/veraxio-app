"""
sayfa_standartlar.py - ISO 42001 ve NIST AI RMF Uyumluluk
"""
import streamlit as st
import auth
auth.giris_gerekli()

from i18n import t
from datetime import datetime


st.title("📚 " + t("standartlar.baslik"))
st.markdown("**" + t("standartlar.alt_baslik") + "**")
st.markdown("---")

kullanici = auth.mevcut_kullanici()

# ============================================================
# STANDARTLAR (Maddeler uluslararasi Ingilizce standartlardan)
# ============================================================
STANDARTLAR = {
    "ISO 42001": {
        "aciklama": "AI Management System (AIMS) - International Standard",
        "kategoriler": {
            "iso_baglam": [
                "AI policy defined and approved",
                "AI roles and responsibilities assigned",
                "Management commitment for AI risks exists",
                "AI ethics committee established",
            ],
            "iso_planlama": [
                "AI risks and opportunities identified",
                "AI objectives set measurably",
                "Legal and regulatory requirements identified",
                "Risk assessment methodology exists",
            ],
            "iso_destek": [
                "Training plan for AI team exists",
                "AI awareness program in place",
                "Communication plan defined",
                "Documentation system established",
            ],
            "iso_operasyon": [
                "AI risk assessment performed regularly",
                "AI systems inventory maintained",
                "Change management process exists",
                "Supplier management conducted",
            ],
            "iso_performans": [
                "AI performance monitored",
                "Internal audits conducted",
                "Management review performed",
                "Nonconformities recorded",
            ],
            "iso_iyilestirme": [
                "Continuous improvement process exists",
                "Corrective actions tracked",
                "Lessons learned documented",
            ],
        },
    },
    "NIST AI RMF": {
        "aciklama": "AI Risk Management Framework - NIST",
        "kategoriler": {
            "nist_govern": [
                "AI risk management policy established",
                "Roles and responsibilities defined",
                "AI risk culture promoted",
                "Stakeholder engagement ensured",
                "Legal requirements monitored",
            ],
            "nist_map": [
                "AI systems categorized",
                "Use cases documented",
                "Affected stakeholders identified",
                "Risks and benefits mapped",
            ],
            "nist_measure": [
                "AI performance measured",
                "Accuracy and reliability tested",
                "Bias and fairness assessed",
                "Security vulnerabilities tested",
                "Transparency and explainability ensured",
            ],
            "nist_manage": [
                "Risk prioritization performed",
                "Risk mitigation strategies applied",
                "Incident response plan prepared",
                "Continuous monitoring mechanism exists",
            ],
        },
    },
}

# ============================================================
# STANDART SECIMI
# ============================================================
st.subheader(t("standartlar.secim"))

secili_standart = st.selectbox(
    t("standartlar.secim_label"),
    list(STANDARTLAR.keys()),
)

std = STANDARTLAR[secili_standart]
st.info(f"**{secili_standart}** — {std['aciklama']}")

st.markdown("---")
st.subheader(t("standartlar.kontrol_listesi"))
st.caption(t("standartlar.kontrol_caption"))

state_key = f"std_{secili_standart.replace(' ', '_')}"
if state_key not in st.session_state:
    st.session_state[state_key] = {}

toplam_madde = 0
isaretlenen = 0

for kategori_key, maddeler in std["kategoriler"].items():
    kategori_ad = t(f"standartlar_kategori.{kategori_key}")
    st.markdown(f"### 🔹 {kategori_ad}")
    for i, madde in enumerate(maddeler):
        key = f"{state_key}_{kategori_key}_{i}"
        mevcut = st.session_state[state_key].get(key, False)
        secim = st.checkbox(madde, value=mevcut, key=key)
        st.session_state[state_key][key] = secim
        toplam_madde += 1
        if secim:
            isaretlenen += 1

# ============================================================
# SONUC
# ============================================================
st.markdown("---")
st.subheader(t("standartlar.sonuc_baslik"))

uyum_orani = round(100 * isaretlenen / toplam_madde, 1) if toplam_madde else 0

col1, col2, col3 = st.columns(3)
col1.metric(t("standartlar.toplam_madde"), toplam_madde)
col2.metric(t("standartlar.uyumlu"), isaretlenen)
col3.metric(t("standartlar.uyum_orani"), f"%{uyum_orani}")

if uyum_orani >= 80:
    st.success(f"🟢 " + t("standartlar.yuksek_uyum") + f" (%{uyum_orani})")
elif uyum_orani >= 50:
    st.warning(f"🟡 " + t("standartlar.orta_uyum") + f" (%{uyum_orani})")
else:
    st.error(f"🔴 " + t("standartlar.dusuk_uyum") + f" (%{uyum_orani})")

st.markdown("### " + t("standartlar.kategori_ozet"))
for kategori_key, maddeler in std["kategoriler"].items():
    kategori_ad = t(f"standartlar_kategori.{kategori_key}")
    kat_toplam = len(maddeler)
    kat_uyumlu = 0
    for i in range(kat_toplam):
        key = f"{state_key}_{kategori_key}_{i}"
        if st.session_state[state_key].get(key, False):
            kat_uyumlu += 1
    kat_oran = round(100 * kat_uyumlu / kat_toplam, 1) if kat_toplam else 0
    emoji = "🟢" if kat_oran >= 80 else ("🟡" if kat_oran >= 50 else "🔴")
    st.markdown(f"{emoji} **{kategori_ad}**: {kat_uyumlu}/{kat_toplam} (%{kat_oran})")

# ============================================================
# RAPOR INDIR
# ============================================================
st.markdown("---")

rapor = f"""# {secili_standart} COMPLIANCE REPORT

**Company:** {kullanici.get('ad_soyad') or kullanici.get('kullanici_adi', '-')}
**Date:** {datetime.now().strftime('%d.%m.%Y %H:%M')}
**Standard:** {secili_standart}
**Overall Compliance:** %{uyum_orani}

---

## OVERALL RESULT

- Total Items: {toplam_madde}
- Compliant: {isaretlenen}
- Non-compliant: {toplam_madde - isaretlenen}
- Compliance Rate: %{uyum_orani}

---

## CATEGORY DETAILS

"""

for kategori_key, maddeler in std["kategoriler"].items():
    kategori_ad = t(f"standartlar_kategori.{kategori_key}")
    kat_toplam = len(maddeler)
    kat_uyumlu = 0
    for i in range(kat_toplam):
        key = f"{state_key}_{kategori_key}_{i}"
        if st.session_state[state_key].get(key, False):
            kat_uyumlu += 1
    kat_oran = round(100 * kat_uyumlu / kat_toplam, 1) if kat_toplam else 0
    rapor += f"\n### {kategori_ad} (%{kat_oran})\n\n"
    for i, madde in enumerate(maddeler):
        key = f"{state_key}_{kategori_key}_{i}"
        durum = "✅" if st.session_state[state_key].get(key, False) else "❌"
        rapor += f"- {durum} {madde}\n"

st.download_button(
    label=t("standartlar.rapor_indir"),
    data=rapor.encode("utf-8"),
    file_name=f"{secili_standart.replace(' ', '_')}_rapor_{datetime.now().strftime('%Y%m%d')}.md",
    mime="text/markdown",
    use_container_width=True,
)

st.markdown("---")
st.caption(t("standartlar.not"))
