"""
landing.html'de hangi Turkce metinlerin data-i18n'siz kaldigini bulur.
"""
import re
from pathlib import Path

icerik = Path("landing.html").read_text(encoding="utf-8")

# Bilinen Turkce kelimeler
TURKCE_KELIMELER = [
    "Uyumlu", "şirket", "uyumluluğunu", "yönetiyor",
    "Manuel", "danışmanlığın", "hafta", "maliyetini",
    "dakikalık", "yazılım", "denetimine", "indirgiyoruz",
    "Tipi", "Denetimi", "Katmanlı", "Görsel", "Tespit",
    "Dil", "Desteği", "Kanıt", "Zinciri",
    "chatbot", "denetimi", "görsel", "rapor",
    "Mikro", "KOBİ", "Kurumsal", "Çoklu", "lokasyon",
    "Erken", "Kuş", "İndirimi", "müşteriye",
    "Adınız", "Soyadınız", "E-posta", "Şirket",
    "Telefon", "Mesajınız", "Demo Talebi Gönder",
    "Gizlilik", "Politikası", "Aydınlatma",
    "Kullanım", "Şartları", "Veri", "İşleme", "Sözleşmesi",
    "sayfa", "teknik", "aracını", "tanıtır",
    "Hukuki", "görüş", "niteliği", "taşımaz",
    "Nihai", "değerlendirme", "uzman", "avukata",
    "başvurun", "hakları", "saklıdır",
]

# Satirlari tara
satirlar = icerik.split("\n")
eksik = []

for i, satir in enumerate(satirlar, 1):
    # Bu satirda Turkce kelime var mi?
    if not any(k in satir for k in TURKCE_KELIMELER):
        continue

    # data-i18n var mi?
    if "data-i18n" in satir:
        continue

    # Sadece HTML tag'li satirlar (JS/CSS degil)
    if satir.strip().startswith(("//", "/*", "*", "const", "let", "var")):
        continue

    # Icerik kismi
    satir_temiz = satir.strip()
    if satir_temiz:
        eksik.append((i, satir_temiz[:110]))

print("=" * 80)
print(f"DATA-I18N'SIZ TURKCE SATIRLAR: {len(eksik)}")
print("=" * 80)
print()

for satir_no, icerik_kisa in eksik:
    print(f"Satir {satir_no}:")
    print(f"  {icerik_kisa}")
    print()