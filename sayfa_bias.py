"""
sayfa_bias.py - Bias ve Adillik Denetimi
CSV dataset yukleyip gruplar arasi oran farkini analiz eder.
"""
import streamlit as st
import auth
auth.giris_gerekli()

import db
import pandas as pd
from datetime import datetime


st.title("⚖️ Bias ve Adillik Denetimi")
st.markdown("**AI modelinizin önyargılı olup olmadığını test edin.**")
st.markdown("---")

kullanici = auth.mevcut_kullanici()
firma_id = kullanici.get("firma_id") if kullanici else None

# ============================================================
# ACIKLAMA
# ============================================================
st.info("""
📌 **Nasıl çalışır?**
1. Bir CSV dosyası yükleyin (ör. kredi başvuruları, işe alım kararları)
2. Hassas sütunu seçin (cinsiyet, yaş grubu, ırk)
3. Sonuç sütununu seçin (onay/red, 0/1)
4. Sistem gruplar arası farkı hesaplar → bias skoru verir
""")

# ============================================================
# DOSYA YUKLE
# ============================================================
st.subheader("📁 Dataset Yükle")

col1, col2 = st.columns(2)
with col1:
    sistem_adi = st.text_input("AI Sistemi Adı *", placeholder="Örn: Kredi Skorlama Modeli")
with col2:
    dataset_adi = st.text_input("Dataset Adı", placeholder="Örn: 2024 Kredi Başvuruları")

dosya = st.file_uploader("CSV Dosyası Yükle", type=["csv"])

if dosya is not None:
    try:
        df = pd.read_csv(dosya)
        st.success(f"✅ Yüklendi: {len(df)} satır, {len(df.columns)} sütun")
        st.markdown("**İlk 5 satır:**")
        st.dataframe(df.head())

        st.markdown("---")
        st.subheader("⚙️ Analiz Ayarları")

        col1, col2 = st.columns(2)
        with col1:
            hassas_sutun = st.selectbox("Hassas Sütun (cinsiyet, yaş, ırk vb.)", df.columns.tolist())
            hassas_degerler = df[hassas_sutun].dropna().unique().tolist()
            st.caption(f"Bulunan gruplar: {', '.join([str(x) for x in hassas_degerler[:5]])}")
        with col2:
            sonuc_sutun = st.selectbox("Sonuç Sütunu (onay/red, 0/1 vb.)", df.columns.tolist())
            pozitif_deger = st.text_input("Pozitif Sonuç Değeri (ör. '1', 'onay', 'evet')", value="1")

        st.markdown("---")

        if st.button("🔍 Bias Analizi Yap", type="primary", use_container_width=True):
            if not sistem_adi:
                st.error("Sistem Adı zorunludur.")
            elif not hassas_sutun or not sonuc_sutun:
                st.error("Hassas ve sonuç sütunu seçilmelidir.")
            else:
                try:
                    # Pozitif sonucu belirle
                    df["_pozitif"] = df[sonuc_sutun].astype(str).str.lower() == str(pozitif_deger).lower()

                    # Gruplara gore onay orani
                    oranlar = df.groupby(hassas_sutun)["_pozitif"].mean()
                    gruplar = oranlar.index.tolist()
                    oran_degerler = oranlar.values.tolist()

                    if len(gruplar) < 2:
                        st.warning("En az 2 grup gerekli (ör. kadın/erkek).")
                    else:
                        min_oran = min(oran_degerler)
                        max_oran = max(oran_degerler)
                        fark = max_oran - min_oran
                        bias_skoru = round(fark * 100, 1)

                        # Risk seviyesi
                        if bias_skoru < 10:
                            risk_seviyesi = "dusuk"
                            emoji = "🟢"
                        elif bias_skoru < 20:
                            risk_seviyesi = "orta"
                            emoji = "🟡"
                        else:
                            risk_seviyesi = "yuksek"
                            emoji = "🔴"

                        # Sonucu goster
                        st.markdown("---")
                        st.subheader("📊 Bias Analiz Sonucu")

                        col1, col2, col3 = st.columns(3)
                        col1.metric("Bias Skoru", f"%{bias_skoru}")
                        col2.metric("En Yüksek Oran", f"%{round(max_oran*100, 1)}")
                        col3.metric("En Düşük Oran", f"%{round(min_oran*100, 1)}")

                        if risk_seviyesi == "yuksek":
                            st.error(f"{emoji} **YÜKSEK BIAS TESPİT EDİLDİ** — Bu model ayrımcılık yapıyor olabilir.")
                        elif risk_seviyesi == "orta":
                            st.warning(f"{emoji} **ORTA SEVİYE BIAS** — İyileştirme önerilir.")
                        else:
                            st.success(f"{emoji} **DÜŞÜK BIAS** — Model adil görünüyor.")

                        st.markdown("### 📋 Gruplara Göre Onay Oranları")
                        for g, o in zip(gruplar, oran_degerler):
                            st.markdown(f"- **{g}**: %{round(o*100, 1)}")

                        st.markdown("### 💡 Öneriler")
                        if bias_skoru >= 20:
                            st.markdown("- Eğitim verisini yeniden dengeleyin")
                            st.markdown("- Hassas özellikleri modelden çıkarın veya maskeleyin")
                            st.markdown("- Fairness-aware algoritma kullanın")
                        elif bias_skoru >= 10:
                            st.markdown("- Azınlık grubun verisini artırın")
                            st.markdown("- Model performansını gruplara göre ayrı test edin")
                        else:
                            st.markdown("- Düzenli izlemeye devam edin")

                        # Kaydet
                        detay = {
                            "gruplar": [{"grup": str(g), "oran": float(o)} for g, o in zip(gruplar, oran_degerler)],
                            "max_oran": float(max_oran),
                            "min_oran": float(min_oran),
                            "fark": float(fark),
                        }
                        try:
                            db.bias_kaydet(
                                firma_id=firma_id,
                                sistem_adi=sistem_adi,
                                dataset_adi=dataset_adi or dosya.name,
                                hassas_sutun=hassas_sutun,
                                sonuc_sutun=sonuc_sutun,
                                bias_skoru=bias_skoru,
                                risk_seviyesi=risk_seviyesi,
                                detay=detay,
                            )
                            st.success("✅ Analiz kaydedildi.")
                        except Exception as e:
                            st.warning("Kayıt hatası: " + str(e))

                except Exception as e:
                    st.error("Analiz hatası: " + str(e))

    except Exception as e:
        st.error("Dosya okuma hatası: " + str(e))

# ============================================================
# GECMIS ANALIZLER
# ============================================================
st.markdown("---")
st.subheader("📚 Geçmiş Analizler")

try:
    gecmis = db.bias_listele(firma_id=firma_id)
except Exception:
    gecmis = []

if not gecmis:
    st.info("Henüz bias analizi yapılmadı.")
else:
    for g in gecmis:
        risk = g.get("risk_seviyesi", "-")
        emoji = {"dusuk": "🟢", "orta": "🟡", "yuksek": "🔴"}.get(risk, "⚪")
        with st.expander(f"{emoji} {g.get('sistem_adi', '-')} — Bias: %{g.get('bias_skoru', 0)}"):
            st.caption("**Tarih:** " + (g.get("olusturma") or "-"))
            st.caption("**Dataset:** " + (g.get("dataset_adi") or "-"))
            st.caption("**Hassas Sütun:** " + (g.get("hassas_sutun") or "-"))
            st.caption("**Sonuç Sütunu:** " + (g.get("sonuc_sutun") or "-"))
            col1, col2 = st.columns([4, 1])
            with col2:
                if st.button("🗑️", key="bias_sil_" + str(g["id"])):
                    db.bias_sil(g["id"])
                    st.rerun()
