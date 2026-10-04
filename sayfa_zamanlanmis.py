"""
Zamanlanmis Denetimler sayfasi
"""

# Giris kontrolu
import auth
auth.giris_gerekli()

import streamlit as st
import db
from i18n import t

st.title(t("zamanlanmis.baslik"))
st.markdown(t("zamanlanmis.aciklama"))
st.markdown("---")

db.init_db()

# ============================================================
# YENI DENETIM EKLE
# ============================================================
st.subheader(t("zamanlanmis.yeni_baslik"))

col1, col2 = st.columns(2)

with col1:
    zm_musteri = st.text_input(t("zamanlanmis.musteri") + " *", key="zm_musteri")
    zm_eposta = st.text_input(t("zamanlanmis.eposta"), placeholder="ornek@sirket.com", key="zm_eposta")
    zm_ai_tipi = st.selectbox(
        t("zamanlanmis.ai_tipi") + " *",
        [
            "Chatbot / AI Asistan",
            "Gorsel Uretimi (C2PA)",
            "Metin Denetimi (AI Tespiti)",
        ],
        key="zm_ai_tipi",
    )

with col2:
    zm_url = st.text_input(t("zamanlanmis.url"), placeholder="https://...", key="zm_url")
    zm_siklik = st.selectbox(
        t("zamanlanmis.siklik") + " *",
        ["gunluk", "haftalik", "aylik"],
        index=1,
        format_func=lambda x: t(f"zamanlanmis.{x}"),
        key="zm_siklik",
    )

if zm_ai_tipi == "Metin Denetimi (AI Tespiti)":
    zm_metin = st.text_area(t("zamanlanmis.metin"), height=100, key="zm_metin")
    zm_chatbot_mesaji = ""
elif zm_ai_tipi == "Chatbot / AI Asistan":
    st.caption(t("zamanlanmis.chatbot_caption"))
    zm_chatbot_mesaji = st.text_area(
        t("zamanlanmis.chatbot_mesaji_opt"),
        height=100,
        placeholder=t("zamanlanmis.chatbot_placeholder"),
        key="zm_chatbot_mesaji",
    )
    zm_metin = ""
else:
    zm_metin = ""
    zm_chatbot_mesaji = ""

st.markdown("---")

if st.button(t("zamanlanmis.ekle_btn"), type="primary", use_container_width=True):
    if not zm_musteri:
        st.error(t("zamanlanmis.hata_musteri"))
    elif zm_ai_tipi in ["Chatbot / AI Asistan", "Gorsel Uretimi (C2PA)"] and not zm_url:
        st.error(t("zamanlanmis.hata_url"))
    elif zm_ai_tipi == "Metin Denetimi (AI Tespiti)" and not zm_metin:
        st.error(t("zamanlanmis.hata_metin"))
    else:
        ek_bilgi = {}
        if zm_metin:
            ek_bilgi["metin"] = zm_metin
        if zm_chatbot_mesaji:
            ek_bilgi["chatbot_mesaji"] = zm_chatbot_mesaji

        # Mevcut dili al
        mevcut_dil = st.session_state.get("dil", "tr")

        db.zamanlanmis_ekle(
            musteri=zm_musteri,
            ai_tipi=zm_ai_tipi,
            url=zm_url,
            ek_bilgi=ek_bilgi,
            siklik=zm_siklik,
            eposta=zm_eposta,
            dil=mevcut_dil,
            firma_id=auth.firma_id(),
        )
        st.success(t("zamanlanmis.basari_ekle").format(zm_musteri))
        st.rerun()

# ============================================================
# MEVCUT ZAMANLANMIS DENETIMLER
# ============================================================
st.markdown("---")
st.subheader(t("zamanlanmis.mevcut_baslik"))

kayitlar = db.zamanlanmis_listele(aktif_only=True)

if not kayitlar:
    st.info(t("zamanlanmis.kayit_yok"))
else:
    for kayit in kayitlar:
        siklik_ceviri = t(f"zamanlanmis.{kayit['siklik']}")
        with st.expander(
            f"**{kayit['musteri']}** — {kayit['ai_tipi']} ({siklik_ceviri})",
            expanded=False,
        ):
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.write(f"**{t('zamanlanmis.id')}:** {kayit['id']}")
                st.write(f"**{t('zamanlanmis.ai_tipi')}:** {kayit['ai_tipi']}")
                st.write(f"**{t('zamanlanmis.siklik')}:** {siklik_ceviri}")
                st.write(f"**{t('zamanlanmis.url')}:** {kayit.get('url') or '-'}")
                st.write(f"**{t('zamanlanmis.eposta')}:** {kayit.get('eposta') or '-'}")
                st.write(f"**Dil:** {kayit.get('dil') or 'tr'}")
                son = kayit.get('son_calisma') or t("zamanlanmis.hic")
                st.write(f"**{t('zamanlanmis.son_calisma')}:** {son}")
                st.write(f"**{t('zamanlanmis.sonraki_calisma')}:** {kayit.get('sonraki_calisma') or '-'}")
                st.write(f"**{t('zamanlanmis.olusturma')}:** {kayit.get('olusturma', '-')}")
            with col_b:
                if st.button(t("zamanlanmis.sil_btn"), key=f"sil_{kayit['id']}", use_container_width=True):
                    db.zamanlanmis_sil(kayit["id"])
                    st.success(t("zamanlanmis.silindi").format(kayit['musteri']))
                    st.rerun()

# ============================================================
# MANUEL CALISTIR
# ============================================================
st.markdown("---")
st.subheader(t("zamanlanmis.manuel_baslik"))

st.caption(t("zamanlanmis.manuel_caption"))

if st.button(t("zamanlanmis.calistir_btn"), type="secondary", use_container_width=True):
    with st.spinner(t("zamanlanmis.calistiriliyor")):
        import subprocess
        import sys
        try:
            sonuc = subprocess.run(
                [sys.executable, "zamanlanmis_calistir.py", "--force"],
                capture_output=True,
                text=True,
                timeout=300,
            )
            st.text(sonuc.stdout)
            if sonuc.stderr:
                st.text(sonuc.stderr)
            st.success(t("zamanlanmis.calistirma_tamam"))
        except Exception as e:
            st.error(t("zamanlanmis.hata").format(e))