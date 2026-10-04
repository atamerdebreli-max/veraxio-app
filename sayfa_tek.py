"""
Tek Denetim sayfasi - sadece Streamlit UI
Is mantigi core.py'de
"""
import tempfile
import os

# Giris kontrolu
import auth
auth.giris_gerekli()

import streamlit as st
import db
from cache_utils import cache_temizle
from i18n import t

import json as _json
import csv as _csv
import io as _io
from siphrix.policy_runtime import PolicyManager
from siphrix.policy_runtime import PolicyManager
from core import ai_metadata_kontrol, deepfake_model_kontrol
from chatbot_scraper import chatbot_url_denetle
from image_downloader import gorsel_url_indir, gecici_dosya_sil
from core import (
    pdf_bytes_al,
    kumulatif_kontrol,
    shadow_ai_kontrol,
    ab_temsilcisi_kontrol,
    kvkk_kontrol,
    kvkk_dokuman_analiz,
    ai_metin_tespit_kontrol,
    synthid_kontrol,
    ai_image_detector_kontrol,
    ai_bildirimi_var_mi, c2pa_kontrol, c2pa_dayaniklilik_testi,
    deepfake_kontrol, kamu_metni_kontrol, duygu_tanima_kontrol,
    rapor_pdf_olustur, json_cikti_olustur, csv_cikti_olustur,
)




def cevir_secenek(x):
    """Radio/checkbox seceneklerini cevirir ama degeri degistirmez."""
    anahtarlar = {
        "Evet": "radio_secenek.evet",
        "Hayir": "radio_secenek.hayir",
        "Emin degilim": "radio_secenek.emin_degilim",
        "Gercek zamanli": "radio_secenek.gercek_zamanli",
        "Sonradan": "radio_secenek.sonradan",
        "Sesli degil": "radio_secenek.sesli_degil",
        "Var": "radio_secenek.var",
        "Yok": "radio_secenek.yok",
        "Sanatsal degil": "radio_secenek.sanatsal_degil",
    }
    return t(anahtarlar.get(x, x))


st.title("🔍 " + t("sayfa_tek.baslik"))
st.markdown("**" + t("sayfa_tek.alt_baslik") + "**")
st.markdown("---")

st.subheader(t("sayfa_tek.ai_tipi_baslik"))
AI_TIPI_ANAHTARLARI = {
    "Chatbot / AI Asistan": "ai_tipleri.chatbot",
    "Gorsel Uretimi (C2PA)": "ai_tipleri.gorsel",
    "Metin Denetimi (AI Tespiti)": "ai_tipleri.metin",
    "KVKK Uyum Denetimi": "ai_tipleri.kvkk",
    "AB Temsilcisi Kontrolu": "ai_tipleri.ab_temsilcisi",
    "Shadow AI Taramasi": "ai_tipleri.shadow_ai",
    "Kumulatif Yukumluluk Analizi": "ai_tipleri.kumulatif",
    "Duygu Tanima (Musteri Tarafi)": "ai_tipleri.duygu_musteri",
    "Duygu Tanima (Calisan Tarafi)": "ai_tipleri.duygu_calisan",
    "Biyometrik Siniflandirma": "ai_tipleri.biyometrik",
    "Deepfake Icerik": "ai_tipleri.deepfake",
    "Kamu Yarari Metni": "ai_tipleri.kamu_metni",
}

ai_tipi = st.selectbox(
    t("sayfa_tek.ai_tipi_sec"),
    [
        "Chatbot / AI Asistan",
        "Gorsel Uretimi (C2PA)",
        "Metin Denetimi (AI Tespiti)",
        "KVKK Uyum Denetimi",
        "AB Temsilcisi Kontrolu",
        "Shadow AI Taramasi",
        "Kumulatif Yukumluluk Analizi",
        "Duygu Tanima (Musteri Tarafi)",
        "Duygu Tanima (Calisan Tarafi)",
        "Biyometrik Siniflandirma",
        "Deepfake Icerik",
        "Kamu Yarari Metni"
    ],
    format_func=lambda x: t(AI_TIPI_ANAHTARLARI.get(x, x)),
)
st.markdown("---")

st.subheader(t("sayfa_tek.musteri_baslik"))
col1, col2 = st.columns(2)
with col1:
    musteri_adi = st.text_input(t("sayfa_tek.musteri_adi") + " *", placeholder="ABC Teknoloji A.S.")
    chatbot_url = st.text_input(t("sayfa_tek.chatbot_url"), placeholder="https://...")
with col2:
    sektor = st.text_input(t("sayfa_tek.sektor"), placeholder="Fintech, SaaS")
    iletisim_kisi = st.text_input(t("sayfa_tek.iletisim"), placeholder="Ad Soyad")

denetci_adi = st.text_input(t("sayfa_tek.denetci_adi") + " *", value="Tamer")

st.markdown("---")
st.subheader(t("sayfa_tek.ai_detay_baslik"))

chatbot_mesaji = ""
c2pa_gorsel = None
ai_metadata_sonuc = None
deepfake_model_sonuc = None

if ai_tipi == "Chatbot / AI Asistan":
    st.caption(t("chatbot_ui.caption"))
    col_url, col_btn = st.columns([3, 1])
    with col_url:
        chatbot_url_input = st.text_input(t("chatbot_ui.url_label"), placeholder=t("chatbot_ui.url_placeholder"), key="chatbot_url_input")
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        url_cek_btn = st.button(t("chatbot_ui.url_btn"), use_container_width=True, key="url_cek_btn")

    if url_cek_btn and chatbot_url_input:
        with st.spinner(t("chatbot_ui.spinner")):
            url_sonuc = chatbot_url_denetle(chatbot_url_input)
            if url_sonuc["durum"] == "OK":
                if url_sonuc["chatbot_mesaji"] and not url_sonuc["chatbot_mesaji"].startswith("("):
                    st.session_state["chatbot_mesaji_auto"] = url_sonuc["chatbot_mesaji"]
                    st.success(t("chatbot_ui.success"))
                    if url_sonuc.get("widget_tipleri"):
                        st.caption(t("chatbot_ui.widget") + ", ".join(url_sonuc["widget_tipleri"]))
                else:
                    st.warning(t("chatbot_ui.warning"))
            elif url_sonuc["durum"] == "CHATBOT_YOK":
                st.info(t("chatbot_ui.info"))
            else:
                st.error("❌ " + url_sonuc.get("hata", "Bilinmeyen hata"))

    varsayilan_mesaj = st.session_state.get("chatbot_mesaji_auto", "")
    chatbot_mesaji = st.text_area(
        t("chatbot_ui.mesaj_label"),
        value=varsayilan_mesaj,
        height=100,
        placeholder=t("chatbot_ui.mesaj_placeholder"),
    )
    cb_apacik = st.radio(
        t("radio.apacik_ortada"),
        ["Hayir", "Evet"],
        help="Kilavuz: Istisna dar yorumlanir; cocuklar/savunmasiz gruplar icin bildirim sart.",
        format_func=cevir_secenek,
    )
    cb_ilk_etkilesim = st.radio(
        t("radio.ilk_etkilesim"),
        ["Evet", "Hayir"],
        help="Madde 50(5): Bildirim ilk etkilesimde yapilmalidir.",
        format_func=cevir_secenek,
    )
    cb_erisilebilirlik = st.radio(
        t("radio.erisilebilirlik"),
        ["Evet", "Hayir", "Emin degilim"],
        help="Madde 50(5): Bildirim erisilebilirlik gerekliliklerine uygun olmali.",
        format_func=cevir_secenek,
    )
    cb_acik = st.radio(
        t("radio.acik_ayirt"),
        ["Evet", "Hayir"],
        help="Madde 50(5): Bildirim acik ve ayirt edilebilir olmali.",
        format_func=cevir_secenek,
    )
elif ai_tipi == "Kumulatif Yukumluluk Analizi":
    st.caption("Sirketinizde hangi AI sistemleri var? Tumunu isaretleyin.")
    kum_chatbot = st.checkbox("Chatbot / AI Asistan")
    kum_gorsel = st.checkbox("Gorsel Uretimi")
    kum_duygu = st.checkbox("Duygu Tanima / Biyometrik")
    kum_deepfake = st.checkbox("Deepfake Icerik")
    kum_kamu = st.checkbox("Kamu Yarari Metni")
    kum_kvkk = st.checkbox("KVKK kapsaminda AI")
    kum_ab = st.checkbox("AB'de musteri/ofis")
    kum_shadow = st.checkbox("Shadow AI (calisan ici)")
elif ai_tipi == "Shadow AI Taramasi":
    st.caption("Sirket icinde habersizce kullanilan AI araclarini degerlendirin.")
    sh_ai_kullanim = st.checkbox("Calisanlar AI araclarini kullaniyor mu?")
    sh_politika = st.checkbox("AI kullanim politikaniz var mi?")
    sh_onayli_liste = st.checkbox("Onayli AI araclari listeniz var mi?")
    sh_veri_sinif = st.checkbox("Veri siniflandirmasi yapiliyor mu?")
    sh_veri_izleme = st.checkbox("AI araclarina veri gonderimi izleniyor mu?")
    sh_egitim = st.checkbox("Calisanlara AI farkindalik egitimi veriliyor mu?")
    sh_onay_sureci = st.checkbox("AI araclari icin onay sureciniz var mi?")
    sh_dlp = st.checkbox("DLP (veri kaybi onleme) sisteminiz var mi?")
elif ai_tipi == "AB Temsilcisi Kontrolu":
    st.caption("AB AI Act Madde 22 - Yetkili temsilci kontrolu")
    ab_musteri = st.checkbox("AB'de musteriniz var mi?")
    ab_ofis = st.checkbox("AB'de ofisiniz var mi?")
    ab_temsilci_var = st.checkbox("AB merkezli yetkili temsilciniz var mi?")
    ab_temsilci_ab = st.checkbox("Temsilci AB'de yerlesik mi?")
    ab_temsilci_yetki = st.checkbox("Temsilci yazili yetkiye sahip mi?")
    ab_temsilci_ilan = st.checkbox("Temsilci bilgileri ilan edilmis mi?")
elif ai_tipi == "KVKK Uyum Denetimi":
    st.caption("KVKK uyumluluk detaylarini doldurun.")
    kvkk_otomatik_karar = st.checkbox("Otomatik karar sistemi var mi? (profil olusturma, skorlama vb.)")
    kvkk_insan_mudahale = st.checkbox("Insan mudahalesi / incelemesi var mi?")
    kvkk_acik_riza = st.checkbox("Kisisel veri isleme icin ACIK RIZA aliniyor mu?")
    kvkk_itiraz = st.checkbox("Kullanicilara ITIRAZ HAKKI taniniyor mu?")
    kvkk_aydinlatma = st.checkbox("Aydinlatma metni / gizlilik politikasi VAR mi?")
    kvkk_veri_sorumlusu = st.checkbox("Veri sorumlusu belirli ve ilan edilmis mi?")
    kvkk_amac = st.checkbox("Veri isleme amaci net mi?")
    kvkk_yurtdisi = st.checkbox("Yurt disina veri aktarimi var mi?")
    st.markdown("---")
    st.caption("Opsiyonel: Gizlilik politikanizi yukleyin (PDF/TXT) - otomatik analiz edilir.")
    kvkk_dosya = st.file_uploader("Gizlilik Politikasi (opsiyonel)", type=["pdf", "txt"])
elif ai_tipi == "Metin Denetimi (AI Tespiti)":
    st.caption("AI tarafindan uretilmis olabilecek bir metni yapistirin.")
    denetlenecek_metin = st.text_area("Metin *", height=200, placeholder="Metni buraya yapistirin...")
elif ai_tipi == "Gorsel Uretimi (C2PA)":
    st.caption(t("gorsel_ui.caption"))
    col_url, col_btn = st.columns([3, 1])
    with col_url:
        gorsel_url_input = st.text_input(t("gorsel_ui.url_label"), placeholder=t("gorsel_ui.url_placeholder"), key="gorsel_url_input")
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        gorsel_url_btn = st.button(t("gorsel_ui.url_btn"), use_container_width=True, key="gorsel_url_btn")

    if gorsel_url_btn and gorsel_url_input:
        with st.spinner(t("gorsel_ui.spinner")):
            indir_sonuc = gorsel_url_indir(gorsel_url_input)
            if indir_sonuc["durum"] == "OK":
                st.session_state["gorsel_url_dosya"] = indir_sonuc["dosya_yolu"]
                st.session_state["gorsel_url_boyut"] = indir_sonuc["boyut"]
                st.success(t("gorsel_ui.success").format(f"{indir_sonuc['boyut']:,}"))
            else:
                st.error("❌ " + indir_sonuc.get("hata", "Bilinmeyen hata"))

    st.markdown("---")
    st.caption(t("gorsel_ui.or_upload"))
    c2pa_gorsel = st.file_uploader(t("gorsel_ui.gorsel_sec"), type=["png", "jpg", "jpeg", "webp"])
    c2pa_200token = st.radio(
        t("radio.200_token"),
        ["Hayir", "Evet", "Emin degilim"],
        help="200 token alti serbest metin icin watermark gerekmez.",
        format_func=cevir_secenek,
    )
    c2pa_birlikte = st.radio(
        t("radio.birlikte_calisabilirlik"),
        ["Evet", "Hayir", "Emin degilim"],
        help="Yeni Kod: tespit mekanizmalari birlikte calisabilir olmali.",
        format_func=cevir_secenek,
    )
    c2pa_katmanli = st.radio(
        t("radio.cok_katmanli"),
        ["Evet", "Hayir", "Emin degilim"],
        help="Yeni Kod: en az iki katman onerilir.",
        format_func=cevir_secenek,
    )
    c2pa_imza = st.radio(
        t("radio.dijital_imza"),
        ["Evet", "Hayir", "Emin degilim"],
        help="Yeni Kod: dijital imza ve zaman damgasi onerilir.",
        format_func=cevir_secenek,
    )
    c2pa_kamuya_acik = st.radio(
        t("radio.kamuya_acik"),
        ["Evet", "Hayir", "Emin degilim"],
        help="Yeni Kod: tespit cozumu kamuya acik olmali.",
        format_func=cevir_secenek,
    )
    c2pa_standart = st.radio(
        t("radio.standart_duzenleme"),
        ["Hayir", "Evet", "Emin degilim"],
        help="Kilavuz: sadece format/duzenleme amacli degisiklikler kapsam disidir.",
        format_func=cevir_secenek,
    )
elif ai_tipi in ["Duygu Tanima (Musteri Tarafi)", "Duygu Tanima (Calisan Tarafi)"]:
    st.caption("Duygu tanima sistemi detaylari.")
    bildirim_dt = st.checkbox(t("checkbox.bildirim_dt"))
    hedef_kitle = st.selectbox("Hedef kitle:", ["Genel", "Savunmasiz Grup"])
    biyometrik_dt = st.checkbox(t("checkbox.biyometrik_dt"))
    dt_kanun = st.radio(
        t("radio.kanun_yetki"),
        ["Hayir", "Evet"],
        help="Madde 50(3) istisnasi: sadece kanunla yetkilendirilmis kullanimlar.",
        format_func=cevir_secenek,
    )
    dt_zaman = st.radio(
        t("radio.zaman"),
        ["Gercek zamanli", "Sonradan", "Emin degilim"],
        help="Madde 50(3): her iki durumda da bildirim gerekir.",
        format_func=cevir_secenek,
    )
elif ai_tipi == "Biyometrik Siniflandirma":
    st.caption("Biyometrik siniflandirma detaylari.")
    bildirim_dt = st.checkbox("Kullanicilara bildirim YAPILIYOR mu?")
    hedef_kitle = st.selectbox("Hedef kitle:", ["Genel", "Savunmasiz Grup"])
    biyometrik_dt = True
    dt_kanun = st.radio(
        t("radio.kanun_yetki"),
        ["Hayir", "Evet"],
        help="Madde 50(3) istisnasi: sadece kanunla yetkilendirilmis kullanimlar.",
        format_func=cevir_secenek,
    )
    dt_zaman = st.radio(
        t("radio.zaman"),
        ["Gercek zamanli", "Sonradan", "Emin degilim"],
        help="Madde 50(3): her iki durumda da bildirim gerekir.",
        format_func=cevir_secenek,
    )
elif ai_tipi == "Deepfake Icerik":
    st.caption("Deepfake icerik detaylari.")
    df_ai_uretim = st.checkbox(t("checkbox.ai_uretim"))
    df_gercekci = st.checkbox(t("checkbox.gercekci"))
    df_mevcudiyet = st.radio(
        t("radio.mevcudiyet"),
        ["Evet", "Hayir"],
        help="Deepfake tanimi: mevcut kisi/nesne/yer/olaya benzeyen ve yanlislikla gercek gorunen icerik.",
        format_func=cevir_secenek,
    )
    df_etiket = st.checkbox(t("checkbox.etiket_var"))
    df_ilk_maruziyet = st.radio(
        t("radio.ilk_maruziyet"),
        ["Evet", "Hayir", "Etiket yok"],
        help="Madde 50(5): Bildirim ilk maruziyette yapilmalidir.",
        format_func=cevir_secenek,
    )
    df_sanatsal = st.checkbox(t("checkbox.sanatsal"))
    df_sesli = st.radio(
        t("radio.sesli_bildirim"),
        ["Sesli degil", "Var", "Yok"],
        help="Sesli deepfake'ler icin isitsel bildirim gerekir.",
        format_func=cevir_secenek,
    )
    df_sanatsal_etiket = st.radio(
        t("radio.sanatsal_etiket"),
        ["Sanatsal degil", "Evet", "Hayir"],
        help="Madde 50(4)(a): sanatsal eserlerde hafifletilmis etiket yeterli.",
        format_func=cevir_secenek,
    )
elif ai_tipi == "Kamu Yarari Metni":
    st.caption("Kamu yarari metni detaylari.")
    km_ai_uretim = st.checkbox(t("checkbox.metin_ai"))
    km_kamu_yarari = st.checkbox(t("checkbox.kamu_yarari"))
    km_insan_denetimi = st.checkbox(t("checkbox.insan_denetimi"))
    km_yetkili = st.radio(
        t("radio.yetkili_inceleme"),
        ["Evet", "Hayir"],
        help="Kilavuz: Sadece goz gezdirmek yeterli degil; nitelikli inceleme sart.",
        format_func=cevir_secenek,
    )
    km_editoryal = st.checkbox(t("checkbox.editoryal_sorumlu"))
    km_editoryal_kim = st.radio(
        t("radio.editoryal_kim"),
        ["Evet", "Hayir"],
        help="Kilavuz: editoryal sorumluluk gercek bir kisi veya kurumda olmali.",
        format_func=cevir_secenek,
    )
    km_kapsam = st.radio(
        t("radio.kamu_kapsam"),
        ["Evet", "Hayir", "Emin degilim"],
        help="Kilavuz: kamu yarari kapsami net olmalidir.",
        format_func=cevir_secenek,
    )
    km_etiket = st.checkbox(t("checkbox.etiket_var"))

st.markdown("---")

# ============================================================
# LIMIT GOSTERGESI
# ============================================================
try:
    import auth as _auth_lim
    _mevcut_k = _auth_lim.mevcut_kullanici()
    _limit = db.limit_kontrol(_mevcut_k.get("kullanici_adi", ""))

    if _limit.get("durum") == "OK":
        _kalan = _limit.get("kalan", -1)
        _kullanim = _limit.get("kullanilan", 0)
        _lim = _limit.get("limit", 0)
        _plan_adi = _limit.get("plan_adi", "-")

        if _kalan == -1:
            st.info(f"💎 **{_plan_adi}** plani - Sinirsiz denetim")
        else:
            if _kalan <= 1:
                st.warning(f"📊 **{_plan_adi}** plani - Bu ay: {_kullanim}/{_lim} ({_kalan} kaldi!)")
            else:
                st.info(f"📊 **{_plan_adi}** plani - Bu ay: {_kullanim}/{_lim} ({_kalan} kaldi)")
    elif _limit.get("durum") in ("LIMIT_DOLDU", "TRIAL_BITTI"):
        st.error(f"🚫 {_limit.get('mesaj', 'Limit doldu')}")
        st.info("💎 Plan yukseltmek icin: **info@veraxio.ai**")
except Exception as _e:
    print(f"[Limit gosterge hatasi] {_e}")

# ============================================================
# DENETLE
# ============================================================
if st.button(t("sayfa_tek.denetle_btn"), type="primary", use_container_width=True):
    # ONCE LIMIT KONTROLU
    try:
        import auth as _auth_lim
        _mevcut_k = _auth_lim.mevcut_kullanici()
        _limit = db.limit_kontrol(_mevcut_k.get("kullanici_adi", ""))

        if _limit.get("durum") in ("LIMIT_DOLDU", "TRIAL_BITTI"):
            st.error(f"🚫 {_limit.get('mesaj', 'Limit doldu')}")
            st.info("💎 Plan yukseltmek icin: **info@veraxio.ai**")
            st.stop()
    except Exception as _e:
        print(f"[Limit kontrol hatasi] {_e}")

    if not musteri_adi:
        st.error("Lutfen Musteri Adi alanini doldurun.")
    else:
        with st.spinner(t("sayfa_tek.spinner")):
            bildirim_var = False
            karar_50_1 = {"bildirim_var": False, "verdict": "N/A", "reason": "N/A", "decision_id": "N/A", "matched_rule_id": "N/A"}
            c2pa_sonuc = None
            dayaniklilik_sonuc = None
            duygu_sonuc = None
            deepfake_sonuc = None
            kamu_metni_sonuc = None
            metin_sonuc = None
            kvkk_sonuc = None
            ab_sonuc = None
            shadow_sonuc = None
            kumulatif_sonuc = None
            kvkk_dokuman_sonuc = None
            synthid_sonuc = None
            ai_metadata_sonuc = None
            deepfake_model_sonuc = None
            ai_image_detector_sonuc = None

            if ai_tipi == "Chatbot / AI Asistan":
                if not chatbot_mesaji:
                    st.error("Lutfen Chatbot Ilk Mesajini girin.")
                    st.stop()
                bildirim_var = ai_bildirimi_var_mi(chatbot_mesaji)
                # Apacik ortada istisnasi
                if not bildirim_var and cb_apacik == "Evet":
                    bildirim_var = True
                    istisna_uygulandi = True
                else:
                    istisna_uygulandi = False
                # Ilk etkilesim kontrolu
                if bildirim_var and cb_ilk_etkilesim == "Hayir":
                    bildirim_var = False
                    ilk_etkilesim_ihlali = True
                else:
                    ilk_etkilesim_ihlali = False
                # Erisilebilirlik + aciklik
                if bildirim_var and cb_erisilebilirlik == "Hayir":
                    bildirim_var = False
                    erisilebilirlik_ihlali = True
                else:
                    erisilebilirlik_ihlali = False
                if bildirim_var and cb_acik == "Hayir":
                    bildirim_var = False
                    aciklik_ihlali = True
                else:
                    aciklik_ihlali = False
                pm = PolicyManager()
                action = "chatbot_interaction_with_disclosure" if bildirim_var else "chatbot_interaction"
                karar = pm.decide({"action_name": action})
                karar_50_1 = {
                    "bildirim_var": bildirim_var,
                    "verdict": karar.verdict,
                    "reason": karar.reason,
                    "decision_id": karar.decision_id,
                    "matched_rule_id": karar.matched_rule_id,
                }
            elif ai_tipi == "Kumulatif Yukumluluk Analizi":
                kumulatif_sonuc = kumulatif_kontrol(
                    kum_chatbot, kum_gorsel, kum_duygu, kum_deepfake,
                    kum_kamu, kum_kvkk, kum_ab, kum_shadow
                )
            elif ai_tipi == "Shadow AI Taramasi":
                shadow_sonuc = shadow_ai_kontrol(
                    sh_ai_kullanim, sh_politika, sh_onayli_liste, sh_veri_sinif,
                    sh_veri_izleme, sh_egitim, sh_onay_sureci, sh_dlp
                )
            elif ai_tipi == "AB Temsilcisi Kontrolu":
                ab_sonuc = ab_temsilcisi_kontrol(
                    ab_musteri, ab_ofis, ab_temsilci_var,
                    ab_temsilci_ab, ab_temsilci_yetki, ab_temsilci_ilan
                )
            elif ai_tipi == "KVKK Uyum Denetimi":
                kvkk_sonuc = kvkk_kontrol(
                    kvkk_otomatik_karar, kvkk_insan_mudahale, kvkk_acik_riza,
                    kvkk_itiraz, kvkk_aydinlatma, kvkk_veri_sorumlusu,
                    kvkk_amac, kvkk_yurtdisi
                )
                kvkk_dokuman_sonuc = None
                if kvkk_dosya:
                    with tempfile.NamedTemporaryFile(delete=False, suffix="." + kvkk_dosya.name.split(".")[-1]) as tmp:
                        tmp.write(kvkk_dosya.read())
                        tmp_path = tmp.name
                    kvkk_dokuman_sonuc = kvkk_dokuman_analiz(tmp_path)
                    os.unlink(tmp_path)
            elif ai_tipi == "Metin Denetimi (AI Tespiti)":
                if not denetlenecek_metin:
                    st.error("Lutfen bir metin girin.")
                    st.stop()
                metin_sonuc = ai_metin_tespit_kontrol(denetlenecek_metin)
                synthid_sonuc = synthid_kontrol(denetlenecek_metin)
            elif ai_tipi == "Gorsel Uretimi (C2PA)":
                if c2pa_standart == "Evet":
                    c2pa_sonuc = {"durum": "KAPSAM_DISI", "uretim_araci": None}
                    dayaniklilik_sonuc = None
                elif st.session_state.get("gorsel_url_dosya") or c2pa_gorsel:
                    # Dosya yolunu belirle
                    if st.session_state.get("gorsel_url_dosya"):
                        tmp_path = st.session_state["gorsel_url_dosya"]
                        gecici_dosya = False
                    else:
                        with tempfile.NamedTemporaryFile(delete=False, suffix="." + c2pa_gorsel.name.split(".")[-1]) as tmp:
                            tmp.write(c2pa_gorsel.read())
                            tmp_path = tmp.name
                        gecici_dosya = True

                    # ORTAK ANALIZ (her iki durumda da calisir)
                    c2pa_sonuc = c2pa_kontrol(tmp_path)
                    dayaniklilik_sonuc = c2pa_dayaniklilik_testi(tmp_path)
                    ai_metadata_sonuc = ai_metadata_kontrol(tmp_path)
                    deepfake_model_sonuc = deepfake_model_kontrol(tmp_path)
                    ai_image_detector_sonuc = ai_image_detector_kontrol(tmp_path)

                    # Sadece yuklenen dosya icin gecici dosyayi sil
                    if gecici_dosya:
                        os.unlink(tmp_path)
            elif ai_tipi in ["Duygu Tanima (Musteri Tarafi)", "Duygu Tanima (Calisan Tarafi)", "Biyometrik Siniflandirma"]:
                duygu_sonuc = duygu_tanima_kontrol(bildirim_dt, hedef_kitle, biyometrik_dt)
                if ai_tipi == "Duygu Tanima (Calisan Tarafi)":
                    duygu_sonuc["durum"] = "YASAK"
                    duygu_sonuc["yasak"] = True
                    duygu_sonuc["bulgular"] = ["Isyerinde calisan duygularinin analizi YASAK (Madde 5(1)(f))"]
                    duygu_sonuc["oneri"] = ["Bu sistemi derhal durdurun. 2 Subat 2025'ten beri yasak."]
                # Kanunla yetkilendirme istisnasi
                if dt_kanun == "Evet":
                    duygu_sonuc["durum"] = "UYUMLU"
                    duygu_sonuc["bulgular"].append("Kanunla yetkilendirilmis kullanim - istisna uygulanir")
                    duygu_sonuc["oneri"] = []
            elif ai_tipi == "Deepfake Icerik":
                deepfake_sonuc = deepfake_kontrol(df_ai_uretim, df_gercekci, df_etiket, df_sanatsal)
                # Mevcudiyet kontrolu
                if deepfake_sonuc["durum"] != "UYUMSUZ":
                    if df_mevcudiyet == "Hayir":
                        deepfake_sonuc["bulgular"].append("Mevcut kisi/nesne/olaya benzemiyor - kapsam disi")
                    elif df_ilk_maruziyet == "Hayir" or df_ilk_maruziyet == "Etiket yok":
                        deepfake_sonuc["durum"] = "UYUMSUZ"
                        deepfake_sonuc["bulgular"].append("Etiket ilk maruziyette gorunmuyor (Madde 50(5))")
                        deepfake_sonuc["oneri"].append("Etiketi ilk maruziyette gorunur hale getirin.")
                # Sesli icerik kontrolu
                if df_sesli == "Yok":
                    deepfake_sonuc["durum"] = "UYUMSUZ"
                    deepfake_sonuc["bulgular"].append("Sesli icerikte isitsel bildirim YOK")
                    deepfake_sonuc["oneri"].append("Sesli icerik icin isitsel bildirim ekleyin.")
                # Sanatsal hafifletilmis etiket kontrolu
                if df_sanatsal and df_sanatsal_etiket == "Hayir":
                    deepfake_sonuc["bulgular"].append("Sanatsal eserde etiket eserin keyfini kaciriyor")
                    deepfake_sonuc["oneri"].append("Etiketi eserin keyfini kacirmayacak sekilde uyarlayin.")
            elif ai_tipi == "Kamu Yarari Metni":
                kamu_metni_sonuc = kamu_metni_kontrol(km_ai_uretim, km_kamu_yarari, km_insan_denetimi, km_editoryal, km_etiket)
                # Yetkili inceleme kontrolu
                if km_insan_denetimi and km_yetkili == "Hayir":
                    kamu_metni_sonuc["durum"] = "UYUMSUZ"
                    kamu_metni_sonuc["bulgular"].append("Inceleyen kisi onay/degistirme/red yetkisine sahip degil")
                    kamu_metni_sonuc["oneri"].append("Nitelikli insan incelemesi saglayin (Kilavuz sarti).")
                # Editoryal sorumluluk kimde kontrolu
                if km_editoryal and km_editoryal_kim == "Hayir":
                    kamu_metni_sonuc["durum"] = "UYUMSUZ"
                    kamu_metni_sonuc["bulgular"].append("Editoryal sorumluluk gercek kisi/kurumda degil")
                    kamu_metni_sonuc["oneri"].append("Editoryal sorumlulugu gercek bir kisi veya kuruma verin.")
                # Kamu yarari kapsami kontrolu
                if km_kapsam != "Evet" and km_ai_uretim and km_kamu_yarari:
                    kamu_metni_sonuc["bulgular"].append("Kamu yarari kapsami net degil - ek inceleme gerekli")

            pdf, rapor_no = rapor_pdf_olustur(
                musteri_adi, sektor, chatbot_url, iletisim_kisi,
                denetci_adi, ai_tipi, karar_50_1, c2pa_sonuc, dayaniklilik_sonuc, duygu_sonuc,
                deepfake_sonuc, kamu_metni_sonuc,
                ai_metadata_sonuc if 'ai_metadata_sonuc' in dir() else None,
                deepfake_model_sonuc if 'deepfake_model_sonuc' in dir() else None,
                ai_image_detector_sonuc if 'ai_image_detector_sonuc' in dir() else None,
                metin_sonuc if 'metin_sonuc' in dir() else None,
                synthid_sonuc if 'synthid_sonuc' in dir() else None,
                kvkk_sonuc if 'kvkk_sonuc' in dir() else None,
                ab_sonuc if 'ab_sonuc' in dir() else None,
                shadow_sonuc if 'shadow_sonuc' in dir() else None,
                kumulatif_sonuc if 'kumulatif_sonuc' in dir() else None,
            )

            st.markdown("---")
            st.subheader(t("sayfa_tek.sonuclar_baslik"))

            if ai_tipi == "Chatbot / AI Asistan":
                if bildirim_var:
                    st.success("✅ Madde 50(1): UYUMLU - AI bildirimi var")
                else:
                    st.error("❌ Madde 50(1): UYUMSUZ - AI bildirimi yok")
                st.caption("Kanit ID: " + str(karar_50_1["decision_id"]))
                st.caption("Karar: " + str(karar_50_1["verdict"]))
            elif ai_tipi == "Kumulatif Yukumluluk Analizi":
                if kumulatif_sonuc["durum"] == "KAPSAM_DISI":
                    st.info("ℹ️ Hicbir AI sistemi secilmedi.")
                else:
                    col1, col2 = st.columns(2)
                    col1.metric("Yukumluluk Sayisi", kumulatif_sonuc["madde_sayisi"])
                    col2.metric("Risk Skoru", f"%{kumulatif_sonuc['risk_skoru']}")
                    for y in kumulatif_sonuc["yukumlulukler"]:
                        st.caption("• " + y)
            elif ai_tipi == "Shadow AI Taramasi":
                if shadow_sonuc["durum"] == "KAPSAM_DISI":
                    st.info("ℹ️ KAPSAM DISI: AI kullanimi yok")
                elif shadow_sonuc["durum"] == "UYUMSUZ":
                    risk = shadow_sonuc.get("risk_seviyesi", "?")
                    if risk == "KRITIK":
                        st.error("🚨 Shadow AI: KRITIK RISK")
                    elif risk == "YUKSEK":
                        st.error("❌ Shadow AI: YUKSEK RISK")
                    else:
                        st.warning("⚠️ Shadow AI: " + risk + " RISK")
                else:
                    st.success("✅ Shadow AI: UYUMLU")
                for b in shadow_sonuc["bulgular"]:
                    st.caption("• " + b)
            elif ai_tipi == "AB Temsilcisi Kontrolu":
                if ab_sonuc["durum"] == "KAPSAM_DISI":
                    st.info("ℹ️ KAPSAM DISI: AB'de musteri veya ofis yok")
                elif ab_sonuc["durum"] == "UYUMSUZ":
                    st.error("❌ AB Temsilcisi: UYUMSUZ")
                else:
                    st.success("✅ AB Temsilcisi: UYUMLU")
                for b in ab_sonuc["bulgular"]:
                    st.caption("• " + b)
            elif ai_tipi == "KVKK Uyum Denetimi":
                if kvkk_sonuc["durum"] == "UYUMSUZ":
                    st.error("❌ KVKK: UYUMSUZ")
                else:
                    st.success("✅ KVKK: UYUMLU")
                for b in kvkk_sonuc["bulgular"]:
                    st.caption("• " + b)
                if kvkk_dokuman_sonuc:
                    st.markdown("---")
                    st.subheader("📄 Dokuman Analizi")
                    if kvkk_dokuman_sonuc.get("durum") == "HATA":
                        st.error("Hata: " + str(kvkk_dokuman_sonuc.get("hata", "")))
                    else:
                        st.caption(f"Bulunan: {', '.join(kvkk_dokuman_sonuc.get('bulunan', []))}")
                        st.caption(f"Eksik: {', '.join(kvkk_dokuman_sonuc.get('eksik', []))}")
            elif ai_tipi == "Metin Denetimi (AI Tespiti)":
                if metin_sonuc:
                    if metin_sonuc.get("uyari"):
                        st.info("ℹ️ " + metin_sonuc["uyari"])
                    if metin_sonuc["durum"] == "AI":
                        st.warning("AI Metin Tespiti: AI (olasilik: %" + str(round(metin_sonuc["ai_olasilik"]*100, 1)) + ")")
                    elif metin_sonuc["durum"] == "INSAN":
                        st.success("AI Metin Tespiti: INSAN (olasilik: %" + str(round(metin_sonuc["insan_olasilik"]*100, 1)) + ")")
                    else:
                        st.error("AI Metin Tespiti: HATA")
                if synthid_sonuc:
                    st.info("SynthID: " + synthid_sonuc.get("durum", "?"))
                    if synthid_sonuc.get("detay"):
                        st.caption(synthid_sonuc["detay"])
            elif ai_tipi == "Gorsel Uretimi (C2PA)":
                if c2pa_sonuc:
                    if c2pa_sonuc["durum"] == "KAPSAM_DISI":
                        st.info("ℹ️ KAPSAM DISI: Sadece yardimci duzenleme - muaf")
                    elif c2pa_sonuc["durum"] == "ISARETLI":
                        st.success("✅ Madde 50(2): C2PA metadata VAR")
                        st.caption("Uretici: " + str(c2pa_sonuc["uretim_araci"]))
                        if ai_metadata_sonuc and ai_metadata_sonuc.get("ai_declared"):
                            st.info("🔍 AI Metadata: " + str(ai_metadata_sonuc.get("source")))
                        if deepfake_model_sonuc and deepfake_model_sonuc.get("durum") in ["DEEPFAKE", "GERCEK"]:
                            if deepfake_model_sonuc["durum"] == "DEEPFAKE":
                                st.warning("⚠️ Deepfake Model (yuz): DEEPFAKE (olasilik: %" + str(round(deepfake_model_sonuc["fake_olasilik"]*100, 1)) + ")")
                            else:
                                st.caption("🤖 Deepfake Model (yuz): GERCEK (olasilik: %" + str(round(deepfake_model_sonuc["gercek_olasilik"]*100, 1)) + ")")
                        # LAYER 4: Genel AI Image Detector
                        if ai_image_detector_sonuc and ai_image_detector_sonuc.get("durum") in ["YAPAY", "GERCEK", "BELIRSIZ"]:
                            if ai_image_detector_sonuc["durum"] == "YAPAY":
                                st.warning("🎨 Genel AI Detector: YAPAY (p_fake: %" + str(round(ai_image_detector_sonuc["p_fake"]*100, 1)) + ")")
                            elif ai_image_detector_sonuc["durum"] == "BELIRSIZ":
                                st.info("🎨 Genel AI Detector: BELIRSIZ (p_real: " + str(ai_image_detector_sonuc["p_real"]) + ")")
                            else:
                                st.caption("🎨 Genel AI Detector: GERCEK (p_real: %" + str(round(ai_image_detector_sonuc["p_real"]*100, 1)) + ")")
                            # CELISKI KONTROLU (akilli)
                            ai_metadata_var = ai_metadata_sonuc and ai_metadata_sonuc.get("ai_declared")
                            yuz_yapay = deepfake_model_sonuc and deepfake_model_sonuc.get("durum") == "DEEPFAKE"
                            genel_yapay = ai_image_detector_sonuc and ai_image_detector_sonuc.get("durum") == "YAPAY"
                            if ai_metadata_var and not (yuz_yapay or genel_yapay):
                                st.error("⚠️ CELISKI: Metadata AI diyor ama iki model de GERCEK diyor!")
                                st.caption("Not: Modeller yuz ve genel AI tespiti icin egitildi. Farkli AI tiplerinde yanlis negatif olabilir.")
                        if dayaniklilik_sonuc:
                            if dayaniklilik_sonuc["durum"] == "DAYANIKLI":
                                st.success("✅ Dayaniklilik: DAYANIKLI")
                            elif dayaniklilik_sonuc["durum"] == "DAYANIKSIZ":
                                st.error("❌ Dayaniklilik: DAYANIKSIZ")
                    else:
                        st.error("❌ Madde 50(2): C2PA metadata YOK")
                else:
                    st.info("ℹ️ Gorsel yuklenmedi.")
            elif duygu_sonuc:
                if duygu_sonuc["durum"] == "YASAK":
                    st.error("🚫 YASAK: " + duygu_sonuc["bulgular"][0])
                elif duygu_sonuc["durum"] == "UYUMSUZ":
                    st.error("❌ Madde 50(3): UYUMSUZ")
                else:
                    st.success("✅ Madde 50(3): UYUMLU")
                for b in duygu_sonuc["bulgular"]:
                    st.caption("• " + b)
                if duygu_sonuc["oneri"]:
                    st.info("Öneri: " + duygu_sonuc["oneri"][0])

            if deepfake_sonuc:
                st.markdown("---")
                st.subheader(t("sayfa_tek.deepfake_baslik"))
                if deepfake_sonuc["durum"] == "UYUMSUZ":
                    st.error("❌ UYUMSUZ")
                else:
                    st.success("✅ UYUMLU")
                for b in deepfake_sonuc["bulgular"]:
                    st.caption("• " + b)
                if deepfake_sonuc["oneri"]:
                    st.info("Öneri: " + deepfake_sonuc["oneri"][0])

            if kamu_metni_sonuc:
                st.markdown("---")
                st.subheader(t("sayfa_tek.kamu_baslik"))
                if kamu_metni_sonuc["durum"] == "UYUMSUZ":
                    st.error("❌ UYUMSUZ")
                else:
                    st.success("✅ UYUMLU")
                for b in kamu_metni_sonuc["bulgular"]:
                    st.caption("• " + b)
                if kamu_metni_sonuc["oneri"]:
                    st.info("Öneri: " + kamu_metni_sonuc["oneri"][0])

            st.markdown("---")
            genel = "UYUMLU"
            if ai_tipi == "Chatbot / AI Asistan" and not bildirim_var:
                genel = "UYUMSUZ"
            elif ai_tipi == "Gorsel Uretimi (C2PA)":
                if c2pa_sonuc and c2pa_sonuc["durum"] not in ["ISARETLI", "KAPSAM_DISI"]:
                    genel = "UYUMSUZ"
                if dayaniklilik_sonuc and dayaniklilik_sonuc["durum"] == "DAYANIKSIZ":
                    genel = "UYUMSUZ"
            elif duygu_sonuc and duygu_sonuc["durum"] in ["YASAK", "UYUMSUZ"]:
                genel = "UYUMSUZ"
            if deepfake_sonuc and deepfake_sonuc["durum"] == "UYUMSUZ":
                genel = "UYUMSUZ"
            if kamu_metni_sonuc and kamu_metni_sonuc["durum"] == "UYUMSUZ":
                genel = "UYUMSUZ"
            if metin_sonuc and metin_sonuc.get("durum") == "AI":
                genel = "UYUMSUZ"
            if kvkk_sonuc and kvkk_sonuc.get("durum") == "UYUMSUZ":
                genel = "UYUMSUZ"
            if ab_sonuc and ab_sonuc.get("durum") == "UYUMSUZ":
                genel = "UYUMSUZ"
            if shadow_sonuc and shadow_sonuc.get("durum") == "UYUMSUZ":
                genel = "UYUMSUZ"
            if kumulatif_sonuc and kumulatif_sonuc.get("durum") in ["KISMI", "KAPSAMLI"]:
                genel = "UYUMSUZ"

            if genel == "UYUMSUZ":
                st.error("# 🚨 GENEL SONUC: " + genel)
                st.error("CEZA RISKI: 15 milyon Euro veya cironun %3'u")
            else:
                st.success("# ✅ GENEL SONUC: " + genel)

            st.markdown("---")
            st.subheader(t("sayfa_tek.rapor_indir_baslik"))

            # JSON ve CSV icerik olustur
            json_veri = json_cikti_olustur(
                rapor_no, musteri_adi, sektor, chatbot_url, iletisim_kisi,
                denetci_adi, ai_tipi, genel, karar_50_1, c2pa_sonuc,
                dayaniklilik_sonuc, duygu_sonuc, deepfake_sonuc, kamu_metni_sonuc
            )
            json_bytes = _json.dumps(json_veri, ensure_ascii=False, indent=2).encode("utf-8")
            csv_bytes = csv_cikti_olustur(
                rapor_no, musteri_adi, sektor, ai_tipi, denetci_adi, genel,
                karar_50_1, c2pa_sonuc, duygu_sonuc, deepfake_sonuc, kamu_metni_sonuc
            )

            # 3 sutun: PDF | JSON | CSV
            col_pdf, col_json, col_csv = st.columns(3)

            with col_pdf:
                pdf_bytes, zaman_bilgi = pdf_bytes_al(pdf, zaman_damgasi_dondur=True)
                st.download_button(
                    label=t("sayfa_tek.pdf_btn"),
                    data=pdf_bytes,
                    file_name="rapor_" + musteri_adi.replace(" ", "_") + "_" + rapor_no + ".pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )

            with col_json:
                st.download_button(
                    label=t("sayfa_tek.json_btn"),
                    data=json_bytes,
                    file_name="rapor_" + musteri_adi.replace(" ", "_") + "_" + rapor_no + ".json",
                    mime="application/json",
                    use_container_width=True,
                )

            with col_csv:
                st.download_button(
                    label=t("sayfa_tek.csv_btn"),
                    data=csv_bytes,
                    file_name="rapor_" + musteri_adi.replace(" ", "_") + "_" + rapor_no + ".csv",
                    mime="text/csv",
                    use_container_width=True,
                )

            # ZAMAN DAMGASI BOLUMU
            if zaman_bilgi and zaman_bilgi.get("hash"):
                st.markdown("---")
                st.subheader("🕐 " + t("sayfa_tek.zaman_damgasi_baslik"))
                st.caption(t("sayfa_tek.zaman_damgasi_aciklama"))
                st.markdown("**" + t("sayfa_tek.hash_label") + "**")
                st.code(zaman_bilgi["hash"], language="text")
                col_ots, col_tsa = st.columns(2)
                with col_ots:
                    if zaman_bilgi.get("ots_bytes"):
                        st.success("✅ " + t("sayfa_tek.blockchain_label"))
                        st.caption(t("sayfa_tek.blockchain_caption"))
                        st.download_button(label="📥 " + t("sayfa_tek.ots_btn"), data=zaman_bilgi["ots_bytes"], file_name="rapor_" + rapor_no + ".pdf.ots", mime="application/octet-stream", use_container_width=True, key="ots_dl")
                with col_tsa:
                    if zaman_bilgi.get("tsr_bytes"):
                        st.success("✅ " + t("sayfa_tek.tsa_label"))
                        st.caption(t("sayfa_tek.tsa_caption"))
                        st.download_button(label="📥 " + t("sayfa_tek.tsr_btn"), data=zaman_bilgi["tsr_bytes"], file_name="rapor_" + rapor_no + ".pdf.tsr", mime="application/octet-stream", use_container_width=True, key="tsr_dl")

            # Otomatik veritabani kaydi
            db.kaydet(
                rapor_no=rapor_no,
                modul="Tek Denetim",
                musteri=musteri_adi,
                sektor=sektor,
                ai_tipi=ai_tipi,
                denetci=denetci_adi,
                genel_sonuc=genel,
                karar=karar_50_1.get("verdict", "N/A"),
                kanit_id=karar_50_1.get("decision_id", "N/A"),
                ceza_riski="15 milyon Euro veya cironun %3u" if genel == "UYUMSUZ" else "",
                json_veri=json_veri,
                firma_id=auth.firma_id(),
            )

            # Cache temizle - yeni kayit aninda gorunsun
            try:
                from cache_utils import cache_temizle
                cache_temizle()
            except Exception:
                pass


            # Audit log
            try:
                db.audit_kaydet(
                    eylem="denetim_yapildi",
                    kullanici_adi=auth.mevcut_kullanici().get("kullanici_adi") if auth.mevcut_kullanici() else None,
                    firma_id=auth.firma_id(),
                    detay=f"AI Tipi: {ai_tipi} | Sonuc: {genel} | Rapor: {rapor_no}",
                )
            except Exception:
                pass

            st.caption("Rapor No: " + rapor_no)