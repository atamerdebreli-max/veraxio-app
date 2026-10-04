"""
Hukuki sayfalar - Gizlilik, KVKK, Kullanim Sartlari, DPA
Tum dillerde gosterilir.
"""
import streamlit as st
from i18n import t


def hukuki_sayfa():
    """Hukuki sayfa - tab'li."""
    st.title("⚖️ " + t("hukuki.baslik"))
    st.caption(t("hukuki.son_guncelleme") + ": 2026-10-02")
    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs([
        "🔒 " + t("hukuki.tab_gizlilik"),
        "🛡️ " + t("hukuki.tab_kvkk"),
        "📜 " + t("hukuki.tab_kullanim"),
        "📄 " + t("hukuki.tab_dpa"),
    ])

    # ============================================================
    # 1) GIZLILIK POLITIKASI
    # ============================================================
    with tab1:
        st.header(t("hukuki.gizlilik_baslik"))

        st.subheader(t("hukuki.gizlilik_1_baslik"))
        st.write(t("hukuki.gizlilik_1_metin"))

        st.subheader(t("hukuki.gizlilik_2_baslik"))
        st.write(t("hukuki.gizlilik_2_metin"))

        st.subheader(t("hukuki.gizlilik_3_baslik"))
        st.write(t("hukuki.gizlilik_3_metin"))

        st.subheader(t("hukuki.gizlilik_4_baslik"))
        st.write(t("hukuki.gizlilik_4_metin"))

        st.subheader(t("hukuki.gizlilik_5_baslik"))
        st.write(t("hukuki.gizlilik_5_metin"))

        st.markdown("---")
        st.caption(t("hukuki.iletisim_caption"))

    # ============================================================
    # 2) KVKK AYDINLATMA
    # ============================================================
    with tab2:
        st.header(t("hukuki.kvkk_baslik"))

        st.subheader(t("hukuki.kvkk_1_baslik"))
        st.write(t("hukuki.kvkk_1_metin"))

        st.subheader(t("hukuki.kvkk_2_baslik"))
        st.write(t("hukuki.kvkk_2_metin"))

        st.subheader(t("hukuki.kvkk_3_baslik"))
        st.write(t("hukuki.kvkk_3_metin"))

        st.subheader(t("hukuki.kvkk_4_baslik"))
        st.write(t("hukuki.kvkk_4_metin"))

        st.subheader(t("hukuki.kvkk_5_baslik"))
        st.write(t("hukuki.kvkk_5_metin"))

        st.subheader(t("hukuki.kvkk_6_baslik"))
        st.write(t("hukuki.kvkk_6_metin"))

        st.markdown("---")
        st.info(t("hukuki.kvkk_basvuru_bilgi"))

    # ============================================================
    # 3) KULLANIM SARTLARI
    # ============================================================
    with tab3:
        st.header(t("hukuki.kullanim_baslik"))

        st.subheader(t("hukuki.kullanim_1_baslik"))
        st.write(t("hukuki.kullanim_1_metin"))

        st.subheader(t("hukuki.kullanim_2_baslik"))
        st.write(t("hukuki.kullanim_2_metin"))

        st.subheader(t("hukuki.kullanim_3_baslik"))
        st.write(t("hukuki.kullanim_3_metin"))

        st.subheader(t("hukuki.kullanim_4_baslik"))
        st.write(t("hukuki.kullanim_4_metin"))

        st.markdown("---")
        st.caption(t("hukuki.kullanim_sorumluluk"))

    # ============================================================
    # 4) VERI ISLEME SOZLESMESI (DPA)
    # ============================================================
    with tab4:
        st.header(t("hukuki.dpa_baslik"))

        st.info(t("hukuki.dpa_ozet"))

        st.subheader(t("hukuki.dpa_1_baslik"))
        st.write(t("hukuki.dpa_1_metin"))

        st.subheader(t("hukuki.dpa_2_baslik"))
        st.write(t("hukuki.dpa_2_metin"))

        st.subheader(t("hukuki.dpa_3_baslik"))
        st.write(t("hukuki.dpa_3_metin"))

        st.subheader(t("hukuki.dpa_4_baslik"))
        st.write(t("hukuki.dpa_4_metin"))

        st.markdown("---")
        st.caption(t("hukuki.dpa_talep"))

    # ============================================================
    # Footer
    # ============================================================
    st.markdown("---")
    st.caption(t("hukuki.footer"))

    # Geri butonu
    if st.button("← " + t("hukuki.geri"), use_container_width=False):
        st.session_state["hukuki_acik"] = False
        st.rerun()


# ============================================================
# SAYFA MODU
# ============================================================
hukuki_sayfa()