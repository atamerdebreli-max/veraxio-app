"""
sayfa_ekip.py - Ekip yonetimi (firma admini icin)
Davet gonderme, ekip listeleme
"""
import streamlit as st
import db
import auth
from i18n import t


# Giris + firma kontrolu
auth.giris_gerekli()
auth.firma_gerekli()

kullanici = auth.mevcut_kullanici()
firma_id = auth.firma_id()
firma = db.firma_bul(firma_id)

st.title("👥 " + t("ekip.baslik"))
st.markdown(f"**{firma['firma_adi'] if firma else ''}**")
st.markdown("---")

# Yetki kontrolu
if not auth.firma_yoneticisi_mi():
    st.warning("⚠️ Bu sayfayi gormek icin firma yoneticisi olmalisiniz.")
    st.stop()


# ============================================================
# EKIP LISTESI
# ============================================================
st.subheader("👥 " + t("ekip.mevcut_uyeler"))

uyeler = db.firma_kullanicilari(firma_id)

if not uyeler:
    st.info("Henuz ekip uyesi yok.")
else:
    for uye in uyeler:
        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
        with col1:
            st.write(f"**{uye.get('ad_soyad', 'Isimsiz')}**")
            st.caption(f"@{uye['kullanici_adi']}")
        with col2:
            st.write(uye.get("eposta", "-"))
        with col3:
            rol = uye.get("firma_rol", "user").upper()
            if rol == "ADMIN":
                st.success(f"🔑 {rol}")
            else:
                st.info(f"👤 {rol}")
        with col4:
            # Kendini silemez
            if uye["kullanici_adi"] != kullanici["kullanici_adi"]:
                if st.button("🗑️", key=f"sil_{uye['id']}", help="Sil"):
                    # Kullanici silme fonksiyonu
                    try:
                        with db._baglanti() as conn:
                            conn.execute("DELETE FROM users WHERE id = ?", (uye["id"],))
                            conn.commit()
                        st.success(f"Silindi: {uye['kullanici_adi']}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Hata: {str(e)[:60]}")


st.markdown("---")


# ============================================================
# YENI DAVET
# ============================================================
st.subheader("📨 " + t("ekip.davet_gonder"))

with st.form("davet_formu"):
    col1, col2 = st.columns(2)
    with col1:
        davet_eposta = st.text_input(t("ekip.davet_eposta") + " *", placeholder="ahmet@sirket.com")
    with col2:
        davet_rol = st.selectbox(
            t("ekip.davet_rol"),
            ["user", "admin"],
            format_func=lambda x: t(f"ekip.rol_{x}"),
        )

    submit = st.form_submit_button(t("ekip.davet_btn"), use_container_width=True, type="primary")

    if submit:
        if not davet_eposta:
            st.error(t("ekip.davet_eposta_zorunlu"))
        elif "@" not in davet_eposta:
            st.error(t("ekip.davet_eposta_gecersiz"))
        else:
            token = db.davet_olustur(
                firma_id=firma_id,
                eposta=davet_eposta,
                rol=davet_rol,
                gonderen=kullanici["kullanici_adi"],
            )

            if token:
                davet_linki = f"http://localhost:8501/?davet={token}"
                st.success("✅ " + t("ekip.davet_olusturuldu"))
                st.markdown("**" + t("ekip.davet_linki") + ":**")
                st.code(davet_linki, language="text")
                st.caption(t("ekip.davet_linki_aciklama"))
            else:
                st.warning(t("ekip.davet_zaten_var"))


st.markdown("---")


# ============================================================
# BEKLEYEN DAVETLER
# ============================================================
st.subheader("⏳ " + t("ekip.bekleyen_davetler"))

davetler = db.davet_listele(firma_id)
bekleyenler = [d for d in davetler if d["durum"] == "bekliyor"]

if not bekleyenler:
    st.info(t("ekip.bekleyen_yok"))
else:
    for davet in bekleyenler:
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            st.write(f"📧 **{davet['eposta']}**")
            st.caption(f"Rol: {davet.get('rol', 'user').upper()}")
        with col2:
            st.caption(f"Gonderen: {davet.get('gonderen', '-')}")
            st.caption(f"Tarih: {davet.get('olusturma', '-')}")
        with col3:
            if st.button("❌", key=f"iptal_{davet['id']}", help="Iptal"):
                db.davet_iptal_et(davet["id"])
                st.success("Davet iptal edildi.")
                st.rerun()