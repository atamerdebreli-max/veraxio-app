"""
login.py - Giris ve kayit sayfasi (coklu dil destekli + Google SSO)
"""
import streamlit as st
import db
import auth
import auth_2fa
from i18n import t


db.init_db()
auth.ilk_kullanici_olustur()


# ============================================================
# GOOGLE OAUTH CALLBACK (en basta)
# ============================================================
_qp_login = dict(st.query_params)
if "code" in _qp_login and "google_oauth_state" in st.session_state:
    try:
        import auth_google
        with st.spinner("🔵 Google ile giriş yapılıyor..."):
            _g_sonuc = auth_google.google_callback(_qp_login["code"])

        if _g_sonuc.get("durum") == "OK":
            _k = _g_sonuc.get("kullanici", {})
            # Auth sistemine giris yap
            auth.google_ile_giris_yap(_k)
            st.query_params.clear()
            st.success("✅ Google ile giriş başarılı!")
            st.rerun()
        else:
            st.error("❌ " + _g_sonuc.get("mesaj", "Google giriş hatası"))
    except Exception as _e:
        st.error("❌ Google giriş hatası: " + str(_e))


# ============================================================
# SIFRE SIFIRLAMA VE DOGRULAMA (session_state uzerinden)
# ============================================================
sifre_token = st.session_state.get("sifre_token", None)
dogrulama_token = st.session_state.get("dogrulama_token", None)


# --- SIFRE SIFIRLAMA SAYFASI ---
if sifre_token:
    st.markdown("## 🔑 " + t("login.sifre_sifirla_baslik"))
    st.markdown("---")

    token_kayit = db.token_bul(sifre_token, tip="sifre_sifirlama")

    if not token_kayit:
        st.error(t("login.sifre_token_gecersiz"))
        if st.button("← Ana Sayfa"):
            del st.session_state["sifre_token"]
            st.rerun()
    else:
        st.info(t("login.sifre_kullanici") + f" **{token_kayit['kullanici_adi']}**")

        with st.form("sifre_sifirla_formu"):
            yeni_sifre = st.text_input(t("login.yeni_sifre") + " *", type="password", placeholder="En az 6 karakter")
            yeni_sifre2 = st.text_input(t("login.yeni_sifre") + " 2 *", type="password")
            submit_sifre = st.form_submit_button(t("login.sifre_sifirla_btn"), use_container_width=True, type="primary")

            if submit_sifre:
                if not yeni_sifre:
                    st.error(t("login.zorunlu"))
                elif auth.sifre_kontrol(yeni_sifre)["durum"] != "OK":
                    st.error("❌ " + auth.sifre_kontrol(yeni_sifre)["hata"])
                elif yeni_sifre != yeni_sifre2:
                    st.error(t("login.sifre_eslesmiyor"))
                else:
                    sonuc = auth.sifre_sifirla(sifre_token, yeni_sifre)
                    if sonuc["durum"] == "OK":
                        st.success(t("login.sifre_sifirlandi"))
                        st.info(t("login.giris_yapabilirsiniz"))
                        if "sifre_token" in st.session_state:
                            del st.session_state["sifre_token"]
                    else:
                        st.error("❌ " + sonuc.get("hata", ""))

    st.stop()


# --- EMAIL DOGRULAMA SAYFASI ---
if dogrulama_token:
    st.markdown("## ✅ " + t("login.dogrulama_baslik"))
    st.markdown("---")

    sonuc = auth.email_dogrula(dogrulama_token)
    if sonuc["durum"] == "OK":
        st.success(t("login.dogrulama_basarili"))
        st.info(t("login.giris_yapabilirsiniz"))
        if "dogrulama_token" in st.session_state:
            del st.session_state["dogrulama_token"]
    else:
        st.error("❌ " + sonuc.get("hata", ""))

    st.stop()


# ============================================================
# ZATEN GIRIS YAPILDIYSA
# ============================================================
if auth.giris_yapildi_mi():
    kullanici = auth.mevcut_kullanici()
    st.success(t("login.zaten_giris") + f" **{kullanici['ad_soyad'] or kullanici['kullanici_adi']}**")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(t("login.rol"), kullanici.get("rol", "user").upper())
    with col2:
        st.metric(t("login.eposta"), kullanici.get("eposta", "-"))
    with col3:
        st.metric(t("login.firma"), kullanici.get("firma_adi", "-") or "-")

    st.markdown("---")
    st.info(t("login.sol_menu"))

    # ============================================================
    # 2FA KURULUMU
    # ============================================================
    st.markdown("---")
    st.subheader("🔐 " + t("login.2fa_yonetim"))

    kullanici_adi_mevcut = kullanici["kullanici_adi"]
    iki_fa_aktif = auth_2fa.iki_fa_gerekli_mi(kullanici_adi_mevcut)

    if iki_fa_aktif:
        st.success("✅ " + t("login.2fa_aktif_mesaj"))

        with st.expander("🔓 " + t("login.2fa_kapat")):
            kapat_sifre = st.text_input(
                t("login.sifre"),
                type="password",
                key="2fa_kapat_sifre",
            )
            if st.button(t("login.2fa_kapat_btn"), key="2fa_kapat_btn"):
                sonuc = auth_2fa.iki_fa_kapat(kullanici_adi_mevcut, kapat_sifre)
                if sonuc["durum"] == "OK":
                    st.success("✅ " + t("login.2fa_kapatildi"))
                    st.rerun()
                else:
                    st.error("❌ " + sonuc.get("hata", ""))

    else:
        st.warning("⚠️ " + t("login.2fa_pasif_mesaj"))

        if st.button("🔐 " + t("login.2fa_baslat_btn"), type="primary", key="2fa_baslat_btn"):
            kurulum = auth_2fa.iki_fa_baslat(kullanici_adi_mevcut)
            st.session_state["2fa_kurulum_goster"] = True

        if st.session_state.get("2fa_kurulum_goster"):
            secret = st.session_state.get("2fa_setup_secret")
            if secret:
                qr_data = auth_2fa.qr_kodu_olustur(kullanici_adi_mevcut, secret)

                st.markdown("**" + t("login.2fa_adim1") + "**")
                st.caption(t("login.2fa_adim1_aciklama"))

                if qr_data:
                    st.markdown(
                        f'<div style="text-align:center;"><img src="{qr_data}" width="220"></div>',
                        unsafe_allow_html=True,
                    )

                st.markdown("**" + t("login.2fa_adim2") + "**")
                st.code(secret, language="text")

                st.markdown("**" + t("login.2fa_adim3") + "**")

                with st.form("2fa_kurulum_formu"):
                    kod_kurulum = st.text_input(
                        t("login.2fa_kod"),
                        placeholder="123456",
                        max_chars=6,
                        key="2fa_kurulum_kod",
                    )
                    submit_kurulum = st.form_submit_button(
                        "✅ " + t("login.2fa_aktiflestir_btn"),
                        use_container_width=True,
                        type="primary",
                    )

                    if submit_kurulum:
                        sonuc = auth_2fa.iki_fa_dogrula_ve_aktiflestir(
                            kullanici_adi_mevcut, kod_kurulum
                        )
                        if sonuc["durum"] == "OK":
                            st.success("✅ " + t("login.2fa_aktiflestirildi"))
                            st.session_state["2fa_kurulum_goster"] = False
                            st.rerun()
                        else:
                            st.error("❌ " + sonuc.get("hata", ""))

    if st.button(t("login.cikis_btn"), type="secondary", use_container_width=True):
        auth.cikis_yap()
        st.rerun()

    st.stop()


# ============================================================
# GIRIS / KAYIT FORMU
# ============================================================
st.markdown(f"## {t('login.baslik')}")
st.markdown(f"*{t('login.alt_baslik')}*")
st.markdown("---")

# Aktif tab kontrolu (landing'den gelindiyse)
if "login_tab" not in st.session_state:
    st.session_state["login_tab"] = "giris"

_aktif_tab = st.session_state.get("login_tab", "giris")
_tab_secenekleri = [t("login.tab_giris"), t("login.tab_kayit")]
_tab_index = 0 if _aktif_tab == "giris" else 1

_tab_secim = st.radio(
    "_login_tab_radio",
    _tab_secenekleri,
    index=_tab_index,
    horizontal=True,
    label_visibility="collapsed",
    key="_login_tab_radio_key",
)

if _tab_secim == t("login.tab_giris"):
    st.session_state["login_tab"] = "giris"
else:
    st.session_state["login_tab"] = "kayit"


# --- GIRIS ---
if st.session_state["login_tab"] == "giris":
    # ============================================================
    # GOOGLE ILE GIRIS BUTONU
    # ============================================================
    try:
        import auth_google
        _g_url = auth_google.google_giris_url()
        if _g_url:
            st.markdown(
                f'<a href="{_g_url}" target="_self" '
                f'style="display:flex;align-items:center;justify-content:center;gap:10px;'
                f'padding:12px;background:#fff;color:#333;border:1px solid #dadce0;'
                f'border-radius:8px;text-decoration:none;font-weight:600;font-size:15px;'
                f'margin-bottom:8px;">'
                f'<svg width="18" height="18" viewBox="0 0 48 48"><path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/><path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/><path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/><path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/></svg>'
                f'Google ile Giriş Yap</a>',
                unsafe_allow_html=True,
            )
            st.markdown(
                '<div style="text-align:center;color:#888;margin:12px 0;font-size:13px;">— veya —</div>',
                unsafe_allow_html=True,
            )
    except Exception as _e:
        print(f"[Google] Buton yuklenemedi: {_e}")

    # ============================================================
    # NORMAL GIRIS FORMU
    # ============================================================
    with st.form("giris_formu"):
        kullanici_adi = st.text_input(t("login.kullanici_adi"), placeholder="admin")
        sifre = st.text_input(t("login.sifre"), type="password", placeholder="••••••••")
        submit = st.form_submit_button(t("login.giris_btn"), use_container_width=True, type="primary")

        if submit:
            if not kullanici_adi or not sifre:
                st.error(t("login.zorunlu"))
            else:
                # 2FA aktif mi kontrol et
                iki_fa_aktif = auth_2fa.iki_fa_gerekli_mi(kullanici_adi)

                if iki_fa_aktif:
                    st.session_state["2fa_bekleyen_kullanici"] = kullanici_adi
                    st.session_state["2fa_bekleyen_sifre"] = sifre
                    st.rerun()
                else:
                    _kilit = db.giris_kilitli_mi(kullanici_adi)
                    if _kilit.get("kilitli"):
                        _kalan = _kilit.get("kalan_dk", 0)
                        st.error(f"🔒 Hesabiniz gecici olarak kilitli. {_kalan} dakika sonra tekrar deneyin.")
                        st.stop()

                    sonuc = auth.giris_yap(kullanici_adi, sifre)
                    if sonuc["durum"] == "OK":
                        db.giris_denemesi_kaydet(kullanici_adi, basarili=True)
                        st.success(t("login.giris_basarili"))
                        st.rerun()
                    else:
                        db.giris_denemesi_kaydet(kullanici_adi, basarili=False)
                        _kalan_hak = db.kalan_deneme_hakki(kullanici_adi)
                        if _kalan_hak > 0:
                            st.error(t("login.giris_hata") + f" ({_kalan_hak} hakkiniz kaldi)")
                        else:
                            st.error("🔒 Hesabiniz 15 dakika kilitlendi. Lutfen sonra tekrar deneyin.")
                        st.stop()

    # 2FA ADIMI
    if st.session_state.get("2fa_bekleyen_kullanici"):
        st.markdown("---")
        st.subheader("🔐 " + t("login.2fa_baslik"))
        st.caption(t("login.2fa_aciklama"))

        bekleyen = st.session_state["2fa_bekleyen_kullanici"]

        with st.form("2fa_formu"):
            kod = st.text_input(
                t("login.2fa_kod"),
                placeholder="123456",
                max_chars=6,
                key="2fa_kod_input",
            )
            submit_2fa = st.form_submit_button(
                "🔐 " + t("login.2fa_dogrula_btn"),
                use_container_width=True,
                type="primary",
            )

            if submit_2fa:
                sonuc = auth_2fa.iki_fa_dogrula_giris(bekleyen, kod)
                if sonuc["durum"] == "OK":
                    sifre_bekleyen = st.session_state.get("2fa_bekleyen_sifre", "")
                    sonuc_giris = auth.giris_yap(bekleyen, sifre_bekleyen)

                    if "2fa_bekleyen_kullanici" in st.session_state:
                        del st.session_state["2fa_bekleyen_kullanici"]
                    if "2fa_bekleyen_sifre" in st.session_state:
                        del st.session_state["2fa_bekleyen_sifre"]

                    if sonuc_giris["durum"] == "OK":
                        st.success(t("login.giris_basarili"))
                        st.rerun()
                    else:
                        st.error(t("login.giris_hata"))
                else:
                    st.error("❌ " + sonuc.get("hata", "Kod gecersiz"))

        if st.button("← " + t("login.2fa_iptal")):
            if "2fa_bekleyen_kullanici" in st.session_state:
                del st.session_state["2fa_bekleyen_kullanici"]
            if "2fa_bekleyen_sifre" in st.session_state:
                del st.session_state["2fa_bekleyen_sifre"]
            st.rerun()

        st.stop()

    # Sifremi unuttum
    st.markdown("---")
    with st.expander("🔑 " + t("login.sifremi_unuttum")):
        sifre_email = st.text_input(t("login.sifre_email_label"), placeholder="ahmet@sirket.com", key="sifre_email_input_k")
        if st.button(t("login.sifre_gonder_btn"), key="sifre_gonder_btn_k", use_container_width=True):
            if not sifre_email:
                st.error(t("login.zorunlu"))
            else:
                dil = st.session_state.get("dil", "tr")
                sonuc = auth.sifre_sifirlama_baslat(sifre_email, dil=dil)
                st.success(t("login.sifre_email_gonderildi"))

    st.markdown("---")
    st.caption(t("login.demo_hesap") + " `admin` / `admin123`")


# --- KAYIT ---
if st.session_state["login_tab"] == "kayit":
    st.markdown(t("login.yeni_firma"))

    davet_token = st.query_params.get("davet", None)

    if davet_token:
        davet = db.davet_bul(davet_token)
        if davet:
            st.info(f"📨 **{davet['firma_adi']}** " + t("login.davet_baslik"))

            with st.form("davet_formu"):
                dav_kullanici = st.text_input(t("login.kullanici_adi") + " *")
                dav_ad = st.text_input(t("login.ad_soyad"))
                dav_sifre = st.text_input(t("login.sifre") + " *", type="password")
                dav_sifre2 = st.text_input(t("login.sifre") + " 2 *", type="password")
                submit_davet = st.form_submit_button(t("login.davet_kabul_btn"), use_container_width=True, type="primary")

                if submit_davet:
                    if not dav_kullanici or not dav_sifre:
                        st.error(t("login.zorunlu"))
                    else:
                        _sk2 = auth.sifre_kontrol(dav_sifre)
                        if _sk2["durum"] != "OK":
                            st.error("❌ " + _sk2["hata"])
                            st.stop()
                        if dav_sifre != dav_sifre2:
                            st.error(t("login.sifre_eslesmiyor"))
                            st.stop()
                        sonuc = auth.davet_kabul_et_ve_kayit_ol(
                            token=davet_token,
                            kullanici_adi=dav_kullanici,
                            sifre=dav_sifre,
                            ad_soyad=dav_ad,
                        )
                        if sonuc["durum"] == "OK":
                            st.success(t("login.davet_basarili"))
                        else:
                            st.error("❌ " + sonuc.get("hata", ""))
        else:
            st.error(t("login.davet_gecersiz"))
        st.stop()

    with st.form("firma_formu"):
        st.markdown(f"### 🏢 {t('login.firma_bilgi')}")
        firma_adi = st.text_input(t("login.firma_adi") + " *", placeholder="ABC Teknoloji A.S.")
        firma_sektor = st.text_input(t("login.firma_sektor"))
        firma_vergi = st.text_input(t("login.firma_vergi"))

        st.markdown("---")
        st.markdown(f"### 👤 {t('login.yonetici_bilgi')}")
        yeni_ad = st.text_input(t("login.ad_soyad") + " *")
        yeni_kullanici = st.text_input(t("login.kullanici_adi") + " *")
        yeni_email = st.text_input(t("login.eposta") + " *")
        yeni_sifre = st.text_input(t("login.sifre") + " *", type="password")
        yeni_sifre2 = st.text_input(t("login.sifre") + " 2 *", type="password")

        submit_kayit = st.form_submit_button(t("login.firma_btn"), use_container_width=True, type="primary")

        if submit_kayit:
            if not firma_adi or not yeni_kullanici or not yeni_sifre:
                st.error(t("login.firma_zorunlu"))
            else:
                _sk = auth.sifre_kontrol(yeni_sifre)
                if _sk["durum"] != "OK":
                    st.error("❌ " + _sk["hata"])
                    st.stop()
                if yeni_sifre != yeni_sifre2:
                    st.error(t("login.sifre_eslesmiyor"))
                    st.stop()
                firma_id = db.firma_ekle(
                    firma_adi=firma_adi,
                    vergi_no=firma_vergi,
                    sektor=firma_sektor,
                )
                sifre_h = auth.sifre_hashle(yeni_sifre)
                basarili = db.kullanici_ekle_firma(
                    kullanici_adi=yeni_kullanici,
                    sifre_hash=sifre_h,
                    ad_soyad=yeni_ad,
                    eposta=yeni_email,
                    firma_id=firma_id,
                    firma_rol="admin",
                    rol="user",
                )
                if basarili:
                    try:
                        _dil = st.session_state.get("dil", "tr")
                        _email_sonuc = auth.email_dogrulama_gonder(yeni_kullanici, yeni_email, _dil)
                        if _email_sonuc.get("durum") == "OK":
                            st.info("📧 " + t("login.email_dogrulama_gonderildi").format(email=yeni_email))
                        else:
                            print(f"[Kayit] Email gonderilemedi: {_email_sonuc}")
                    except Exception as _e:
                        print(f"[Kayit] Email hatasi: {_e}")

                    try:
                        trial_sonuc = db.trial_baslat(yeni_kullanici)
                        if trial_sonuc["durum"] == "OK":
                            st.success(
                                "🎁 **7 gün ücretsiz deneme** başlatıldı! "
                                f"({trial_sonuc['bitis'][:10]} tarihine kadar)"
                            )
                    except Exception as e:
                        print(f"[Kayit] Trial hatasi: {e}")

                    try:
                        from cache_utils import cache_temizle
                        cache_temizle()
                    except Exception:
                        pass

                    st.success(f"✅ **{firma_adi}** " + t("login.firma_basarili"))
                    st.info(t("login.firma_sonra_giris"))
                    st.warning("⚠️ " + t("login.email_dogrulama_gerekli"))
                else:
                    db.firma_sil(firma_id)
                    st.error(t("login.kullanici_alindi"))


# ============================================================
# HUKUKI LINKLER (footer)
# ============================================================
st.markdown("---")
with st.container():
    c1, c2, c3 = st.columns(3)
    with c1:
        st.caption("🔒 " + t("hukuki.tab_gizlilik"))
    with c2:
        st.caption("🛡️ " + t("hukuki.tab_kvkk"))
    with c3:
        st.caption("📜 " + t("hukuki.tab_kullanim"))
    st.caption(t("hukuki.footer"))
