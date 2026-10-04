"""
Plan Yukseltme sayfasi
- Mevcut plan gosterimi
- Plan secimi (Pro / Enterprise)
- Fatura bilgileri + odeme yontemi
- Talep gonder -> DB'ye kayit + admin bildirimi
"""
import streamlit as st
from datetime import datetime

import auth
auth.giris_gerekli()

import db
from i18n import t
from cache_utils import cache_temizle

db.init_db()

kullanici = auth.mevcut_kullanici()
kullanici_adi = kullanici.get("kullanici_adi", "-")
firma_adi = auth.firma_adi() or "-"

st.title("💎 " + t("yukselt.baslik"))
st.markdown(t("yukselt.aciklama"))
st.markdown("---")

# ============================================================
# 1) MEVCUT PLAN
# ============================================================
limit_bilgi = db.limit_kontrol(kullanici_adi)
mevcut_plan = limit_bilgi.get("plan", "free")

col1, col2, col3 = st.columns(3)
col1.metric(t("yukselt.mevcut_plan"), t(f"plan.{mevcut_plan}"))
col2.metric(t("yukselt.bu_ay_kullanim"), f"{limit_bilgi.get('kullanilan', 0)}/{limit_bilgi.get('limit', 0)}")
if limit_bilgi.get("kalan", 0) == -1:
    col3.metric(t("yukselt.kalan"), "∞")
else:
    col3.metric(t("yukselt.kalan"), limit_bilgi.get("kalan", 0))

st.markdown("---")

# ============================================================
# 2) BEKLEYEN TALEP VAR MI?
# ============================================================
bekleyenler = db.yukseltme_listele(durum="bekliyor")
kendi_bekleyen = [b for b in bekleyenler if b.get("kullanici_adi") == kullanici_adi]

if kendi_bekleyen:
    talep = kendi_bekleyen[0]
    st.info(f"⏳ **{t('yukselt.bekleyen_baslik')}**")
    st.write(f"**{t('yukselt.istenen_plan')}:** {t(f'plan.{talep['istenen_plan']}')}")
    st.write(f"**{t('yukselt.tarih')}:** {talep['olusturma']}")
    st.caption(t("yukselt.bekleyen_aciklama"))
    st.stop()

# ============================================================
# 3) PLAN KARSILASTIRMA
# ============================================================
st.subheader("📊 " + t("yukselt.karsilastirma"))

planlar = [
    {"kod": "free", "ad": t("plan.free"), "fiyat": "0", "limit": "3"},
    {"kod": "pro", "ad": t("plan.pro"), "fiyat": "12.900 TL", "limit": "100"},
    {"kod": "enterprise", "ad": t("plan.enterprise"), "fiyat": "39.900 TL", "limit": "∞"},
]

cols = st.columns(3)
for i, p in enumerate(planlar):
    with cols[i]:
        secili = p["kod"] == mevcut_plan
        baslik = f"**{p['ad']}**"
        if secili:
            baslik += " ✅"
        st.markdown(baslik)
        st.markdown(f"### {p['fiyat']}")
        st.caption(f"{p['limit']} {t('yukselt.denetim_ay')}")

st.markdown("---")

# ============================================================
# 4) YUKSELTME FORMU
# ============================================================
st.subheader("🚀 " + t("yukselt.form_baslik"))
st.caption(t("yukselt.form_aciklama"))

# Mevcut plan haric
secilabilir = [p for p in planlar if p["kod"] != mevcut_plan and p["kod"] != "free"]

if not secilabilir:
    st.info(t("yukselt.zaten_premium"))
    st.stop()

with st.form("yukseltme_formu"):
    istenen_plan = st.selectbox(
        t("yukselt.istenen_plan") + " *",
        [p["kod"] for p in secilabilir],
        format_func=lambda x: next(p["ad"] for p in secilabilir if p["kod"] == x),
    )

    st.markdown(f"**{t('yukselt.fatura_bilgi')}**")

    fatura_ad = st.text_input(t("yukselt.fatura_ad") + " *", value=kullanici.get("ad_soyad") or "")
    fatura_sirket = st.text_input(t("yukselt.fatura_sirket"), value=firma_adi)
    fatura_vergi = st.text_input(t("yukselt.fatura_vergi"), placeholder="1234567890")
    fatura_adres = st.text_area(t("yukselt.fatura_adres"), height=80)
    fatura_eposta = st.text_input(t("yukselt.fatura_eposta") + " *", value=kullanici.get("eposta") or "")

    st.markdown(f"**{t('yukselt.odeme_yontemi')}**")
    odeme = st.radio(
        t("yukselt.odeme_secim"),
        ["havale", "kredi_karti", "fatura"],
        format_func=lambda x: t(f"yukselt.odeme_{x}"),
        horizontal=True,
    )

    notlar = st.text_area(t("yukselt.notlar"), height=60)

    onay = st.checkbox(t("yukselt.onay"))

    submit = st.form_submit_button(
        "🚀 " + t("yukselt.gonder_btn"),
        type="primary",
        use_container_width=True,
    )

    if submit:
        if not fatura_ad or not fatura_eposta:
            st.error(t("yukselt.hata_zorunlu"))
        elif not onay:
            st.error(t("yukselt.hata_onay"))
        else:
            fatura_bilgi = (
                f"Ad: {fatura_ad} | Sirket: {fatura_sirket} | "
                f"Vergi: {fatura_vergi} | Adres: {fatura_adres} | "
                f"Eposta: {fatura_eposta}"
            )

            sonuc = db.yukseltme_talep_ekle(
                kullanici_adi=kullanici_adi,
                istenen_plan=istenen_plan,
                odeme_yontemi=odeme,
                fatura_bilgi=fatura_bilgi,
                notlar=notlar,
            )

            if sonuc.get("durum") == "OK":
                # Audit log
                try:
                    db.audit_kaydet(
                        eylem="yukseltme_talebi",
                        kullanici_adi=kullanici_adi,
                        firma_id=auth.firma_id(),
                        detay=f"Istenen: {istenen_plan} | Odeme: {odeme} | Talep: {sonuc['talep_id']}",
                    )
                except Exception:
                    pass

                try:
                    cache_temizle()
                except Exception:
                    pass

                st.success("✅ " + t("yukselt.basari"))
                st.info(t("yukselt.basari_aciklama"))
                st.balloons()
                st.rerun()
            else:
                st.error(f"❌ {sonuc.get('mesaj', 'Hata')}")

# ============================================================
# 5) ILETISIM
# ============================================================
st.markdown("---")
st.caption(f"📧 {t('yukselt.iletisim')}: info@veraxio.ai")