"""
Ana uygulama - Streamlit navigasyon
"""
import streamlit as st


# ============================================================
# LOG SISTEMI
# ============================================================
import sys
import traceback
import logger as _logger_mod

_log = _logger_mod.log_al("main")

def _global_exception_handler(exc_type, exc_value, exc_tb):
    """Yakalanmamis hatalari log'a yazar."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_tb)
        return
    _log.error(
        "YAKALANMAMIS HATA: %s\n%s",
        exc_value,
        "".join(traceback.format_exception(exc_type, exc_value, exc_tb)),
    )

sys.excepthook = _global_exception_handler
@st.cache_resource
def _startup_log():
    """Uygulama baslarken 1 kez log yazar."""
    _log.info("=== Uygulama baslatildi ===")
    return True

_startup_log()

st.set_page_config(
    page_title="AI Uyumluluk Denetimi",
    page_icon="🔍",
    layout="wide"
)

# ============================================================
# QUERY PARAM YAKALAYICI (sifre sifirlama + email dogrulama)
# ============================================================
_qp = dict(st.query_params)

_onemli_parametre_var = False

if "sifre_sifirla" in _qp:
    st.session_state["sifre_token"] = _qp["sifre_sifirla"]
    _onemli_parametre_var = True

if "email_dogrula" in _qp:
    st.session_state["dogrulama_token"] = _qp["email_dogrula"]
    _onemli_parametre_var = True

if "davet" in _qp:
    _onemli_parametre_var = True  # davet_token login.py'de query_params'tan okunuyor
# ============================================================
# LANDING PAGE (giris yapilmamissa goster)
# ============================================================
if "landing_goster" not in st.session_state:
    st.session_state["landing_goster"] = True

# Giris yapildiysa landing'i kapat
try:
    import auth as _auth_landing
    if _auth_landing.giris_yapildi_mi():
        st.session_state["landing_goster"] = False
except Exception:
    pass

# Landing gosterilecekse, goster ve dur
if st.session_state["landing_goster"] and not _onemli_parametre_var:
    import landing_embed
    landing_embed.goster()
    st.stop()
# auth + session importlari (erken)
import auth as _auth
import session_manager

# i18n baslat
import i18n
from i18n import t, dil_secici

# Session state baslangic
if "dil" not in st.session_state:
    st.session_state["dil"] = "tr"

# Dil secici - EN BASTA cagir ki sayfa basliklari dogru hesaplansin
dil_secici()

# ============================================================
# SESSION TIMEOUT KONTROLU
# ============================================================
if _auth.giris_yapildi_mi():
    session_manager.session_kontrol()

# Tema uygula (dark mode CSS)
import tema
tema.tema_uygula()
# Navigasyon - basliklar i18n'den (dil secici cagrildiktan sonra)
sayfa_tek = st.Page("sayfa_tek.py", title=t("menu.tek_denetim"), icon="🔍", default=True)
sayfa_toplu = st.Page("sayfa_toplu.py", title=t("menu.toplu_denetim"), icon="📂")
sayfa_gecmis = st.Page("sayfa_gecmis.py", title=t("menu.gecmis"), icon="📜")
sayfa_dashboard = st.Page("sayfa_dashboard.py", title=t("menu.dashboard"), icon="📊")
sayfa_hesabim = st.Page("sayfa_hesabim.py", title=t("menu.hesabim"), icon="👤")
sayfa_yukselt = st.Page("sayfa_yukselt.py", title=t("menu.yukselt"), icon="💎")
sayfa_hukuki = st.Page("sayfa_hukuki.py", title=t("menu.hukuki"), icon="⚖️")
sayfa_zamanlanmis = st.Page("sayfa_zamanlanmis.py", title=t("menu.zamanlanmis"), icon="⏰")
sayfa_login = st.Page("login.py", title=t("menu.login"), icon="🔐")
sayfa_onboarding = st.Page("sayfa_onboarding.py", title=t("menu.onboarding"), icon="👋")
sayfa_ekip = st.Page("sayfa_ekip.py", title=t("menu.ekip"), icon="👥")
sayfa_admin = st.Page("sayfa_admin.py", title=t("menu.admin"), icon="🔧")

# Onemli parametre varsa sadece login sayfasini goster
if _onemli_parametre_var:
    pg = st.navigation([sayfa_login], position="hidden")
else:
    pg = st.navigation([sayfa_login, sayfa_tek, sayfa_toplu, sayfa_gecmis, sayfa_dashboard, sayfa_onboarding, sayfa_zamanlanmis, sayfa_ekip, sayfa_hukuki, sayfa_hesabim, sayfa_yukselt, sayfa_admin])

# Sidebar basligi
st.sidebar.title("◆ " + t("app.baslik"))
st.sidebar.markdown("**" + t("app.kapsam") + "**")

st.sidebar.markdown("---")

# Kullanici bilgisi + Trial + Limit
import session_manager
if _auth.giris_yapildi_mi():
    _kullanici = _auth.mevcut_kullanici()
    st.sidebar.success(f"👤 {_kullanici.get('ad_soyad') or _kullanici.get('kullanici_adi')}")
    st.sidebar.caption(f"Rol: {_kullanici.get('rol', 'user').upper()}")

    # Session kalan sure
    session_manager.kalan_sure_goster()

    # Trial durumu
    try:
        _trial = _auth.db.trial_durum(_kullanici.get("kullanici_adi", ""))
        _durum = _trial.get("durum", "YOK")
        _plan_sb = _trial.get("plan", "free")

        if _durum == "AKTIF" and _plan_sb == "trial":
            _kalan_gun = _trial.get("kalan_gun", 0)
            if _kalan_gun > 0:
                st.sidebar.info(t("sidebar.trial_days").format(gun=_kalan_gun))
            else:
                _kalan_saat = _trial.get("kalan_saat", 0)
                st.sidebar.warning(t("sidebar.trial_hours").format(saat=_kalan_saat))
        elif _durum == "SURESI_DOLDU":
            st.sidebar.error(t("sidebar.trial_expired"))
    except Exception:
        pass

    # Kullanim limiti
    try:
        import db as _db_sb
        _lim_sonuc = _db_sb.limit_kontrol(_kullanici.get("kullanici_adi", ""))
        if _lim_sonuc.get("durum") == "OK":
            _kalan = _lim_sonuc.get("kalan", -1)
            _kull = _lim_sonuc.get("kullanilan", 0)
            _lim = _lim_sonuc.get("limit", 0)
            if _kalan == -1:
                st.sidebar.caption(t("sidebar.unlimited"))
            else:
                st.sidebar.caption(t("sidebar.usage").format(kull=_kull, lim=_lim))
        elif _lim_sonuc.get("durum") in ("LIMIT_DOLDU", "TRIAL_BITTI"):
            st.sidebar.error(t("sidebar.limit_exceeded"))
    except Exception:
        pass
else:
    st.sidebar.info(t("sidebar.not_logged"))

st.sidebar.markdown("---")
st.sidebar.caption(t("app.surum"))

# Arka plan scheduler'i baslat (sadece bir kez)
import scheduler_thread

@st.cache_resource
def _scheduler_baslat():
    """Scheduler'i bir kez baslatir."""
    scheduler_thread.baslat(interval_saniye=300)
    return True

_scheduler_baslat()

# Sidebar'da scheduler durumu
with st.sidebar:
    st.markdown("---")
    durum = scheduler_thread.durum()
    if durum["calisiyor"]:
        st.caption("🟢 Otomatik denetim aktif (5 dk)")
    else:
        st.caption("🔴 Otomatik denetim kapali")

# Sayfayi calistir
pg.run()
