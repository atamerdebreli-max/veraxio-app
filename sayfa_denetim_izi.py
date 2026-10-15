"""
sayfa_denetim_izi.py - Denetim Izi ve Degisiklik Gecmisi
Kim, ne zaman, ne yapti? Tum islem gecmisi.
"""
import streamlit as st
import auth
auth.giris_gerekli()

import db
from datetime import datetime, timedelta
import csv as _csv
import io as _io


st.title("📜 Denetim İzi")
st.markdown("**Kim, ne zaman, ne yaptı? Tüm işlem geçmişi.**")
st.markdown("---")

kullanici = auth.mevcut_kullanici()
firma_id = kullanici.get("firma_id") if kullanici else None

# ============================================================
# ISTATISTIK
# ============================================================
try:
    ozet = db.audit_ozet(firma_id)
    col1, col2, col3 = st.columns(3)
    col1.metric("Toplam Kayıt", ozet["toplam"])
    col2.metric("Başarılı", ozet["basarili"])
    col3.metric("Başarısız", ozet["basarisiz"])
    st.markdown("---")
except Exception as e:
    st.warning("İstatistik yüklenemedi: " + str(e))

# ============================================================
# EYLEM DAGILIMI
# ============================================================
try:
    dagilim = db.audit_eylem_dagilimi(firma_id)
    if dagilim:
        st.subheader("📊 Eylem Dağılımı")
        for d in dagilim[:10]:
            eylem = d.get("eylem", "-")
            sayi = d.get("n", 0)
            st.markdown(f"- **{eylem}**: {sayi} kez")
        st.markdown("---")
except Exception:
    pass

# ============================================================
# FILTRELER
# ============================================================
st.subheader("🔍 Filtrele")

col1, col2, col3 = st.columns(3)
with col1:
    filtre_kullanici = st.text_input("Kullanıcı Adı", placeholder="admin")
with col2:
    filtre_eylem = st.text_input("Eylem", placeholder="denetim_yapildi")
with col3:
    gun_sayisi = st.selectbox("Tarih Aralığı", ["Son 7 gün", "Son 30 gün", "Son 90 gün", "Tümü"])

# Tarih hesapla
tarih_bas = None
if gun_sayisi == "Son 7 gün":
    tarih_bas = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
elif gun_sayisi == "Son 30 gün":
    tarih_bas = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
elif gun_sayisi == "Son 90 gün":
    tarih_bas = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")

# ============================================================
# KAYITLAR
# ============================================================
st.markdown("---")
st.subheader("📋 Kayıtlar")

try:
    kayitlar = db.audit_filtrele(
        firma_id=firma_id,
        kullanici_adi=filtre_kullanici or None,
        eylem=filtre_eylem or None,
        tarih_bas=tarih_bas,
        limit=500,
    )
except Exception as e:
    st.error("Kayıtlar yüklenemedi: " + str(e))
    kayitlar = []

if not kayitlar:
    st.info("Kayıt bulunamadı.")
else:
    st.caption(f"**{len(kayitlar)} kayıt bulundu.**")

    # Tablo
    import pandas as pd
    df = pd.DataFrame(kayitlar)
    # Sadece onemli sutunlari goster
    goster = []
    for k in kayitlar:
        goster.append({
            "Tarih": k.get("tarih", "-"),
            "Kullanıcı": k.get("kullanici_adi") or "-",
            "Eylem": k.get("eylem", "-"),
            "Detay": (k.get("detay") or "")[:80],
            "Başarılı": "✅" if k.get("basarili") == 1 else "❌",
            "IP": k.get("ip_adresi") or "-",
        })
    df_goster = pd.DataFrame(goster)
    st.dataframe(df_goster, use_container_width=True)

    # CSV indir
    csv_buf = _io.StringIO()
    writer = _csv.writer(csv_buf)
    writer.writerow(["Tarih", "Kullanici", "Eylem", "Detay", "Basarili", "IP"])
    for k in kayitlar:
        writer.writerow([
            k.get("tarih", ""),
            k.get("kullanici_adi", ""),
            k.get("eylem", ""),
            k.get("detay", ""),
            "Evet" if k.get("basarili") == 1 else "Hayir",
            k.get("ip_adresi", ""),
        ])
    csv_bytes = csv_buf.getvalue().encode("utf-8-sig")

    st.download_button(
        label="📥 CSV İndir",
        data=csv_bytes,
        file_name="denetim_izi_" + datetime.now().strftime("%Y%m%d") + ".csv",
        mime="text/csv",
        use_container_width=True,
    )
