"""
Hesabim sayfasi - KVKK/GDPR haklarim
- Kendi verilerimi indir (JSON)
- Hesabimi sil (right to be forgotten)
"""
import json
from datetime import datetime

import streamlit as st
import auth
auth.giris_gerekli()

import db
from i18n import t

db.init_db()

kullanici = auth.mevcut_kullanici()
kullanici_adi = kullanici.get("kullanici_adi", "-")
firma_id_k = auth.firma_id()
firma_adi_k = auth.firma_adi() or "-"

st.title("👤 " + t("hesabim.baslik"))
st.markdown(t("hesabim.aciklama"))
st.markdown("---")

# ============================================================
# 1) HESAP BILGILERI
# ============================================================
st.subheader("📋 " + t("hesabim.bilgi_baslik"))

c1, c2 = st.columns(2)
with c1:
    st.write(f"**{t('hesabim.ad_soyad')}:** {kullanici.get('ad_soyad') or '-'}")
    st.write(f"**{t('hesabim.kullanici_adi')}:** {kullanici_adi}")
    st.write(f"**{t('hesabim.eposta')}:** {kullanici.get('eposta') or '-'}")
with c2:
    st.write(f"**{t('hesabim.firma')}:** {firma_adi_k}")
    st.write(f"**{t('hesabim.rol')}:** {kullanici.get('rol', 'user').upper()}")
    st.write(f"**{t('hesabim.firma_rol')}:** {kullanici.get('firma_rol', 'user').upper()}")

st.markdown("---")

# ============================================================
# 2) VERIMI INDIR (KVKK md.11 / GDPR md.15)
# ============================================================
st.subheader("📥 " + t("hesabim.export_baslik"))
st.caption(t("hesabim.export_aciklama"))

if st.button("📥 " + t("hesabim.export_btn"), type="primary", use_container_width=True):
    with st.spinner(t("hesabim.export_hazirlaniyor")):
        try:
            # 1) Kullanici bilgileri
            kullanici_veri = {
                "kullanici_adi": kullanici_adi,
                "ad_soyad": kullanici.get("ad_soyad"),
                "eposta": kullanici.get("eposta"),
                "rol": kullanici.get("rol"),
                "firma_rol": kullanici.get("firma_rol"),
                "firma_id": firma_id_k,
                "firma_adi": firma_adi_k,
                "olusturma": kullanici.get("olusturma"),
                "son_giris": kullanici.get("son_giris"),
            }

            # 2) Denetim kayitlari (firma bazli)
            denetimler = db.listele(limit=None, filtre_firma_id=firma_id_k)

            # 3) Audit log (kendi eylemleri)
            try:
                audit_log = db.audit_listele(limit=1000, kullanici_adi=kullanici_adi, firma_id=firma_id_k)
            except Exception:
                audit_log = []

            # 4) Zamanlanmis denetimler
            try:
                tum_zaman = db.zamanlanmis_listele(aktif_only=False)
                zamanlanmis = [z for z in tum_zaman if z.get("firma_id") == firma_id_k]
            except Exception:
                zamanlanmis = []

            # Paket
            export = {
                "export_tarihi": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "export_turu": "KVKK Madde 11 / GDPR Madde 15 - Veri Erisim Talebi",
                "kullanici": kullanici_veri,
                "denetimler": denetimler,
                "audit_log": audit_log,
                "zamanlanmis_denetimler": zamanlanmis,
                "ozet": {
                    "toplam_denetim": len(denetimler),
                    "toplam_audit_log": len(audit_log),
                    "toplam_zamanlanmis": len(zamanlanmis),
                },
            }

            json_bytes = json.dumps(export, ensure_ascii=False, indent=2, default=str).encode("utf-8")
            dosya_adi = f"verilerim_{kullanici_adi}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            st.success("✅ " + t("hesabim.export_hazir"))
            st.download_button(
                label="📥 " + t("hesabim.export_indir"),
                data=json_bytes,
                file_name=dosya_adi,
                mime="application/json",
                use_container_width=True,
                key="hesabim_export_dl",
            )
            st.caption(f"📊 {t('hesabim.export_ozet')}: "
                       f"{len(denetimler)} denetim, "
                       f"{len(audit_log)} log, "
                       f"{len(zamanlanmis)} zamanlanmis")

        except Exception as e:
            st.error(f"❌ {t('hesabim.export_hata')}: {e}")

st.markdown("---")

# ============================================================
# 3) HESABIMI SIL (KVKK md.7 / GDPR md.17)
# ============================================================
st.subheader("🗑️ " + t("hesabim.sil_baslik"))
st.warning(t("hesabim.sil_uyari"))

with st.expander("⚠️ " + t("hesabim.sil_detay")):
    st.write(t("hesabim.sil_aciklama_1"))
    st.write(t("hesabim.sil_aciklama_2"))
    st.write(t("hesabim.sil_aciklama_3"))

    onay = st.checkbox(t("hesabim.sil_onay"), key="hesabim_sil_onay")

    if onay:
        # Yazma onayi
        yazilan = st.text_input(
            t("hesabim.sil_yaz") + f' ("{kullanici_adi}")',
            key="hesabim_sil_yaz",
        )

        if st.button("🗑️ " + t("hesabim.sil_btn"), type="secondary", use_container_width=True):
            if yazilan.strip() != kullanici_adi:
                st.error("❌ " + t("hesabim.sil_eslesmedi"))
            else:
                try:
                    # Audit log (silmeden once)
                    try:
                        db.audit_kaydet(
                            eylem="kullanici_kendi_hesabini_sildi",
                            kullanici_adi=kullanici_adi,
                            firma_id=firma_id_k,
                            detay=f"KVKK/GDPR kapsaminda hesap silindi: {kullanici_adi}",
                        )
                    except Exception:
                        pass

                    # Sil
                    db.kullanici_sil(kullanici_adi)

                    # Cikis
                    auth.cikis_yap()
                    st.success("✅ " + t("hesabim.sil_basarili"))
                    st.info(t("hesabim.sil_sonra"))
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ {t('hesabim.sil_hata')}: {e}")