\# AI Uyumluluk Kutusu



\*\*AB AI Act Madde 50 Uyumluluk Denetim Platformu\*\*



AB Yapay Zeka Yasası'nın Madde 50 şeffaflık yükümlülüklerine uyumu, manuel danışmanlığın 6-12 hafta ve 28.000-62.000 € maliyetinden, 5 dakikalık ve 5.000 TL/ay'lık bir yazılım denetimine indirgiyoruz.



\## 🚀 Özellikler



\### 15 AI Tipi Denetimi

\- \*\*Chatbot / AI Asistan\*\* (Madde 50(1))

\- \*\*Görsel Üretimi\*\* — 4 katmanlı tespit (C2PA + Metadata + SigLIP + CLIP)

\- \*\*Metin Denetimi\*\* — RoBERTa + SynthID

\- \*\*Duygu Tanıma\*\* (Madde 50(3))

\- \*\*Biyometrik Sınıflandırma\*\* (Madde 50(3))

\- \*\*Deepfake İçerik\*\* (Madde 50(4)(a))

\- \*\*Kamu Yararı Metni\*\* (Madde 50(4)(b))

\- \*\*KVKK Uyum Denetimi\*\* (KVKK Madde 11)

\- \*\*AB Temsilcisi Kontrolü\*\* (Madde 22)

\- \*\*Shadow AI Taraması\*\*

\- \*\*Kümülatif Yükümlülük Analizi\*\*



\### Çoklu Dil Desteği

\- 🇹🇷 Türkçe

\- 🇬🇧 İngilizce

\- 🇧🇬 Bulgarca

\- 🇷🇴 Romence

\- 🇭🇷 Hırvatça



\### Çıktı Formatları

\- \*\*PDF\*\* — Detaylı denetim raporu (İngilizce)

\- \*\*JSON\*\* — Makine-okunabilir format

\- \*\*CSV\*\* — Tablo formatı



\### Hukuki Bağlam

\- \*\*LEGAL BASIS\*\* — AB AI Act + KVKK referansları

\- \*\*DISCLAIMER\*\* — Sorumluluk reddi

\- \*\*CHAIN OF CUSTODY\*\* — SHA-256 hash + zaman damgası

\- \*\*AI CONTENT LABELS\*\* — AB ikonları



\### REST API

\- `POST /denetle` — Tek denetim

\- `GET /gecmis` — Geçmiş listesi

\- `GET /istatistik` — İstatistikler



\### Veritabanı

\- SQLite ile geçmiş kayıtları

\- Filtreleme, dışa aktarma, silme



\## 📦 Kurulum



\### Gereksinimler

\- Python 3.10+

\- 4 GB RAM (model indirme için)

\- 2 GB disk alanı



\### Adım 1: Bağımlılıkları Yükleyin



```bash

pip install -r requirements.txt

