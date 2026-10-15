"""
sayfa_entegrasyon.py - Slack/Jira Entegrasyonu
"""
import streamlit as st
import auth
auth.giris_gerekli()

import db
import requests
from i18n import t
from datetime import datetime


st.title("🔌 " + t("entegrasyon.baslik"))
st.markdown("**" + t("entegrasyon.alt_baslik") + "**")
st.markdown("---")

kullanici = auth.mevcut_kullanici()
firma_id = kullanici.get("firma_id") if kullanici else None

# ============================================================
# SLACK ENTEGRASYONU
# ============================================================
st.subheader(t("entegrasyon.slack_baslik"))

st.info(t("entegrasyon.nasil_kurulur"))

mevcut_slack = None
try:
    mevcut_slack = db.entegrasyon_bul(firma_id, "slack")
except Exception:
    pass

if mevcut_slack:
    st.success(t("entegrasyon.aktif"))
    st.caption(t("entegrasyon.webhook") + mevcut_slack["webhook_url"][:60] + "...")
    if mevcut_slack.get("son_test"):
        st.caption(t("entegrasyon.son_test") + mevcut_slack["son_test"])
else:
    st.warning(t("entegrasyon.kurulmamis"))

with st.expander(t("entegrasyon.ayarlar"), expanded=(not mevcut_slack)):
    with st.form("slack_form"):
        webhook_url = st.text_input(
            t("entegrasyon.webhook_label"),
            value=mevcut_slack["webhook_url"] if mevcut_slack else "",
            placeholder="https://hooks.slack.com/services/...",
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.form_submit_button(t("entegrasyon.kaydet"), type="primary", use_container_width=True):
                if not webhook_url or not webhook_url.startswith("https://hooks.slack.com/"):
                    st.error(t("entegrasyon.gecersiz_url"))
                else:
                    try:
                        db.entegrasyon_kaydet(firma_id, "slack", webhook_url)
                        st.success(t("entegrasyon.kaydedildi"))
                        st.rerun()
                    except Exception as e:
                        st.error(t("entegrasyon.kayit_hatasi") + str(e))
        with col2:
            if st.form_submit_button(t("entegrasyon.test_et"), use_container_width=True):
                if not webhook_url:
                    st.error(t("entegrasyon.gecersiz_url"))
                else:
                    try:
                        yanit = requests.post(webhook_url, json={
                            "text": "🧪 *Veraxio Test*\n\n✅ Test mesajı başarılı!",
                            "username": "Veraxio",
                            "icon_emoji": ":shield:",
                        }, timeout=10)
                        if yanit.status_code == 200:
                            st.success(t("entegrasyon.test_basarili"))
                            db.entegrasyon_test_guncelle(firma_id, "slack")
                        else:
                            st.error(t("entegrasyon.test_hatasi") + str(yanit.status_code))
                    except Exception as e:
                        st.error(t("entegrasyon.baglanti_hatasi") + str(e))
        with col3:
            if st.form_submit_button(t("entegrasyon.sil"), use_container_width=True):
                db.entegrasyon_sil(firma_id, "slack")
                st.success(t("entegrasyon.silindi"))
                st.rerun()

# ============================================================
# JIRA (YAKINDA)
# ============================================================
st.markdown("---")
st.subheader(t("entegrasyon.jira_baslik"))
st.info(t("entegrasyon.jira_yakinda"))

# ============================================================
# MANUEL BILDIRIM GONDER
# ============================================================
st.markdown("---")
st.subheader(t("entegrasyon.manuel_baslik"))

if mevcut_slack:
    with st.form("manuel_bildirim"):
        baslik = st.text_input(t("entegrasyon.baslik_label"), value="AI Act Uyumluluk Raporu")
        mesaj = st.text_area(t("entegrasyon.mesaj"), placeholder=t("entegrasyon.mesaj_placeholder"), height=100)
        renk = st.selectbox(t("entegrasyon.renk"), [
            t("entegrasyon.renk_iyi"),
            t("entegrasyon.renk_uyari"),
            t("entegrasyon.renk_tehlike"),
        ])

        if st.form_submit_button(t("entegrasyon.gonder"), type="primary", use_container_width=True):
            if not mesaj:
                st.error(t("entegrasyon.mesaj_bos"))
            else:
                renk_kodlari = {
                    t("entegrasyon.renk_iyi"): "good",
                    t("entegrasyon.renk_uyari"): "warning",
                    t("entegrasyon.renk_tehlike"): "danger",
                }
                try:
                    yanit = requests.post(mevcut_slack["webhook_url"], json={
                        "attachments": [{
                            "color": renk_kodlari[renk],
                            "title": baslik,
                            "text": mesaj,
                            "footer": "Veraxio · " + datetime.now().strftime("%d.%m.%Y %H:%M"),
                        }]
                    }, timeout=10)
                    if yanit.status_code == 200:
                        st.success(t("entegrasyon.gonderildi"))
                    else:
                        st.error(t("entegrasyon.test_hatasi") + str(yanit.status_code))
                except Exception as e:
                    st.error(t("entegrasyon.baglanti_hatasi") + str(e))
else:
    st.caption(t("entegrasyon.once_slack"))

# ============================================================
# OTOMATIK BILDIRIM AYARI
# ============================================================
if mevcut_slack:
    st.markdown("---")
    st.subheader(t("entegrasyon.otomatik_baslik"))
    st.caption(t("entegrasyon.otomatik_aciklama"))

    col1, col2 = st.columns(2)
    with col1:
        st.checkbox(t("entegrasyon.oto_denetim"), value=True, disabled=True)
        st.checkbox(t("entegrasyon.oto_uyumsuz"), value=True, disabled=True)
    with col2:
        st.checkbox(t("entegrasyon.oto_red_team"), value=True, disabled=True)
        st.checkbox(t("entegrasyon.oto_bias"), value=True, disabled=True)
