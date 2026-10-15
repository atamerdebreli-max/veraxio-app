"""
sayfa_egitim.py - AI Farkindalik Egitim Modulu (5 dil)
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
# EGITIM ICERIKLERI - 5 DIL
# ============================================================
EGITIM_ICERIK = {
    "tr": {
        "MOD1": {
            "baslik": "AI Act Nedir?",
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
            "baslik": "Şeffaflık Yükümlülükleri (Madde 50)",
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
            "baslik": "Yüksek Riskli AI Sistemleri",
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
            "baslik": "Veri Yönetişimi ve KVKK",
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
            "baslik": "Etik AI ve Sorumluluk",
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
    },
    "en": {
        "MOD1": {
            "baslik": "What is AI Act?",
            "sure": "10 min",
            "icerik": """
## EU Artificial Intelligence Act (AI Act)

The AI Act is the European Union's first comprehensive law regulating AI systems.

### Key Facts
- **Entry into force:** August 1, 2024
- **Full application:** August 2, 2026
- **Scope:** All AI systems used in or affecting the EU

### Risk Categories
1. **Prohibited AI** (Article 5) — Social scoring, subliminal manipulation
2. **High-Risk AI** (Annex III) — Health, hiring, credit, education
3. **Limited Risk AI** (Article 50) — Chatbot, AI content, deepfake
4. **Minimal Risk AI** — All other AI systems

### Penalties
- **15 million Euro** or **3% of turnover** (whichever is higher)
""",
            "quiz": [
                {"soru": "When will the AI Act be fully applicable?",
                 "secenekler": ["August 1, 2024", "August 2, 2026", "January 1, 2027", "December 31, 2025"], "dogru": 1},
                {"soru": "What is the maximum penalty under the AI Act?",
                 "secenekler": ["1 million Euro", "5 million Euro", "15 million Euro or 3% of turnover", "10 million Euro"], "dogru": 2},
                {"soru": "Which of the following is PROHIBITED under the AI Act?",
                 "secenekler": ["Chatbot", "Social scoring", "AI image generation", "Text summarization"], "dogru": 1},
            ],
        },
        "MOD2": {
            "baslik": "Transparency Obligations (Article 50)",
            "sure": "15 min",
            "icerik": """
## Article 50 — Transparency Obligations

AI Act Article 50 introduces transparency rules for limited-risk AI systems.

### Mandatory Disclosures
1. **Chatbot:** Inform user of AI interaction
2. **AI Content:** Mark AI-generated content
3. **Deepfake:** Indicate synthetic media
4. **Emotion Recognition:** Notify user
5. **Biometric:** Categorization notice

### Disclosure Requirements
- Made at **first interaction**
- **Clear and understandable**
- **Accessible** format
- **Visible** and distinguishable

### Exceptions
- Free text under 200 tokens
- Format/editing-only changes
- Legally authorized uses
""",
            "quiz": [
                {"soru": "When should chatbot disclosure be made?",
                 "secenekler": ["When user asks", "At first interaction", "After 10 messages", "Not required"], "dogru": 1},
                {"soru": "Which risk category does AI Act Article 50 relate to?",
                 "secenekler": ["Prohibited AI", "High-risk", "Limited-risk (transparency)", "Minimal-risk"], "dogru": 2},
            ],
        },
        "MOD3": {
            "baslik": "High-Risk AI Systems",
            "sure": "15 min",
            "icerik": """
## High-Risk AI Systems (Article 6 + Annex III)

### Annex III — High-Risk Areas
1. **Biometric identification** (including remote)
2. **Critical infrastructure** (energy, water, transport)
3. **Education** (exams, grading)
4. **Employment** (hiring, promotion, dismissal)
5. **Credit scoring** (financial decisions)
6. **Health** (diagnosis, treatment)
7. **Migration** (asylum, visa)
8. **Law** (judicial support)

### Obligations for High-Risk Systems
- Risk management system (Article 9)
- Data governance (Article 10)
- Technical documentation (Article 11)
- Record keeping (Article 12)
- Transparency (Article 13)
- **Human oversight (Article 14)**
- Accuracy, robustness, cybersecurity (Article 15)
""",
            "quiz": [
                {"soru": "Which of the following is HIGH-RISK AI?",
                 "secenekler": ["Chatbot", "Credit scoring", "AI image generation", "Music recommendation"], "dogru": 1},
                {"soru": "Which obligation is mandatory for high-risk AI systems?",
                 "secenekler": ["Advertising", "Human oversight", "Free access", "Open source"], "dogru": 1},
            ],
        },
        "MOD4": {
            "baslik": "Data Governance and KVKK",
            "sure": "10 min",
            "icerik": """
## Data Governance and KVKK Compliance

### Data Principles in AI Systems
1. **Purpose Limitation:** Data processed only for specific purpose
2. **Data Minimization:** No unnecessary data collection
3. **Accuracy:** Data kept current and accurate
4. **Retention:** Deleted after legal period
5. **Transparency:** Information about processing

### Obligations under KVKK
- **Explicit Consent:** Required for personal data
- **Disclosure:** Data subject informed
- **Right to Object:** User can object to decision
- **Data Breach:** Notify within 72 hours

### Bias Management
- Training data must be balanced
- Group differences monitored
- Fairness tests performed regularly
""",
            "quiz": [
                {"soru": "Within how many hours must a data breach be notified?",
                 "secenekler": ["24 hours", "48 hours", "72 hours", "1 week"], "dogru": 2},
                {"soru": "What is required for personal data processing under KVKK?",
                 "secenekler": ["Company decision", "Explicit consent", "Manager approval", "State permit"], "dogru": 1},
            ],
        },
        "MOD5": {
            "baslik": "Ethical AI and Responsibility",
            "sure": "10 min",
            "icerik": """
## Ethical AI and Responsibility

### Core Ethical Principles
1. **Human Dignity:** AI does not harm human dignity
2. **Autonomy:** Human decision freedom protected
3. **Fairness:** AI does not discriminate
4. **Transparency:** Decisions explainable
5. **Responsibility:** Every decision has an owner
6. **Privacy:** Personal data protected

### Human Oversight
- **Human approval** mandatory in high-risk decisions
- "Auto-approval" prohibited
- Overseer must be trained
- Oversight decisions logged

### Corporate Responsibility
- AI policy must be documented
- Ethics committee established
- Regular employee training
- Violations reported
""",
            "quiz": [
                {"soru": "Which is NOT an ethical AI principle?",
                 "secenekler": ["Transparency", "Fairness", "Maximum profit", "Responsibility"], "dogru": 2},
                {"soru": "What is mandatory in high-risk AI decisions?",
                 "secenekler": ["Advertising", "Human oversight", "Free access", "Anonymity"], "dogru": 1},
            ],
        },
    },
    "bg": {
        "MOD1": {
            "baslik": "Какво е AI Act?",
            "sure": "10 мин",
            "icerik": """
## Закон за изкуствения интелект на ЕС (AI Act)

AI Act е първият всеобхватен закон на ЕС, регулиращ AI системите.

### Основни факти
- **Влизане в сила:** 1 август 2024
- **Пълно прилагане:** 2 август 2026
- **Обхват:** Всички AI системи в ЕС

### Категории риск
1. **Забранен AI** (Член 5) — Социално оценяване, подсъзнателна манипулация
2. **Високорисков AI** (Приложение III) — Здраве, наемане, кредит, образование
3. **Ограничен риск** (Член 50) — Чатбот, AI съдържание, deepfake
4. **Минимален риск** — Всички останали AI системи

### Санкции
- **15 милиона евро** или **3% от оборота** (по-високото)
""",
            "quiz": [
                {"soru": "Кога AI Act ще бъде напълно приложим?",
                 "secenekler": ["1 август 2024", "2 август 2026", "1 януари 2027", "31 декември 2025"], "dogru": 1},
                {"soru": "Каква е максималната глоба по AI Act?",
                 "secenekler": ["1 милион евро", "5 милиона евро", "15 милиона евро или 3% от оборота", "10 милиона евро"], "dogru": 2},
                {"soru": "Кое от следните е ЗАБРАНЕНО по AI Act?",
                 "secenekler": ["Чатбот", "Социално оценяване", "AI генериране на изображения", "Обобщаване на текст"], "dogru": 1},
            ],
        },
        "MOD2": {
            "baslik": "Задължения за прозрачност (Член 50)",
            "sure": "15 мин",
            "icerik": """
## Член 50 — Задължения за прозрачност

AI Act Член 50 въвежда правила за прозрачност за AI системи с ограничен риск.

### Задължителни уведомления
1. **Чатбот:** Информиране на потребителя
2. **AI съдържание:** Маркиране на AI съдържание
3. **Deepfake:** Посочване на синтетични медии
4. **Разпознаване на емоции:** Уведомление
5. **Биометричен:** Уведомление за категоризация

### Изисквания
- При **първо взаимодействие**
- **Ясно и разбираемо**
- **Достъпен** формат
- **Видимо** и различимо

### Изключения
- Свободен текст под 200 токена
- Само редакционни промени
- Законно разрешени употреби
""",
            "quiz": [
                {"soru": "Кога трябва да се направи уведомление за чатбот?",
                 "secenekler": ["Когато потребителят попита", "При първо взаимодействие", "След 10 съобщения", "Не е задължително"], "dogru": 1},
                {"soru": "Коя категория риск покрива Член 50?",
                 "secenekler": ["Забранен AI", "Високорисков", "Ограничен риск (прозрачност)", "Минимален риск"], "dogru": 2},
            ],
        },
        "MOD3": {
            "baslik": "Високорискови AI системи",
            "sure": "15 мин",
            "icerik": """
## Високорискови AI системи (Член 6 + Приложение III)

### Приложение III — Високорискови области
1. **Биометрична идентификация** (вкл. дистанционна)
2. **Критична инфраструктура** (енергия, вода, транспорт)
3. **Образование** (изпити, оценяване)
4. **Заетост** (наемане, повишение, уволнение)
5. **Кредитен рейтинг** (финансови решения)
6. **Здраве** (диагноза, лечение)
7. **Миграция** (убежище, виза)
8. **Право** (съдебна подкрепа)

### Задължения за високорискови системи
- Система за управление на риска (Член 9)
- Управление на данни (Член 10)
- Техническа документация (Член 11)
- Съхранение на записи (Член 12)
- Прозрачност (Член 13)
- **Човешки надзор (Член 14)**
- Точност, устойчивост, киберсигурност (Член 15)
""",
            "quiz": [
                {"soru": "Кое от следните е ВИСОКОРИСКОВ AI?",
                 "secenekler": ["Чатбот", "Кредитен рейтинг", "AI генериране на изображения", "Музикална препоръка"], "dogru": 1},
                {"soru": "Кое задължение е задължително за високорискови AI системи?",
                 "secenekler": ["Реклама", "Човешки надзор", "Безплатен достъп", "Отворен код"], "dogru": 1},
            ],
        },
        "MOD4": {
            "baslik": "Управление на данни и KVKK",
            "sure": "10 мин",
            "icerik": """
## Управление на данни и съответствие с KVKK

### Принципи на данните в AI системи
1. **Ограничение на целта:** Данни само за конкретна цел
2. **Минимизиране:** Без ненужно събиране
3. **Точност:** Актуални и точни данни
4. **Съхранение:** Изтриване след законния период
5. **Прозрачност:** Информация за обработката

### Задължения по KVKK
- **Изрично съгласие:** За лични данни
- **Уведомление:** Субектът на данни е информиран
- **Право на възражение:** Потребителят може да възрази
- **Нарушение:** Уведомяване в 72 часа

### Управление на пристрастия
- Обучителните данни трябва да са балансирани
- Разликите между групите се наблюдават
- Редовни тестове за справедливост
""",
            "quiz": [
                {"soru": "В колко часа трябва да се докладва нарушение на данни?",
                 "secenekler": ["24 часа", "48 часа", "72 часа", "1 седмица"], "dogru": 2},
                {"soru": "Какво е необходимо за обработка на лични данни по KVKK?",
                 "secenekler": ["Решение на фирмата", "Изрично съгласие", "Одобрение от ръководител", "Държавно разрешение"], "dogru": 1},
            ],
        },
        "MOD5": {
            "baslik": "Етичен AI и отговорност",
            "sure": "10 мин",
            "icerik": """
## Етичен AI и отговорност

### Основни етични принципи
1. **Човешко достойнство:** AI не уврежда достойнството
2. **Автономия:** Свободата на решението е защитена
3. **Справедливост:** AI не дискриминира
4. **Прозрачност:** Решенията са обясними
5. **Отговорност:** Всяко решение има собственик
6. **Поверителност:** Личните данни са защитени

### Човешки надзор
- **Човешко одобрение** задължително при високорискови решения
- "Автоматично одобрение" е забранено
- Надзорникът трябва да е обучен
- Решенията за надзор се записват

### Корпоративна отговорност
- AI политиката трябва да е документирана
- Създаване на етичен комитет
- Редовно обучение на служители
- Докладване на нарушения
""",
            "quiz": [
                {"soru": "Кой НЕ е етичен принцип за AI?",
                 "secenekler": ["Прозрачност", "Справедливост", "Максимална печалба", "Отговорност"], "dogru": 2},
                {"soru": "Какво е задължително при високорискови AI решения?",
                 "secenekler": ["Реклама", "Човешки надзор", "Безплатен достъп", "Анонимност"], "dogru": 1},
            ],
        },
    },
    "ro": {
        "MOD1": {
            "baslik": "Ce este AI Act?",
            "sure": "10 min",
            "icerik": """
## Regulamentul UE privind inteligența artificială (AI Act)

AI Act este prima lege cuprinzătoare a UE care reglementează sistemele AI.

### Informații cheie
- **Intrare în vigoare:** 1 august 2024
- **Aplicare completă:** 2 august 2026
- **Domeniu:** Toate sistemele AI din UE

### Categorii de risc
1. **AI interzis** (Articolul 5) — Scor social, manipulare subliminală
2. **AI cu risc ridicat** (Anexa III) — Sănătate, angajare, credit, educație
3. **AI cu risc limitat** (Articolul 50) — Chatbot, conținut AI, deepfake
4. **AI cu risc minim** — Toate celelalte sisteme AI

### Sancțiuni
- **15 milioane Euro** sau **3% din cifra de afaceri** (mai mare)
""",
            "quiz": [
                {"soru": "Când va fi pe deplin aplicabil AI Act?",
                 "secenekler": ["1 august 2024", "2 august 2026", "1 ianuarie 2027", "31 decembrie 2025"], "dogru": 1},
                {"soru": "Care este amenda maximă conform AI Act?",
                 "secenekler": ["1 milion Euro", "5 milioane Euro", "15 milioane Euro sau 3% din cifra de afaceri", "10 milioane Euro"], "dogru": 2},
                {"soru": "Care dintre următoarele este INTERZIS conform AI Act?",
                 "secenekler": ["Chatbot", "Scor social", "Generare imagini AI", "Rezumare text"], "dogru": 1},
            ],
        },
        "MOD2": {
            "baslik": "Obligații de transparență (Articolul 50)",
            "sure": "15 min",
            "icerik": """
## Articolul 50 — Obligații de transparență

AI Act Articolul 50 introduce reguli de transparență pentru sistemele AI cu risc limitat.

### Notificări obligatorii
1. **Chatbot:** Informarea utilizatorului
2. **Conținut AI:** Marcarea conținutului AI
3. **Deepfake:** Indicarea media sintetică
4. **Recunoaștere emoții:** Notificare
5. **Biometric:** Notificare de categorisire

### Cerințe
- La **prima interacțiune**
- **Clar și ușor de înțeles**
- Format **accesibil**
- **Vizibil** și distinctiv

### Excepții
- Text liber sub 200 tokeni
- Doar modificări de format/editare
- Utilizări autorizate legal
""",
            "quiz": [
                {"soru": "Când trebuie făcută notificarea chatbotului?",
                 "secenekler": ["Când întreabă utilizatorul", "La prima interacțiune", "După 10 mesaje", "Nu este necesar"], "dogru": 1},
                {"soru": "Care categorie de risc este acoperită de Articolul 50?",
                 "secenekler": ["AI interzis", "Risc ridicat", "Risc limitat (transparență)", "Risc minim"], "dogru": 2},
            ],
        },
        "MOD3": {
            "baslik": "Sisteme AI cu risc ridicat",
            "sure": "15 min",
            "icerik": """
## Sisteme AI cu risc ridicat (Articolul 6 + Anexa III)

### Anexa III — Domenii cu risc ridicat
1. **Identificare biometrică** (inclusiv la distanță)
2. **Infrastructură critică** (energie, apă, transport)
3. **Educație** (examene, notare)
4. **Angajare** (recrutare, promovare, concediere)
5. **Scor credit** (decizii financiare)
6. **Sănătate** (diagnostic, tratament)
7. **Migrație** (azil, viză)
8. **Drept** (suport judiciar)

### Obligații pentru sistemele cu risc ridicat
- Sistem de management al riscurilor (Art. 9)
- Guvernanța datelor (Art. 10)
- Documentație tehnică (Art. 11)
- Păstrarea înregistrărilor (Art. 12)
- Transparență (Art. 13)
- **Supraveghere umană (Art. 14)**
- Acuratețe, robustețe, securitate cibernetică (Art. 15)
""",
            "quiz": [
                {"soru": "Care dintre următoarele este AI CU RISC RIDICAT?",
                 "secenekler": ["Chatbot", "Scor credit", "Generare imagini AI", "Recomandare muzicală"], "dogru": 1},
                {"soru": "Care obligație este obligatorie pentru sistemele AI cu risc ridicat?",
                 "secenekler": ["Publicitate", "Supraveghere umană", "Acces gratuit", "Sursă deschisă"], "dogru": 1},
            ],
        },
        "MOD4": {
            "baslik": "Guvernanța datelor și KVKK",
            "sure": "10 min",
            "icerik": """
## Guvernanța datelor și conformitatea KVKK

### Principii ale datelor în sistemele AI
1. **Limitarea scopului:** Date doar pentru scop specific
2. **Minimizarea:** Fără colectare inutilă
3. **Acuratețe:** Date actuale și corecte
4. **Păstrare:** Ștergere după perioada legală
5. **Transparență:** Informații despre procesare

### Obligații conform KVKK
- **Consimțământ explicit:** Pentru date personale
- **Informare:** Subiectul datelor este informat
- **Dreptul de opoziție:** Utilizatorul poate obiecta
- **Breșă de date:** Notificare în 72 ore

### Managementul prejudecăților
- Datele de antrenament trebuie echilibrate
- Diferențele între grupuri monitorizate
- Teste de corectitudine regulate
""",
            "quiz": [
                {"soru": "În câte ore trebuie raportată o breșă de date?",
                 "secenekler": ["24 ore", "48 ore", "72 ore", "1 săptămână"], "dogru": 2},
                {"soru": "Ce este necesar pentru procesarea datelor personale conform KVKK?",
                 "secenekler": ["Decizia companiei", "Consimțământ explicit", "Aprobarea managerului", "Permis de stat"], "dogru": 1},
            ],
        },
        "MOD5": {
            "baslik": "AI etic și responsabilitate",
            "sure": "10 min",
            "icerik": """
## AI etic și responsabilitate

### Principii etice fundamentale
1. **Demnitate umană:** AI nu dăunează demnității
2. **Autonomie:** Libertatea deciziei este protejată
3. **Corectitudine:** AI nu discriminează
4. **Transparență:** Deciziile sunt explicabile
5. **Responsabilitate:** Fiecare decizie are un proprietar
6. **Confidențialitate:** Datele personale sunt protejate

### Supraveghere umană
- **Aprobare umană** obligatorie în decizii cu risc ridicat
- "Aprobare automată" interzisă
- Supraveghetorul trebuie instruit
- Deciziile de supraveghere înregistrate

### Responsabilitate corporativă
- Politica AI trebuie documentată
- Comitet etic înființat
- Instruire regulată a angajaților
- Încălcările raportate
""",
            "quiz": [
                {"soru": "Care NU este un principiu etic AI?",
                 "secenekler": ["Transparență", "Corectitudine", "Profit maxim", "Responsabilitate"], "dogru": 2},
                {"soru": "Ce este obligatoriu în deciziile AI cu risc ridicat?",
                 "secenekler": ["Publicitate", "Supraveghere umană", "Acces gratuit", "Anonimitate"], "dogru": 1},
            ],
        },
    },
    "hr": {
        "MOD1": {
            "baslik": "Što je AI Act?",
            "sure": "10 min",
            "icerik": """
## EU Zakon o umjetnoj inteligenciji (AI Act)

AI Act je prvi sveobuhvatni zakon EU koji regulira AI sustave.

### Ključne činjenice
- **Stupanje na snagu:** 1. kolovoza 2024.
- **Puna primjena:** 2. kolovoza 2026.
- **Opseg:** Svi AI sustavi u EU

### Kategorije rizika
1. **Zabranjen AI** (Članak 5) — Društveno ocjenjivanje, podsvjesna manipulacija
2. **AI visokog rizika** (Prilog III) — Zdravlje, zapošljavanje, kredit, obrazovanje
3. **AI ograničenog rizika** (Članak 50) — Chatbot, AI sadržaj, deepfake
4. **AI minimalnog rizika** — Svi ostali AI sustavi

### Kazne
- **15 milijuna eura** ili **3% prometa** (veće)
""",
            "quiz": [
                {"soru": "Kada će AI Act biti u potpunosti primjenjiv?",
                 "secenekler": ["1. kolovoza 2024.", "2. kolovoza 2026.", "1. siječnja 2027.", "31. prosinca 2025."], "dogru": 1},
                {"soru": "Koja je maksimalna kazna prema AI Act-u?",
                 "secenekler": ["1 milijun eura", "5 milijuna eura", "15 milijuna eura ili 3% prometa", "10 milijuna eura"], "dogru": 2},
                {"soru": "Što je od navedenog ZABRANJENO prema AI Act-u?",
                 "secenekler": ["Chatbot", "Društveno ocjenjivanje", "AI generiranje slika", "Sažimanje teksta"], "dogru": 1},
            ],
        },
        "MOD2": {
            "baslik": "Obveze transparentnosti (Članak 50)",
            "sure": "15 min",
            "icerik": """
## Članak 50 — Obveze transparentnosti

AI Act Članak 50 uvodi pravila transparentnosti za AI sustave ograničenog rizika.

### Obavezne obavijesti
1. **Chatbot:** Informiranje korisnika
2. **AI sadržaj:** Označavanje AI sadržaja
3. **Deepfake:** Naznaka sintetičkih medija
4. **Prepoznavanje emocija:** Obavijest
5. **Biometrijski:** Obavijest o kategorizaciji

### Zahtjevi
- Pri **prvoj interakciji**
- **Jasno i razumljivo**
- **Pristupačan** format
- **Vidljivo** i uočljivo

### Iznimke
- Slobodni tekst do 200 tokena
- Samo promjene formata/uređivanja
- Zakonski odobrene upotrebe
""",
            "quiz": [
                {"soru": "Kada treba dati obavijest chatbota?",
                 "secenekler": ["Kada korisnik pita", "Pri prvoj interakciji", "Nakon 10 poruka", "Nije potrebno"], "dogru": 1},
                {"soru": "Koja kategorija rizika je pokrivena Člankom 50?",
                 "secenekler": ["Zabranjen AI", "Visoki rizik", "Ograničeni rizik (transparentnost)", "Minimalni rizik"], "dogru": 2},
            ],
        },
        "MOD3": {
            "baslik": "AI sustavi visokog rizika",
            "sure": "15 min",
            "icerik": """
## AI sustavi visokog rizika (Članak 6 + Prilog III)

### Prilog III — Područja visokog rizika
1. **Biometrijska identifikacija** (uključujući daljinsku)
2. **Kritična infrastruktura** (energija, voda, transport)
3. **Obrazovanje** (ispiti, ocjenjivanje)
4. **Zapošljavanje** (zapošljavanje, promaknuće, otkaz)
5. **Kreditni rejting** (financijske odluke)
6. **Zdravlje** (dijagnoza, liječenje)
7. **Migracija** (azil, viza)
8. **Pravo** (sudska podrška)

### Obveze za sustave visokog rizika
- Sustav upravljanja rizicima (Članak 9)
- Upravljanje podacima (Članak 10)
- Tehnička dokumentacija (Članak 11)
- Čuvanje zapisa (Članak 12)
- Transparentnost (Članak 13)
- **Ljudski nadzor (Članak 14)**
- Točnost, robusnost, kibernetička sigurnost (Članak 15)
""",
            "quiz": [
                {"soru": "Što je od navedenog AI VISOKOG RIZIKA?",
                 "secenekler": ["Chatbot", "Kreditni rejting", "AI generiranje slika", "Glazbena preporuka"], "dogru": 1},
                {"soru": "Koja obveza je obavezna za AI sustave visokog rizika?",
                 "secenekler": ["Oglašavanje", "Ljudski nadzor", "Besplatan pristup", "Otvoreni kod"], "dogru": 1},
            ],
        },
        "MOD4": {
            "baslik": "Upravljanje podacima i KVKK",
            "sure": "10 min",
            "icerik": """
## Upravljanje podacima i usklađenost s KVKK

### Načela podataka u AI sustavima
1. **Ograničenje svrhe:** Podaci samo za određenu svrhu
2. **Minimizacija:** Bez nepotrebnog prikupljanja
3. **Točnost:** Ažurni i točni podaci
4. **Čuvanje:** Brisanje nakon zakonskog roka
5. **Transparentnost:** Informacije o obradi

### Obveze prema KVKK
- **Izričita privola:** Za osobne podatke
- **Informiranje:** Subjekt podataka informiran
- **Pravo na prigovor:** Korisnik može prigovoriti
- **Kršenje podataka:** Obavijest u 72 sata

### Upravljanje pristranošću
- Podaci za obuku moraju biti uravnoteženi
- Razlike između skupina prate se
- Redoviti testovi pravednosti
""",
            "quiz": [
                {"soru": "U koliko sati treba prijaviti kršenje podataka?",
                 "secenekler": ["24 sata", "48 sati", "72 sata", "1 tjedan"], "dogru": 2},
                {"soru": "Što je potrebno za obradu osobnih podataka prema KVKK?",
                 "secenekler": ["Odluka tvrtke", "Izričita privola", "Odobrenje upravitelja", "Državna dozvola"], "dogru": 1},
            ],
        },
        "MOD5": {
            "baslik": "Etički AI i odgovornost",
            "sure": "10 min",
            "icerik": """
## Etički AI i odgovornost

### Temeljna etička načela
1. **Ljudsko dostojanstvo:** AI ne šteti dostojanstvu
2. **Autonomija:** Sloboda odluke je zaštićena
3. **Pravednost:** AI ne diskriminira
4. **Transparentnost:** Odluke su objašnjive
5. **Odgovornost:** Svaka odluka ima vlasnika
6. **Privatnost:** Osobni podaci su zaštićeni

### Ljudski nadzor
- **Ljudsko odobrenje** obavezno u odlukama visokog rizika
- "Automatsko odobrenje" zabranjeno
- Nadzornik mora biti obučen
- Odluke nadzora se bilježe

### Korporativna odgovornost
- AI politika mora biti dokumentirana
- Etički odbor osnovan
- Redovita obuka zaposlenika
- Kršenja se prijavljuju
""",
            "quiz": [
                {"soru": "Što NIJE etičko načelo AI-a?",
                 "secenekler": ["Transparentnost", "Pravednost", "Maksimalni profit", "Odgovornost"], "dogru": 2},
                {"soru": "Što je obavezno u AI odlukama visokog rizika?",
                 "secenekler": ["Oglašavanje", "Ljudski nadzor", "Besplatan pristup", "Anonimnost"], "dogru": 1},
            ],
        },
    },
}

# ============================================================
# AKTIF DILE GORE ICERIK SEC
# ============================================================
dil = st.session_state.get("dil", "tr")
if dil not in EGITIM_ICERIK:
    dil = "tr"
MODULLER = EGITIM_ICERIK[dil]

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
    modul_secenekleri.append(f"{durum_emoji} {kod}: {m['baslik']} ({m['sure']})")

secili_modul_str = st.selectbox(t("egitim.modul_sec"), modul_secenekleri)
secili_kod = secili_modul_str.split(":")[0].replace("✅", "").replace("⏳", "").strip()

modul = MODULLER[secili_kod]

# ============================================================
# MODUL ICERIGI
# ============================================================
st.markdown("---")
st.markdown(f"## 📖 {modul['baslik']}")
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
                    modul_adi=modul["baslik"],
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
        sertifika += f"\n  ✅ {m['baslik']} — Skor: %{skor}"

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
