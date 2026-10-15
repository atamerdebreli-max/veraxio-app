"""
sayfa_entegrasyon.py - Slack/Jira Entegrasyonu
Denetim sonuclarini Slack kanalina gonderir.
"""
import streamlit as st
import auth
auth.giris_gerekli()

import db
import requests
from datetime import datetime


st.title("🔌 Entegrasyonlar")
st.markdown("**Denetim sonuçlarını Slack kanalınıza otomatik gönderin.**")
st.markdown("---")

kullanici = auth.mevcut_kullanici()
firma_id = kullanici.get("firma_id") if kullanici else None

# ============================================================
# SLACK ENTEGRASYONU
# ============================================================
st.subheader("💬 Slack Entegrasyonu")

st.info("""
**Nasıl kurulur?**
1. Slack'te **Incoming Webhooks** uygulamasını açın
2. Bir kanal seçin (ör. #ai-act-uyumluluk)
3. Webhook URL'ini kopyalayın (`https://hooks.slack.com/services/...`)
4. Aşağıya yapıştırın ve kaydedin
""")

# Mevcut entegrasyon
mevcut_slack = None
try:
    mevcut_slack = db.entegrasyon_bul(firma_id, "slack")
except Exception:
    pass

if mevcut_slack:
    st.success("✅ Slack entegrasyonu **aktif**")
    st.caption("Webhook: " + mevcut_slack["webhook_url"][:60] + "...")
    if mevcut_slack.get("son_test"):
        st.caption("Son test: " + mevcut_slack["son_test"])
else:
    st.warning("⚠️ Slack entegrasyonu **kurulmamış**")

# Kaydetme formu
with st.expander("⚙️ Slack Webhook Ayarları", expanded=(not mevcut_slack)):
    with st.form("slack_form"):
        webhook_url = st.text_input(
            "Slack Webhook URL",
            value=mevcut_slack["webhook_url"] if mevcut_slack else "",
            placeholder="https://hooks.slack.com/services/...",
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.form_submit_button("💾 Kaydet", type="primary", use_container_width=True):
                if not webhook_url or not webhook_url.startswith("https://hooks.slack.com/"):
                    st.error("Geçerli bir Slack webhook URL'i girin.")
                else:
                    try:
                        db.entegrasyon_kaydet(firma_id, "slack", webhook_url)
                        st.success("✅ Slack entegrasyonu kaydedildi.")
                        st.rerun()
                    except Exception as e:
                        st.error("Kayıt hatası: " + str(e))
        with col2:
            if st.form_submit_button("🧪 Test Et", use_container_width=True):
                if not webhook_url:
                    st.error("Önce webhook URL'ini girin.")
                else:
                    try:
                        yanit = requests.post(webhook_url, json={
                            "text": "🧪 *Veraxio Test Mesajı*\n\nBu bir test bildirimidir. Entegrasyon çalışıyor! ✅",
                            "username": "Veraxio",
                            "icon_emoji": ":shield:",
                        }, timeout=10)
                        if yanit.status_code == 200:
                            st.success("✅ Test mesajı gönderildi! Slack kanalınızı kontrol edin.")
                            db.entegrasyon_test_guncelle(firma_id, "slack")
                        else:
                            st.error(f"❌ Slack hatası: {yanit.status_code} — {yanit.text}")
                    except Exception as e:
                        st.error("Bağlantı hatası: " + str(e))
        with col3:
            if st.form_submit_button("🗑️ Sil", use_container_width=True):
                db.entegrasyon_sil(firma_id, "slack")
                st.success("Slack entegrasyonu silindi.")
                st.rerun()

# ============================================================
# JIRA (YAKINDA)
# ============================================================
st.markdown("---")
st.subheader("📋 Jira Entegrasyonu")
st.info("🚧 **Yakında:** Jira entegrasyonu geliştirme aşamasında. Bulunan her eksik için otomatik ticket oluşturulacak.")

# ============================================================
# MANUEL BILDIRIM GONDER
# ============================================================
st.markdown("---")
st.subheader("📤 Manuel Bildirim Gönder")

if mevcut_slack:
    with st.form("manuel_bildirim"):
        baslik = st.text_input("Başlık", value="AI Act Uyumluluk Raporu")
        mesaj = st.text_area("Mesaj", placeholder="Kanalınıza gönderilecek mesaj...", height=100)
        renk = st.selectbox("Renk", ["iyi (yeşil)", "uyarı (sarı)", "tehlike (kırmızı)"])

        if st.form_submit_button("📤 Gönder", type="primary", use_container_width=True):
            if not mesaj:
                st.error("Mesaj boş olamaz.")
            else:
                renk_kodlari = {"iyi (yeşil)": "good", "uyarı (sarı)": "warning", "tehlike (kırmızı)": "danger"}
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
                        st.success("✅ Bildirim gönderildi!")
                    else:
                        st.error(f"❌ Slack hatası: {yanit.status_code}")
                except Exception as e:
                    st.error("Bağlantı hatası: " + str(e))
else:
    st.caption("Önce Slack entegrasyonunu kurun.")

# ============================================================
# OTOMATIK BILDIRIM AYARI
# ============================================================
if mevcut_slack:
    st.markdown("---")
    st.subheader("🔔 Otomatik Bildirimler")
    st.caption("Bu olaylarda otomatik Slack bildirimi gönderilir:")

    col1, col2 = st.columns(2)
    with col1:
        st.checkbox("✅ Denetim tamamlandığında", value=True, disabled=True)
        st.checkbox("⚠️ Uyumsuz sonuç bulunduğunda", value=True, disabled=True)
    with col2:
        st.checkbox("🎯 Red team testi tamamlandığında", value=True, disabled=True)
        st.checkbox("⚖️ Bias tespit edildiğinde", value=True, disabled=True)

    st.caption("⚠️ Bu özellik yapılandırma aşamasında. Şimdilik manuel bildirim kullanabilirsiniz.")
