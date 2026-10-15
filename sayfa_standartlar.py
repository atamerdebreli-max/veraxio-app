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
# STANDARTLAR
# ============================================================
STANDARTLAR = {
    "ISO 42001": {
        "aciklama": "Yapay Zeka Yönetim Sistemi (AIMS) - Uluslararası Standart",
        "kategoriler": {
            "Bağlam ve Liderlik": [
                "AI politikası tanımlanmış ve onaylanmış",
                "AI rolleri ve sorumlulukları belirlenmiş",
                "AI riskleri için yönetim taahhüdü var",
                "AI etik kurulu oluşturulmuş",
            ],
            "Planlama": [
                "AI riskleri ve fırsatları tanımlanmış",
                "AI hedefleri ölçülebilir şekilde belirlenmiş",
                "Yasal ve düzenleyici gereksinimler belirlenmiş",
                "Risk değerlendirme metodolojisi var",
            ],
            "Destek": [
                "AI ekibi için eğitim planı var",
                "AI farkındalık programı mevcut",
                "İletişim planı tanımlanmış",
                "Dokümantasyon sistemi kurulmuş",
            ],
            "Operasyon": [
                "AI risk değerlendirmesi düzenli yapılıyor",
                "AI sistemleri envanteri tutuluyor",
                "Değişiklik yönetimi süreci var",
                "Tedarikçi yönetimi yapılıyor",
            ],
            "Performans Değerlendirme": [
                "AI performansı izleniyor",
                "İç denetimler yapılıyor",
                "Yönetim gözden geçirmesi yapılıyor",
                "Uygunsuzluklar kayıt altına alınıyor",
            ],
            "İyileştirme": [
                "Sürekli iyileştirme süreci var",
                "Düzeltici aksiyonlar takip ediliyor",
                "Öğrenilen dersler kaydediliyor",
            ],
        },
    },
    "NIST AI RMF": {
        "aciklama": "AI Risk Yönetim Çerçevesi - ABD Ulusal Standartlar Enstitüsü",
        "kategoriler": {
            "GOVERN (Yönetişim)": [
                "AI risk yönetimi politikası oluşturulmuş",
                "Roller ve sorumluluklar tanımlanmış",
                "AI risk kültürü teşvik ediliyor",
                "Paydaş katılımı sağlanıyor",
                "Yasal gereksinimler izleniyor",
            ],
            "MAP (Haritalama)": [
                "AI sistemleri kategorize edilmiş",
                "Kullanım senaryoları belgelenmiş",
                "Etkilenen paydaşlar tanımlanmış",
                "Riskler ve faydalar haritalanmış",
            ],
            "MEASURE (Ölçüm)": [
                "AI performansı ölçülüyor",
                "Doğruluk ve güvenilirlik test ediliyor",
                "Bias ve adillik değerlendiriliyor",
                "Güvenlik açıkları test ediliyor",
                "Şeffaflık ve açıklanabilirlik sağlanıyor",
            ],
            "MANAGE (Yönetim)": [
                "Risk önceliklendirmesi yapılıyor",
                "Risk azaltma stratejileri uygulanıyor",
                "Olay müdahale planı hazırlanmış",
                "Sürekli izleme mekanizması var",
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

for kategori, maddeler in std["kategoriler"].items():
    st.markdown(f"### 🔹 {kategori}")
    for i, madde in enumerate(maddeler):
        key = f"{state_key}_{kategori}_{i}"
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
for kategori, maddeler in std["kategoriler"].items():
    kat_toplam = len(maddeler)
    kat_uyumlu = 0
    for i in range(kat_toplam):
        key = f"{state_key}_{kategori}_{i}"
        if st.session_state[state_key].get(key, False):
            kat_uyumlu += 1
    kat_oran = round(100 * kat_uyumlu / kat_toplam, 1) if kat_toplam else 0
    emoji = "🟢" if kat_oran >= 80 else ("🟡" if kat_oran >= 50 else "🔴")
    st.markdown(f"{emoji} **{kategori}**: {kat_uyumlu}/{kat_toplam} (%{kat_oran})")

# ============================================================
# RAPOR INDIR
# ============================================================
st.markdown("---")

rapor = f"""# {secili_standart} UYUMLULUK RAPORU

**Şirket:** {kullanici.get('ad_soyad') or kullanici.get('kullanici_adi', '-')}
**Tarih:** {datetime.now().strftime('%d.%m.%Y %H:%M')}
**Standart:** {secili_standart}
**Genel Uyum:** %{uyum_orani}

---

## GENEL SONUC

- Toplam Madde: {toplam_madde}
- Uyumlu: {isaretlenen}
- Uyumsuz: {toplam_madde - isaretlenen}
- Uyum Oranı: %{uyum_orani}

---

## KATEGORI DETAYLARI

"""

for kategori, maddeler in std["kategoriler"].items():
    kat_toplam = len(maddeler)
    kat_uyumlu = 0
    for i in range(kat_toplam):
        key = f"{state_key}_{kategori}_{i}"
        if st.session_state[state_key].get(key, False):
            kat_uyumlu += 1
    kat_oran = round(100 * kat_uyumlu / kat_toplam, 1) if kat_toplam else 0
    rapor += f"\n### {kategori} (%{kat_oran})\n\n"
    for i, madde in enumerate(maddeler):
        key = f"{state_key}_{kategori}_{i}"
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
