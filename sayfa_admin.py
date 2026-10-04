"""
sayfa_admin.py - Sistem admini paneli
Tum firmalar, kullanicilar, istatistikler
"""
import streamlit as st
import db
from cache_utils import (
    istatistik_cached, firma_listele_cached,
    kullanicilari_listele_cached,
)
import auth
from i18n import t


# Giris + admin kontrolu
auth.giris_gerekli()

if not auth.admin_mi():
    st.warning("⚠️ Bu sayfa sadece sistem yoneticisi icindir.")
    st.stop()


st.title("🔧 " + t("admin.baslik"))
st.markdown("---")


# ============================================================
# GENEL ISTATISTIK
# ============================================================
istat = istatistik_cached()
firmalar = firma_listele_cached()
tum_kullanicilar = kullanicilari_listele_cached()

col1, col2, col3, col4 = st.columns(4)
col1.metric(t("admin.toplam_firma"), len(firmalar))
col2.metric(t("admin.toplam_kullanici"), len(tum_kullanicilar))
col3.metric(t("admin.toplam_denetim"), istat["toplam"])
col4.metric(t("admin.uyumsuz"), istat["uyumsuz"])

st.markdown("---")


# ============================================================
# FIRMALAR
# ============================================================
st.subheader("🏢 " + t("admin.firmalar"))

if not firmalar:
    st.info("Henuz firma yok.")
else:
    for firma in firmalar:
        firma_id = firma["id"]
        firma_kullanicilari = db.firma_kullanicilari(firma_id)
        firma_istat = istatistik_cached(firma_id=firma_id)

        with st.expander(
            f"**{firma['firma_adi']}** — {len(firma_kullanicilari)} kullanici — {firma_istat['toplam']} denetim",
            expanded=False,
        ):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**ID:** {firma['id']}")
                st.write(f"**Firma:** {firma['firma_adi']}")
                st.write(f"**Sektor:** {firma.get('sektor', '-')}")
                st.write(f"**Vergi No:** {firma.get('vergi_no', '-')}")
                st.write(f"**E-posta:** {firma.get('eposta', '-')}")
                st.write(f"**Olusturma:** {firma.get('olusturma', '-')}")
            with col2:
                st.write(f"**Kullanici:** {len(firma_kullanicilari)}")
                st.write(f"**Denetim:** {firma_istat['toplam']}")
                st.write(f"**Uyumlu:** {firma_istat['uyumlu']}")
                st.write(f"**Uyumsuz:** {firma_istat['uyumsuz']}")

            st.markdown("**Kullanicilar:**")
            for k in firma_kullanicilari:
                rol = k.get("firma_rol", "user").upper()
                st.caption(f"  • @{k['kullanici_adi']} - {k.get('ad_soyad', '-')} - {rol}")


st.markdown("---")


# ============================================================
# TUM KULLANICILAR
# ============================================================
st.subheader("👥 " + t("admin.tum_kullanicilar"))

if not tum_kullanicilar:
    st.info("Henuz kullanici yok.")
else:
    for k in tum_kullanicilar:
        col1, col2, col3, col4 = st.columns([2, 3, 2, 2])
        with col1:
            st.write(f"**@{k['kullanici_adi']}**")
        with col2:
            st.write(k.get("ad_soyad", "-"))
            st.caption(k.get("eposta", "-"))
        with col3:
            rol = k.get("rol", "user").upper()
            if rol == "ADMIN":
                st.success(f"🔑 {rol}")
            else:
                st.info(f"👤 {rol}")
        with col4:
            firma = db.firma_bul(k.get("firma_id")) if k.get("firma_id") else None
            st.write(firma["firma_adi"] if firma else "Sistem")


st.markdown("---")


# ============================================================
# AUDIT LOG (DENETIM KAYITLARI)
# ============================================================
st.subheader("📋 " + t("admin.audit_log"))
st.caption(t("admin.audit_aciklama"))

# Filtreler
col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    audit_kullanici = st.text_input(t("admin.audit_kullanici"), key="audit_kullanici")
with col_f2:
    audit_eylem = st.selectbox(
        t("admin.audit_eylem"),
        ["", "giris_basarili", "giris_basarisiz", "cikis", "denetim_yapildi", "sifre_sifirlandi"],
        key="audit_eylem",
    )
with col_f3:
    audit_limit = st.number_input(t("admin.audit_limit"), min_value=10, max_value=500, value=50, key="audit_limit")

# Kayitlari al
audit_kayitlar = db.audit_listele(
    limit=int(audit_limit),
    kullanici_adi=audit_kullanici if audit_kullanici else None,
    eylem=audit_eylem if audit_eylem else None,
)

if not audit_kayitlar:
    st.info(t("admin.audit_yok"))
else:
    # Tablo olarak goster
    for k in audit_kayitlar:
        col1, col2, col3, col4 = st.columns([2, 2, 2, 4])

        # Basarili/basarisiz ikonu
        if k.get("basarili"):
            ikon = "✅"
        else:
            ikon = "❌"

        with col1:
            st.caption(k["tarih"])
        with col2:
            st.write(f"{ikon} **{k.get('kullanici_adi') or '-'}**")
        with col3:
            st.write(f"`{k['eylem']}`")
        with col4:
            st.caption((k.get("detay") or "-")[:80])

st.markdown("---")


# ============================================================
# API ANAHTARLARI
# ============================================================
st.subheader("🔑 " + t("admin.api_anahtarlari"))

anahtarlar = db.api_anahtarlari_listele(aktif_only=False)

if not anahtarlar:
    st.info("Henuz API anahtari yok.")
else:
    for a in anahtarlar:
        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
        with col1:
            st.code(a["anahtar"][:25] + "...", language="text")
        with col2:
            st.write(f"**{a['musteri']}**")
        with col3:
            st.caption(f"Kullanim: {a.get('toplam_istek', 0)}")
            st.caption(f"Son: {a.get('son_kullanim', '-')}")
        with col4:
            if st.button("🗑️", key=f"anahtar_sil_{a['id']}", help="Sil"):
                db.api_anahtari_sil(a["anahtar"])
                st.success("Silindi.")
                st.rerun()

st.markdown("---")


# ============================================================
# YENI API ANAHTARI
# ============================================================
st.subheader("➕ " + t("admin.yeni_api_anahtari"))

with st.form("api_anahtar_formu"):
    musteri_adi = st.text_input(t("admin.musteri_adi"), placeholder="ABC Teknoloji A.S.")
    submit = st.form_submit_button(t("admin.anahtar_olustur"), use_container_width=True, type="primary")

    if submit:
        if not musteri_adi:
            st.error("Musteri adi zorunlu.")
        else:
            yeni_anahtar = db.api_anahtari_olustur(musteri_adi)
            st.success("✅ " + t("admin.anahtar_olusturuldu"))
            st.code(yeni_anahtar, language="text")
            st.caption(t("admin.anahtar_uyari"))


# ============================================================
# YEDEK YONETIMI
# ============================================================
st.markdown("---")
st.subheader("💾 " + t("admin.yedek_baslik"))

# db_yedek modulu import (varsa)
try:
    import db_yedek
    _DB_YEDEK_VAR = True
except Exception as _e:
    _DB_YEDEK_VAR = False
    st.error("⚠️ db_yedek modulu yuklenemedi: " + str(_e))

if _DB_YEDEK_VAR:
    # --- Manuel yedek al ---
    col_b1, col_b2 = st.columns([1, 3])

    with col_b1:
        if st.button("🔄 " + t("admin.manuel_yedek_al"), type="primary", use_container_width=True):
            with st.spinner(t("admin.yedek_alinıyor")):
                try:
                    yeni_yedek = db_yedek.yedek_al(etiket="manuel")
                    if yeni_yedek:
                        st.success(f"✅ {t('admin.yedek_alindi')}: {yeni_yedek.name}")
                        try:
                            db.audit_kaydet(
                                eylem="db_yedek_alindi",
                                kullanici_adi=auth.mevcut_kullanici().get("kullanici_adi", "-"),
                                detay=f"Manuel yedek: {yeni_yedek.name}",
                            )
                        except Exception:
                            pass
                        st.rerun()
                    else:
                        st.error("❌ Yedek alinamadi.")
                except Exception as e:
                    st.error(f"❌ Hata: {e}")

    with col_b2:
        st.caption(t("admin.yedek_aciklama"))

    # --- Mevcut yedekler ---
    st.markdown("##### " + t("admin.mevcut_yedekler"))

    yedekler = db_yedek.yedek_listele()

    if not yedekler:
        st.info("Henuz yedek yok.")
    else:
        # Toplam boyut
        toplam_kb = sum(y["boyut_kb"] for y in yedekler)
        st.caption(f"Toplam {len(yedekler)} yedek, {toplam_kb:.1f} KB")

        # Son 10 yedek
        for y in yedekler[:10]:
            col_y1, col_y2, col_y3, col_y4 = st.columns([4, 2, 2, 1])

            with col_y1:
                st.code(y["isim"], language="text")
            with col_y2:
                st.caption(f"{y['boyut_kb']} KB")
            with col_y3:
                st.caption(y["tarih"])
            with col_y4:
                # Indirme butonu
                try:
                    with open(y["yol"], "rb") as f:
                        yedek_bytes = f.read()
                    st.download_button(
                        label="📥",
                        data=yedek_bytes,
                        file_name=y["isim"],
                        mime="application/x-sqlite3",
                        key=f"yedek_indir_{y['isim']}",
                        help="Indir",
                    )
                except Exception:
                    st.caption("—")

        if len(yedekler) > 10:
            st.caption(f"... ve {len(yedekler) - 10} yedek daha")


# ============================================================
# DEMO TALEPLERI
# ============================================================
st.markdown("---")
st.subheader("📩 " + t("admin.demo_talepleri"))

demo_talepleri = db.listele(limit=200)

# Demo taleplerini filtrele
demo_liste = [d for d in demo_talepleri if d.get("modul") == "Demo Talebi"]

if not demo_liste:
    st.info("Henuz demo talebi yok.")
else:
    # CSV indirme
    import csv as _csv
    import io as _io
    from datetime import datetime as _dt

    csv_buf = _io.StringIO()
    csv_w = _csv.writer(csv_buf)
    csv_w.writerow(["Tarih", "Ad Soyad", "E-posta", "Sirket", "Telefon", "Mesaj"])
    for d in demo_liste:
        import json as _json
        try:
            veri = _json.loads(d.get("json_veri") or "{}")
        except Exception:
            veri = {}
        csv_w.writerow([
            d.get("tarih", ""),
            veri.get("ad", d.get("musteri", "")),
            veri.get("email", ""),
            veri.get("sirket", d.get("sektor", "")),
            veri.get("telefon", ""),
            veri.get("mesaj", ""),
        ])

    csv_bytes = csv_buf.getvalue().encode("utf-8-sig")

    c_toplam, c_csv = st.columns([3, 1])
    with c_toplam:
        st.caption(f"Toplam {len(demo_liste)} demo talebi")
    with c_csv:
        st.download_button(
            label="📥 CSV Indir",
            data=csv_bytes,
            file_name="demo_talepleri_" + _dt.now().strftime("%Y%m%d") + ".csv",
            mime="text/csv",
            use_container_width=True,
            key="demo_csv_indir",
        )

    st.markdown("")

    # Tablo
    for d in demo_liste[:50]:
        import json as _json
        try:
            veri = _json.loads(d.get("json_veri") or "{}")
        except Exception:
            veri = {}

        ad = veri.get("ad", d.get("musteri", "-"))
        email = veri.get("email", "-")
        sirket = veri.get("sirket", d.get("sektor", "-"))
        telefon = veri.get("telefon", "-")
        mesaj = veri.get("mesaj", "-")

        with st.expander(f"**{ad}** - {email} - {d.get('tarih', '')[:16]}", expanded=False):
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"**Ad Soyad:** {ad}")
                st.write(f"**E-posta:** {email}")
                st.write(f"**Sirket:** {sirket}")
            with c2:
                st.write(f"**Telefon:** {telefon}")
                st.write(f"**Tarih:** {d.get('tarih', '-')}")
                st.write(f"**Kayit:** {d.get('rapor_no', '-')}")

            if mesaj:
                st.markdown("**Mesaj:**")
                st.write(mesaj)

            # Sil butonu
            if st.button("🗑️ Sil", key=f"demo_sil_{d.get('rapor_no')}", type="secondary"):
                db.sil(d.get("rapor_no"))
                st.success("Silindi.")
                st.rerun()
# ============================================================
# PLAN YONETIMI
# ============================================================
st.markdown("---")
st.subheader("💎 " + t("admin.plan_limitleri"))

dagilim = db.plan_dagilimi()
limitler = db.plan_limitleri()

c1, c2, c3, c4 = st.columns(4)
c1.metric(t("plan.free"), dagilim.get("free", 0))
c2.metric(t("plan.trial"), dagilim.get("trial", 0))
c3.metric(t("plan.pro"), dagilim.get("pro", 0))
c4.metric(t("plan.enterprise"), dagilim.get("enterprise", 0))

st.markdown("")

with st.expander(t("admin.plan_limitleri_expander")):
    for plan, limit in limitler.items():
        plan_adi = t(f"plan.{plan}")
        if limit == 0:
            limit_str = t("plan.unlimited_short")
        else:
            limit_str = f"{limit}{t('plan.month_suffix')}"
        st.write(f"**{plan_adi}** ({plan}): {limit_str}")

st.markdown("")

tum_users = db.kullanicilari_listele()

if tum_users:
    st.markdown("**" + t("admin.kullanici_planlari") + "**")

    planlar_listesi = ["free", "trial", "pro", "enterprise"]

    for u in tum_users:
        k_adi = u.get("kullanici_adi")
        mevcut_plan = u.get("plan") or "free"
        mevcut_plan_adi = t(f"plan.{mevcut_plan}")

        with st.expander(f"**{k_adi}** - {mevcut_plan_adi}", expanded=False):
            col_a, col_b = st.columns([2, 1])

            with col_a:
                st.write(f"**{t('admin.ad_soyad')}:** {u.get('ad_soyad') or '-'}")
                st.write(f"**{t('admin.eposta')}:** {u.get('eposta') or '-'}")
                st.write(f"**{t('admin.rol')}:** {u.get('rol', '-')}")
                st.write(f"**{t('admin.mevcut_plan')}:** {mevcut_plan_adi}")

                if mevcut_plan == "trial":
                    trial = db.trial_durum(k_adi)
                    if trial.get("durum") == "AKTIF":
                        st.success(t("admin.trial_days_short").format(gun=trial.get("kalan_gun", 0)))
                    elif trial.get("durum") == "SURESI_DOLDU":
                        st.error(t("admin.trial_expired"))

            with col_b:
                yeni_plan = st.selectbox(
                    t("admin.plan_degistir"),
                    planlar_listesi,
                    index=planlar_listesi.index(mevcut_plan) if mevcut_plan in planlar_listesi else 0,
                    format_func=lambda p: t(f"plan.{p}"),
                    key=f"plan_sec_{k_adi}",
                )

                if st.button("💾 " + t("admin.kaydet"), key=f"plan_kaydet_{k_adi}", type="primary", use_container_width=True):
                    if yeni_plan == mevcut_plan:
                        st.info(t("admin.plan_ayni"))
                    else:
                        sonuc = db.plan_guncelle(k_adi, yeni_plan)
                        if sonuc.get("durum") == "OK":
                            st.success(f"✅ {t('admin.plan_guncellendi')}: {k_adi} -> {t(f'plan.{yeni_plan}')}")
                            st.rerun()
                        else:
                            st.error(f"❌ {sonuc.get('mesaj', 'Hata')}")
else:
    st.info("Henuz kullanici yok.")


# ============================================================
# BEKLEYEN YUKSELTME TALEPLERI  (yukseltme_talepleri_admin)
# ============================================================
st.markdown("---")
st.subheader("⏳ " + t("admin.yukseltme_talepleri"))

sayac = db.yukseltme_sayaci()

col_a, col_b, col_c = st.columns(3)
col_a.metric(t("admin.bekleyen"), sayac.get("bekliyor", 0))
col_b.metric(t("admin.onaylanan"), sayac.get("onaylandi", 0))
col_c.metric(t("admin.reddedilen"), sayac.get("reddedildi", 0))

st.markdown("")

# Filtre
filtre = st.radio(
    t("admin.durum_filtre"),
    ["bekliyor", "onaylandi", "reddedildi", "hepsi"],
    format_func=lambda x: t(f"admin.durum_{x}"),
    horizontal=True,
    key="yukseltme_filtre",
)

durum_filtre = None if filtre == "hepsi" else filtre
talepler = db.yukseltme_listele(durum=durum_filtre, limit=100)

if not talepler:
    st.info(t("admin.talep_yok"))
else:
    for talep in talepler:
        durum = talep.get("durum", "?")
        ikon = {"bekliyor": "⏳", "onaylandi": "✅", "reddedildi": "❌"}.get(durum, "?")

        baslik = f"{ikon} **{talep.get('firma_adi') or talep.get('kullanici_adi')}** — {talep.get('istenen_plan', '?').upper()} — {talep.get('olusturma', '')[:16]}"

        with st.expander(baslik, expanded=(durum == "bekliyor")):
            c1, c2 = st.columns(2)

            with c1:
                st.write(f"**{t('admin.kullanici')}:** {talep.get('kullanici_adi', '-')}")
                st.write(f"**{t('admin.firma')}:** {talep.get('firma_adi') or '-'}")
                st.write(f"**{t('admin.eposta')}:** {talep.get('eposta') or '-'}")
                st.write(f"**{t('admin.mevcut_plan')}:** {talep.get('mevcut_plan', '?').upper()}")
                st.write(f"**{t('admin.istenen_plan')}:** {talep.get('istenen_plan', '?').upper()}")

            with c2:
                st.write(f"**{t('admin.odeme_yontemi')}:** {talep.get('odeme_yontemi', '-')}")
                st.write(f"**{t('admin.tarih')}:** {talep.get('olusturma', '-')}")
                if talep.get("islem_tarih"):
                    st.write(f"**{t('admin.islem_tarih')}:** {talep['islem_tarih']}")
                if talep.get("islem_yapan"):
                    st.write(f"**{t('admin.islem_yapan')}:** {talep['islem_yapan']}")

            # Fatura bilgisi
            with st.expander("📋 " + t("admin.fatura_bilgi")):
                st.write(talep.get("fatura_bilgi") or "-")

            if talep.get("notlar"):
                st.markdown("**" + t("admin.notlar") + ":**")
                st.write(talep["notlar"])

            # Aksiyon butonlari (sadece bekleyen)
            if durum == "bekliyor":
                st.markdown("---")
                btn1, btn2, _ = st.columns([1, 1, 3])

                with btn1:
                    if st.button(
                        "✅ " + t("admin.onayla"),
                        key=f"onayla_{talep['id']}",
                        type="primary",
                        use_container_width=True,
                    ):
                        sonuc = db.yukseltme_onayla(talep["id"], islem_yapan=auth.mevcut_kullanici().get("kullanici_adi", "admin"))
                        if sonuc.get("durum") == "OK":
                            try:
                                db.audit_kaydet(
                                    eylem="yukseltme_onaylandi",
                                    kullanici_adi=auth.mevcut_kullanici().get("kullanici_adi", "admin"),
                                    detay=f"Talep {talep['id']}: {talep['kullanici_adi']} -> {talep['istenen_plan']}",
                                )
                                from cache_utils import cache_temizle
                                cache_temizle()
                            except Exception:
                                pass
                            st.success(f"✅ {sonuc['kullanici_adi']} -> {sonuc['yeni_plan'].upper()}")
                            st.rerun()
                        else:
                            st.error(f"❌ {sonuc.get('mesaj', 'Hata')}")

                with btn2:
                    if st.button(
                        "❌ " + t("admin.reddet"),
                        key=f"reddet_{talep['id']}",
                        type="secondary",
                        use_container_width=True,
                    ):
                        sonuc = db.yukseltme_reddet(talep["id"], islem_yapan=auth.mevcut_kullanici().get("kullanici_adi", "admin"), sebep="Admin reddetti")
                        if sonuc.get("durum") == "OK":
                            st.success("❌ " + t("admin.reddedildi_mesaj"))
                            st.rerun()
                        else:
                            st.error(f"❌ {sonuc.get('mesaj', 'Hata')}")

