"""
sayfa_politikalar.py - Hazir Politika Sablonlari
AI Act uyumlulugu icin 6 hazir politika sablonu sunar.
"""
import streamlit as st
import auth
auth.giris_gerekli()

import db
from datetime import datetime


st.title("📋 Politika Şablonları")
st.markdown("**AI Act uyumluluğu için hazır politika şablonları.**")
st.markdown("---")

kullanici = auth.mevcut_kullanici()
firma_id = kullanici.get("firma_id") if kullanici else None
firma_adi = kullanici.get("ad_soyad") or kullanici.get("kullanici_adi") or "Şirket"

# ============================================================
# SABLONLAR
# ============================================================
SABLONLAR = {
    "AI Kullanım Politikası": {
        "kod": "AIKP",
        "aciklama": "Şirketinizdeki AI kullanımına ilişkin genel kurallar.",
        "icerik": """# AI KULLANIM POLİTİKASI

**Şirket:** {FIRMA}
**Tarih:** {TARIH}
**Versiyon:** 1.0

## 1. AMAÇ
Bu politika, {FIRMA} bünyesinde kullanılan tüm yapay zeka (AI) sistemlerinin
güvenli, etik ve yasalara uygun şekilde kullanılmasını sağlamayı amaçlar.

## 2. KAPSAM
Bu politika, şirket çalışanları, yükleniciler ve tüm AI sistemlerini kapsar.

## 3. YASAL DAYANAK
- AB Yapay Zeka Tüzüğü (AI Act) Madde 50
- KVKK (6698 sayılı Kanun)
- GDPR (AB 2016/679)
- İlgili sektörel mevzuat

## 4. TEMEL İLKELER
1. **Şeffaflık:** AI sistemlerinin kullanıldığı kullanıcıya açıkça bildirilir.
2. **Hesap Verebilirlik:** Her AI sistemi için bir sorumlu atanır.
3. **Adillik:** AI sistemleri ayrımcılık yapmaz.
4. **Gizlilik:** Kişisel veriler KVKK/GDPR uyumlu işlenir.
5. **İnsan Gözetimi:** Yüksek riskli kararlar insan onayından geçer.

## 5. SORUMLULUKLAR
- **Yönetim:** Politikayı onaylar ve kaynak sağlar.
- **AI Sorumlusu:** Sistemleri envanterde tutar, denetimleri yapar.
- **Çalışanlar:** Politikaya uyar, ihlalleri bildirir.
- **BT Departmanı:** Teknik önlemleri uygular.

## 6. YASAKLI KULLANIMLAR
- Sosyal skorlama
- Bilinçaltı manipülasyon
- Savunmasız grupları hedefleme
- Yasadışı içerik üretimi
- Kişisel verileri izinsiz işleme

## 7. İHLAL VE YAPTIRIM
Politika ihlalleri disiplin soruşturmasına yol açabilir.

## 8. GÖZDEN GEÇİRME
Bu politika yılda en az bir kez gözden geçirilir.

---
**Onaylayan:** _______________________
**Tarih:** {TARIH}
""",
    },
    "Veri Yönetişimi Politikası": {
        "kod": "VYP",
        "aciklama": "AI sistemlerinde kullanılan verilerin yönetimi.",
        "icerik": """# VERİ YÖNETİŞİMİ POLİTİKASI

**Şirket:** {FIRMA}
**Tarih:** {TARIH}
**Versiyon:** 1.0

## 1. AMAÇ
AI sistemlerinde kullanılan verilerin toplanması, işlenmesi, saklanması ve
imha edilmesine ilişkin kuralları belirler.

## 2. VERİ SINIFLANDIRMASI
- **Kamu:** Herkese açık veriler
- **İç:** Sadece çalışanlara açık
- **Gizli:** Sadece yetkililere açık
- **Çok Gizli:** Özel erişim gerektirir

## 3. KİŞİSEL VERİ İŞLEME
- Açık rıza alınır
- Aydınlatma yükümlülüğü yerine getirilir
- Veri minimizasyonu ilkesine uyulur
- Amaçla sınırlılık gözetilir

## 4. VERİ KAYNAKLARI
- Eğitim verisi kaynağı belgelenir
- Veri kalitesi kontrol edilir
- Bias taraması yapılır
- Üçüncü taraf veriler için lisans kontrol edilir

## 5. SAKLAMA VE İMHA
- KVKK/GDPR sürelerine uyulur
- Otomatik imha mekanizmaları kurulur
- Yedekler şifrelenir

## 6. VERİ AKTARIMI
- Yurt dışı aktarım için açık rıza veya yeterlilik kararı gerekir
- Aktarım kayıt altına alınır

## 7. VERİ İHLALİ
72 saat içinde ilgili otoriteye bildirilir.

---
**Onaylayan:** _______________________
**Tarih:** {TARIH}
""",
    },
    "Etik AI Politikası": {
        "kod": "EAP",
        "aciklama": "AI sistemlerinin etik ilkeleri.",
        "icerik": """# ETİK AI POLİTİKASI

**Şirket:** {FIRMA}
**Tarih:** {TARIH}
**Versiyon:** 1.0

## 1. AMAÇ
AI sistemlerinin etik ilkelere uygun geliştirilmesini ve kullanılmasını sağlar.

## 2. TEMEL ETİK İLKELER
1. **İnsan Onuru:** AI insan onurunu zedelemez.
2. **Özerklik:** İnsan karar alma özgürlüğü korunur.
3. **Adalet:** AI ayrımcılık yapmaz.
4. **Şeffaflık:** AI kararları açıklanabilir olmalıdır.
5. **Sorumluluk:** Her AI kararının bir sorumlusu vardır.
6. **Mahremiyet:** Kişisel veriler korunur.
7. **Sürdürülebilirlik:** AI çevreye zarar vermez.

## 3. RİSKLİ ALANLAR
- Sağlık kararları
- İşe alım / terfi
- Kredi skorlama
- Adli kararlar
- Eğitim değerlendirmesi
- Biyometrik tanımlama

Bu alanlarda AI kullanımı **insan gözetimi** gerektirir.

## 4. ETİK KURUL
Şirket bünyesinde bir Etik Kurul oluşturulur. Kurul:
- Yeni AI projelerini değerlendirir
- Etik ihlalleri inceler
- Politika güncellemelerini önerir

## 5. ŞEFFAFLIK
Kullanıcılar AI ile etkileşimde olduklarını bilir.

## 6. İTİRAZ HAKKI
Kullanıcılar AI kararlarına itiraz edebilir.

---
**Onaylayan:** _______________________
**Tarih:** {TARIH}
""",
    },
    "Şeffaflık Politikası": {
        "kod": "SP",
        "aciklama": "AI Act Madde 50 uyumlu şeffaflık kuralları.",
        "icerik": """# ŞEFFAFLIK POLİTİKASI

**Şirket:** {FIRMA}
**Tarih:** {TARIH}
**Versiyon:** 1.0

## 1. AMAÇ
AI Act Madde 50 kapsamında şeffaflık yükümlülüklerinin yerine getirilmesi.

## 2. AI BİLDİRİMİ
Aşağıdaki durumlarda kullanıcıya AI bildirimi yapılır:
- Chatbot / sanal asistan ile etkileşim
- AI tarafından üretilen içerik
- Duygu tanıma sistemleri
- Biyometrik kategorizasyon
- Deepfake içerik

## 3. BİLDİRİM ŞEKLİ
- **İlk etkileşimde** yapılır
- **Açık ve anlaşılır** dille
- **Erişilebilir** formatta
- **Görünür** ve **ayırt edilebilir** şekilde

## 4. AI İÇERİK İŞARETLEME
- Metin: Metadata + watermark
- Görsel: C2PA + görünür etiket
- Ses: İşitsel bildirim
- Video: Görsel + işitsel bildirim

## 5. İSTİSNALAR
- 200 token altı serbest metin
- Sadece format/düzenleme amaçlı değişiklikler
- Kanunla yetkilendirilmiş kullanımlar

## 6. KAYIT VE BELGELEME
Tüm bildirimler kayıt altına alınır.

## 7. GÖZDEN GEÇİRME
AI Act güncellemeleri takip edilir.

---
**Onaylayan:** _______________________
**Tarih:** {TARIH}
""",
    },
    "İnsan Gözetimi Politikası": {
        "kod": "IGP",
        "aciklama": "AI Act Madde 14 uyumlu insan gözetimi.",
        "icerik": """# İNSAN GÖZETİMİ POLİTİKASI

**Şirket:** {FIRMA}
**Tarih:** {TARIH}
**Versiyon:** 1.0

## 1. AMAÇ
AI Act Madde 14 kapsamında yüksek riskli AI sistemlerinde insan gözetimi.

## 2. KAPSAM
Aşağıdaki AI sistemleri insan gözetimi gerektirir:
- Sağlık kararları
- İşe alım / terfi
- Kredi skorlama
- Eğitim değerlendirmesi
- Kritik altyapı
- Biyometrik tanımlama

## 3. İNSAN GÖZETİMİ MEKANİZMASI
1. **Anlama:** Gözetmen AI çıktısını anlar.
2. **İzleme:** AI davranışını sürekli izler.
3. **Müdahale:** Gerekirse AI'ı durdurur.
4. **Geçersiz Kılma:** AI kararını reddedebilir.
5. **Onaylama:** Kritik kararları onaylar.

## 4. SORUMLULUKLAR
- Her AI sistemi için **gözetmen** atanır
- Gözetmen eğitim alır
- Gözetmen kararları kayıt altına alınır

## 5. OTOMASYON YASAKLARI
- İnsan onayı olmadan kritik karar verilemez
- "Otomatik onay" mekanizması kurulamaz
- Gözetmen atlanamaz

## 6. İTİRAZ MEKANİZMASI
Kullanıcılar AI kararlarına itiraz edebilir.

## 7. KAYIT
Tüm gözetim kararları 5 yıl saklanır.

---
**Onaylayan:** _______________________
**Tarih:** {TARIH}
""",
    },
    "Risk Yönetimi Politikası": {
        "kod": "RYP",
        "aciklama": "AI Act Madde 9 uyumlu risk yönetim sistemi.",
        "icerik": """# RİSK YÖNETİMİ POLİTİKASI

**Şirket:** {FIRMA}
**Tarih:** {TARIH}
**Versiyon:** 1.0

## 1. AMAÇ
AI Act Madde 9 kapsamında AI sistemlerine ilişkin risklerin sistematik yönetimi.

## 2. RİSK YÖNETİM SÜRECİ
1. **Tanımlama:** Riskler belirlenir
2. **Analiz:** Risklerin olasılığı ve etkisi değerlendirilir
3. **Değerlendirme:** Risk seviyesi belirlenir
4. **Önleme:** Önlemler planlanır
5. **Uygulama:** Önlemler hayata geçirilir
6. **İzleme:** Sürekli takip edilir
7. **Gözden Geçirme:** Periyodik olarak yeniden değerlendirilir

## 3. RİSK KATEGORİLERİ
- **Yasal Risk:** Ceza, dava
- **Operasyonel Risk:** Kesinti, hata
- **Etik Risk:** Ayrımcılık, mahremiyet ihlali
- **İtibar Riski:** Marka hasarı
- **Teknik Risk:** Güvenlik açığı, veri sızıntısı

## 4. RİSK SEVİYELERİ
- 🟢 **Düşük:** Kabul edilebilir
- 🟡 **Orta:** İyileştirme gerekli
- 🔴 **Yüksek:** Derhal müdahale
- ⛔ **Kritik:** Sistem durdurulmalı

## 5. SORUMLULUKLAR
- **Risk Yöneticisi:** Genel sorumluluk
- **AI Sorumlusu:** Sistem bazlı riskler
- **BT:** Teknik riskler
- **Hukuk:** Yasal riskler

## 6. DOKÜMANTASYON
Her risk kaydedilir, önlemler izlenir.

## 7. RAPORLAMA
Yönetime aylık risk raporu sunulur.

---
**Onaylayan:** _______________________
**Tarih:** {TARIH}
""",
    },
}

# ============================================================
# SABLON KARTLARI
# ============================================================
st.subheader("📚 Hazır Şablonlar")
st.caption("Her şablonu şirketiniz için uyarlayıp indirebilirsiniz. **Word/PDF** olarak kaydedebilirsiniz.")

for ad, sablon in SABLONLAR.items():
    with st.container():
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"### 📄 {ad}")
            st.caption(sablon["aciklama"])
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            # Icerik uret
            icerik = sablon["icerik"].format(
                FIRMA=firma_adi,
                TARIH=datetime.now().strftime("%d.%m.%Y"),
            )
            # Indir butonu
            st.download_button(
                label="📥 İndir",
                data=icerik.encode("utf-8"),
                file_name=f"{sablon['kod']}_{firma_adi.replace(' ', '_')}.md",
                mime="text/markdown",
                use_container_width=True,
                key="dl_" + sablon["kod"],
            )
        with st.expander("👁️ Önizleme"):
            st.markdown(sablon["icerik"].format(
                FIRMA=firma_adi,
                TARIH=datetime.now().strftime("%d.%m.%Y"),
            ))
        st.markdown("---")

# ============================================================
# INDIRME GECMISI
# ============================================================
st.subheader("📜 İndirme Geçmişi")

try:
    gecmis = db.politika_log_listele(firma_id=firma_id)
except Exception:
    gecmis = []

if not gecmis:
    st.info("Henüz şablon indirilmedi.")
else:
    for g in gecmis[:10]:
        st.caption("📄 **" + (g.get("sablon_adi") or "-") + "** — " + (g.get("olusturma") or "-"))
