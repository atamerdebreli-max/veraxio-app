"""
sayfa_egitim.py - AI Farkindalik Egitim Modulu
"""
import streamlit as st
import auth
auth.giris_gerekli()

import db
from i18n import t
from datetime import datetime


st.title("🎓 " + t("egitim.baslik"))
st.markdown("**" + t("egitim.alt_baslik") + "**")
st.markdown("---")

kullanici = auth.mevcut_kullanici()
firma_id = kullanici.get("firma_id") if kullanici else None
kullanici_adi = kullanici.get("kullanici_adi", "?")

# ============================================================
# MODULLER
# ============================================================
MODULLER = {
    "MOD1": {
        "anahtar_baslik": "egitim.mod1_baslik",
        "sure": "10 dk",
        "icerik": """
## AB Yapay Zeka Tüzüğü (AI Act)

AI Act, Avrupa Birliği'nin yapay zeka sistemlerini düzenleyen ilk kapsamlı yasasıdır.

### Temel Bilgiler
- **Yürürlük tarihi:** 1 Ağustos 2024
- **Tam uygulama:** 2 Ağustos 2026
- **Kapsam:** AB'de kullanılan veya AB'ye etki eden tüm AI sistemleri

### Risk Kategorileri
1. **Yasak AI** (Madde 5) — Sosyal skorlama, bilinçaltı manipülasyon
2. **Yüksek Riskli AI** (Ek III) — Sağlık, işe alım, kredi, eğitim
3. **Sınırlı Riskli AI** (Madde 50) — Chatbot, AI içerik, deepfake
4. **Minimal Riskli AI** — Diğer tüm AI sistemleri

### Cezalar
- **15 milyon Euro** veya **cironun %3'ü** (hangisi yüksekse)
""",
        "quiz": [
            {"soru": "AI Act hangi tarihte tam olarak uygulanmaya başlayacak?",
             "secenekler": ["1 Ağustos 2024", "2 Ağustos 2026", "1 Ocak 2027", "31 Aralık 2025"], "dogru": 1},
            {"soru": "AI Act kapsamında maksimum ceza nedir?",
             "secenekler": ["1 milyon Euro", "5 milyon Euro", "15 milyon Euro veya cironun %3'ü", "10 milyon Euro"], "dogru": 2},
            {"soru": "Aşağıdakilerden hangisi AI Act'te YASAK kategorisindedir?",
             "secenekler": ["Chatbot", "Sosyal skorlama", "AI görsel üretimi", "Metin özetleme"], "dogru": 1},
        ],
    },
    "MOD2": {
        "anahtar_baslik": "egitim.mod2_baslik",
        "sure": "15 dk",
        "icerik": """
## Madde 50 — Şeffaflık Yükümlülükleri

AI Act Madde 50, sınırlı riskli AI sistemleri için şeffaflık kuralları getirir.

### Zorunlu Bildirimler
1. **Chatbot:** Kullanıcıya AI ile etkileşimde olduğunu bildirme
2. **AI İçerik:** AI tarafından üretilen içeriği işaretleme
3. **Deepfake:** Sentetik medya olduğunu belirtme
4. **Duygu Tanıma:** Kullanıcıya bildirim
5. **Biyometrik:** Kategorizasyon bildirimi

### Bildirim Şartları
- **İlk etkileşimde** yapılmalı
- **Açık ve anlaşılır** olmalı
- **Erişilebilir** formatta olmalı
- **Görünür** ve ayırt edilebilir olmalı

### İstisnalar
- 200 token altı serbest metin
- Sadece format/düzenleme amaçlı değişiklikler
- Kanunla yetkilendirilmiş kullanımlar
""",
        "quiz": [
            {"soru": "Chatbot bildirimi ne zaman yapılmalı?",
             "secenekler": ["Kullanıcı sorduğunda", "İlk etkileşimde", "10 mesaj sonra", "Şart değil"], "dogru": 1},
            {"soru": "AI Act Madde 50 hangi risk kategorisiyle ilgilidir?",
             "secenekler": ["Yasak AI", "Yüksek riskli", "Sınırlı riskli (şeffaflık)", "Minimal riskli"], "dogru": 2},
        ],
    },
    "MOD3": {
        "anahtar_baslik": "egitim.mod3_baslik",
        "sure": "15 dk",
        "icerik": """
## Yüksek Riskli AI Sistemleri (Madde 6 + Ek III)

### Ek III — Yüksek Riskli Alanlar
1. **Biyometrik tanımlama** (uzaktan dahil)
2. **Kritik altyapı** (enerji, su, ulaşım)
3. **Eğitim** (sınav, not değerlendirme)
4. **İstihdam** (işe alım, terfi, işten çıkarma)
5. **Kredi skorlama** (finansal kararlar)
6. **Sağlık** (teşhis, tedavi)
7. **Göç** (sığınma, vize)
8. **Hukuk** (yargı desteği)

### Yüksek Riskli Sistemler için Yükümlülükler
- Risk yönetim sistemi (Madde 9)
- Veri yönetişimi (Madde 10)
- Teknik dokümantasyon (Madde 11)
- Kayıt tutma (Madde 12)
- Şeffaflık (Madde 13)
- **İnsan gözetimi (Madde 14)**
- Doğruluk, sağlamlık, siber güvenlik (Madde 15)
""",
        "quiz": [
            {"soru": "Aşağıdakilerden hangisi YÜKSEK RİSKLİ AI kategorisindedir?",
             "secenekler": ["Chatbot", "Kredi skorlama", "AI görsel üretimi", "Müzik önerisi"], "dogru": 1},
            {"soru": "Yüksek riskli AI sistemleri için hangi yükümlülük zorunludur?",
             "secenekler": ["Reklam", "İnsan gözetimi", "Ücretsiz erişim", "Açık kaynak"], "dogru": 1},
        ],
    },
    "MOD4": {
        "anahtar_baslik": "egitim.mod4_baslik",
        "sure": "10 dk",
        "icerik": """
## Veri Yönetişimi ve KVKK Uyumu

### AI Sistemlerinde Veri İlkeleri
1. **Amaçla Sınırlılık:** Veri sadece belirli amaç için işlenir
2. **Veri Minimizasyonu:** Gereksiz veri toplanmaz
3. **Doğruluk:** Veriler güncel ve doğru tutulur
4. **Saklama Süresi:** Kanuni süre sonunda silinir
5. **Şeffaflık:** Veri işleme hakkında bilgilendirme

### KVKK Kapsamında Yükümlülükler
- **Açık Rıza:** Kişisel veri işleme için gerekli
- **Aydınlatma:** Veri sahibine bilgi verilir
- **İtiraz Hakkı:** Kullanıcı karara itiraz edebilir
- **Veri İhlali:** 72 saat içinde bildirim

### Bias (Önyargı) Yönetimi
- Eğitim verisi dengeli olmalı
- Gruplar arası fark izlenmeli
- Adillik testleri düzenli yapılmalı
""",
        "quiz": [
            {"soru": "Veri ihlali kaç saat içinde bildirilmelidir?",
             "secenekler": ["24 saat", "48 saat", "72 saat", "1 hafta"], "dogru": 2},
            {"soru": "KVKK kapsamında kişisel veri işleme için ne gerekir?",
             "secenekler": ["Şirket kararı", "Açık rıza", "Yönetici onayı", "Devlet izni"], "dogru": 1},
        ],
    },
    "MOD5": {
        "anahtar_baslik": "egitim.mod5_baslik",
        "sure": "10 dk",
        "icerik": """
## Etik AI ve Sorumluluk

### Temel Etik İlkeler
1. **İnsan Onuru:** AI insan onurunu zedelemez
2. **Özerklik:** İnsan karar özgürlüğü korunur
3. **Adalet:** AI ayrımcılık yapmaz
4. **Şeffaflık:** Kararlar açıklanabilir
5. **Sorumluluk:** Her kararın sorumlusu var
6. **Mahremiyet:** Kişisel veriler korunur

### İnsan Gözetimi
- Yüksek riskli kararlarda **insan onayı** zorunlu
- "Otomatik onay" yasak
- Gözetmen eğitimli olmalı
- Gözetim kararları kayıt altında

### Şirket Sorumluluğu
- AI politikası yazılı olmalı
- Etik kurul oluşturulmalı
- Çalışan eğitimi düzenli yapılmalı
- İhlaller bildirilmeli
""",
        "quiz": [
            {"soru": "Etik AI ilkelerinden biri DEĞİLDİR?",
             "secenekler": ["Şeffaflık", "Adalet", "Maksimum kâr", "Sorumluluk"], "dogru": 2},
            {"soru": "Yüksek riskli AI kararlarında ne zorunludur?",
             "secenekler": ["Reklam", "İnsan gözetimi", "Ücretsiz erişim", "Anonimlik"], "dogru": 1},
        ],
    },
}

# ============================================================
# KULLANICI EGITIM DURUMU
# ============================================================
try:
    tamamlanan = db.egitim_listele(kullanici_adi)
except Exception:
    tamamlanan = []

tamamlanan_kodlar = {t_item["modul_kodu"]: t_item for t_item in tamamlanan if t_item.get("tamamlandi") == 1}

st.subheader(t("egitim.durum"))
toplam_modul = len(MODULLER)
tamamlanan_sayi = len(tamamlanan_kodlar)
ilerleme = round(100 * tamamlanan_sayi / toplam_modul, 0) if toplam_modul else 0

col1, col2, col3 = st.columns(3)
col1.metric(t("egitim.toplam_modul"), toplam_modul)
col2.metric(t("egitim.tamamlanan"), tamamlanan_sayi)
col3.metric(t("egitim.ilerleme"), f"%{ilerleme}")

st.progress(ilerleme / 100)
st.markdown("---")

# ============================================================
# MODUL SECIMI
# ============================================================
st.subheader(t("egitim.moduller"))

modul_secenekleri = []
for kod, m in MODULLER.items():
    durum_emoji = "✅" if kod in tamamlanan_kodlar else "⏳"
    modul_secenekleri.append(f"{durum_emoji} {kod}: {t(m['anahtar_baslik'])} ({m['sure']})")

secili_modul_str = st.selectbox(t("egitim.modul_sec"), modul_secenekleri)
secili_kod = secili_modul_str.split(":")[0].replace("✅", "").replace("⏳", "").strip()

modul = MODULLER[secili_kod]

# ============================================================
# MODUL ICERIGI
# ============================================================
st.markdown("---")
st.markdown(f"## 📖 {t(modul['anahtar_baslik'])}")
st.caption(f"⏱️ {modul['sure']}")
st.markdown(modul["icerik"])

st.markdown("---")
st.markdown("## " + t("egitim.quiz"))
st.caption(t("egitim.quiz_caption"))

dogru_sayisi = 0
toplam_soru = len(modul["quiz"])
cevaplar = []

with st.form(f"quiz_{secili_kod}"):
    for i, soru in enumerate(modul["quiz"]):
        st.markdown(f"**{i+1}. {soru['soru']}**")
        secim = st.radio(
            t("egitim.cevap"),
            soru["secenekler"],
            key=f"quiz_{secili_kod}_{i}",
            label_visibility="collapsed",
        )
        cevaplar.append(soru["secenekler"].index(secim))
        st.markdown("")

    if st.form_submit_button(t("egitim.gonder"), type="primary", use_container_width=True):
        dogru_sayisi = sum(1 for i, c in enumerate(cevaplar) if c == modul["quiz"][i]["dogru"])
        quiz_skoru = round(100 * dogru_sayisi / toplam_soru, 0)

        if quiz_skoru >= 70:
            st.success(t("egitim.tebrikler").format(dogru=dogru_sayisi, toplam=toplam_soru, skor=int(quiz_skoru)))
            try:
                db.egitim_kaydet(
                    firma_id=firma_id,
                    kullanici_adi=kullanici_adi,
                    modul_kodu=secili_kod,
                    modul_adi=t(modul["anahtar_baslik"]),
                    quiz_skoru=int(quiz_skoru),
                    tamamlandi=1,
                )
                st.balloons()
                st.rerun()
            except Exception as e:
                st.warning(t("egitim.kayit_hatasi") + str(e))
        else:
            st.error(t("egitim.tekrar_dene").format(dogru=dogru_sayisi, toplam=toplam_soru, skor=int(quiz_skoru)))

# ============================================================
# SERTIFIKA
# ============================================================
if tamamlanan_sayi == toplam_modul:
    st.markdown("---")
    st.success(t("egitim.sertifika"))

    sertifika = f"""
═══════════════════════════════════════════
      AI FARKINDALIK SERTİFİKASI
═══════════════════════════════════════════

Bu sertifika,

    {kullanici.get('ad_soyad') or kullanici_adi}

tarafından AI Act ve AI etiği konusunda
{tamamlanan_sayi} modüllük eğitim programının
başarıyla tamamlandığını belgeler.

Tarih: {datetime.now().strftime('%d.%m.%Y')}

Modüller:
"""
    for kod, m in MODULLER.items():
        kayit = tamamlanan_kodlar.get(kod, {})
        skor = kayit.get("quiz_skoru", 0)
        sertifika += f"\n  ✅ {t(m['anahtar_baslik'])} — Skor: %{skor}"

    sertifika += f"""

Sertifika No: CERT-{kullanici_adi}-{datetime.now().strftime('%Y%m%d')}

═══════════════════════════════════════════
         ◆ Veraxio
   AB AI Act Madde 50 Uyumluluk Platformu
═══════════════════════════════════════════
"""

    st.download_button(
        label=t("egitim.sertifika_indir"),
        data=sertifika.encode("utf-8"),
        file_name=f"sertifika_{kullanici_adi}.txt",
        mime="text/plain",
        use_container_width=True,
    )

# ============================================================
# KAYITLAR
# ============================================================
st.markdown("---")
st.subheader(t("egitim.kayitlar"))

if not tamamlanan:
    st.info(t("egitim.kayit_yok"))
else:
    for t_item in tamamlanan:
        if t_item.get("tamamlandi") == 1:
            st.markdown(f"✅ **{t_item.get('modul_adi', '-')}** — Skor: %{t_item.get('quiz_skoru', 0)} — {t_item.get('olusturma', '')[:10]}")
