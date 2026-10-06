"""
1) Kalan 2 HTML duzeltmesi
2) I18N objesini genislet (yeni anahtarlar icin 5 dil)
"""
import re
import shutil
from pathlib import Path
from datetime import datetime

KOK = Path(".")
HEDEF = KOK / "landing.html"

icerik = HEDEF.read_text(encoding="utf-8")

zaman = datetime.now().strftime("%Y%m%d_%H%M%S")
yedek = KOK / f"landing_i18n_son_oncesi_{zaman}.html.bak"
shutil.copy2(HEDEF, yedek)
print(f"[+] Yedek: {yedek.name}")

# ============================================================
# 1) KALAN 2 HTML DUZELTMESI
# ============================================================
# Hero badge text - regex ile bul
pattern_badge = r'AB AI Act Madde 50 Uyumlu(\s*</div>)'
if re.search(pattern_badge, icerik):
    icerik = re.sub(
        pattern_badge,
        r'<span data-i18n="hero_badge_text">AB AI Act Madde 50 Uyumlu</span>\1',
        icerik, count=1
    )
    print("[+] Hero badge cevrildi.")

# Features sub - regex ile bul (cok satirli)
pattern_feat = r'<p>(Manuel danışmanlığın 6-12 hafta ve 28\.000-62\.000 € maliyetini,)<br>(5 dakikalık ve 4\.900 TL/ay\'lık yazılım denetimine indirgiyoruz\.)</p>'
if re.search(pattern_feat, icerik):
    icerik = re.sub(
        pattern_feat,
        r'<p><span data-i18n="features_sub_1">\1</span><br><span data-i18n="features_sub_2">\2</span></p>',
        icerik, count=1
    )
    print("[+] Features sub cevrildi.")

# ============================================================
# 2) I18N OBJESINI GENISLET
# ============================================================
# Her dil icin eksik anahtarlari ekle

# TR icin yeni anahtarlar (zaten TR, eklemeye gerek yok ama guvenli)
YENI_TR = '''
        hero_badge_text: "AB AI Act Madde 50 Uyumlu",
        social_proof: "Yüzlerce şirket uyumluluğunu Veraxio ile yönetiyor",
        features_sub_1: "Manuel danışmanlığın 6-12 hafta ve 28.000-62.000 € maliyetini,",
        features_sub_2: "5 dakikalık ve 4.900 TL/ay'lık yazılım denetimine indirgiyoruz.",
        feat1_title: "11 AI Tipi Denetimi",
        feat1_desc: "Chatbot, görsel üretimi, deepfake, kamu yararı metni, duygu tanıma, KVKK uyumu, AB temsilcisi, Shadow AI, kümülatif analiz ve daha fazlası.",
        feat2_title: "4 Katmanlı Görsel Tespit",
        feat2_desc: "C2PA metadata + PNG/IPTC + SigLIP deepfake modeli + CLIP genel AI detektörü ile kapsamlı analiz.",
        feat3_title: "5 Dil Desteği",
        feat3_desc: "Türkçe, İngilizce, Bulgarca, Romence, Hırvatça. Balkanlar ve Doğu Avrupa pazarına hazır altyapı.",
        feat4_title: "Kanıt Zinciri",
        feat4_desc: "SHA-256 hash + zaman damgası. Denetime hazır PDF raporu. Hukuki dayanak ve sorumluluk reddi dahil.",
        plan1_feat1: "1 chatbot denetimi",
        plan1_feat2: "10 görsel / ay",
        plan1_feat3: "PDF rapor",
        plan1_feat4: "E-posta desteği",
        plan2_feat1: "5 chatbot denetimi",
        plan2_feat2: "50 görsel / ay",
        plan2_feat3: "REST API erişimi",
        plan2_feat4: "Zamanlanmış denetim",
        plan2_feat5: "Otomatik e-posta raporu",
        plan2_feat6: "Geçmiş arşivi",
        plan3_feat1: "Sınırsız denetim",
        plan3_feat2: "Özel entegrasyon",
        plan3_feat3: "Öncelikli destek",
        plan3_feat4: "Özel rapor",
        plan3_feat5: "AB temsilcisi takibi",
        footer_gizlilik: "Gizlilik Politikası",
        footer_kvkk: "KVKK Aydınlatma",
        footer_kullanim: "Kullanım Şartları",
        footer_dpa: "Veri İşleme Sözleşmesi",
        footer_disclaimer: "Bu sayfa teknik bir denetim aracını tanıtır. Hukuki görüş niteliği taşımaz. Nihai hukuki değerlendirme için uzman bir avukata başvurun.",
        footer_copyright: "© 2026 Veraxio. Tüm hakları saklıdır.",
'''

YENI_EN = '''
        hero_badge_text: "EU AI Act Article 50 Compliant",
        social_proof: "Hundreds of companies manage compliance with Veraxio",
        features_sub_1: "Manual consulting takes 6-12 weeks and costs 28,000-62,000 €.",
        features_sub_2: "We reduce it to a 5-minute audit at 4,900 TL/month.",
        feat1_title: "11 AI Type Audits",
        feat1_desc: "Chatbot, image generation, deepfake, public interest text, emotion recognition, KVKK compliance, EU representative, Shadow AI, cumulative analysis and more.",
        feat2_title: "4-Layer Visual Detection",
        feat2_desc: "Comprehensive analysis with C2PA metadata + PNG/IPTC + SigLIP deepfake model + CLIP general AI detector.",
        feat3_title: "5 Language Support",
        feat3_desc: "Turkish, English, Bulgarian, Romanian, Croatian. Ready for Balkans and Eastern Europe market.",
        feat4_title: "Chain of Evidence",
        feat4_desc: "SHA-256 hash + timestamp. Audit-ready PDF report. Includes legal basis and disclaimer.",
        plan1_feat1: "1 chatbot audit",
        plan1_feat2: "10 images / month",
        plan1_feat3: "PDF report",
        plan1_feat4: "Email support",
        plan2_feat1: "5 chatbot audits",
        plan2_feat2: "50 images / month",
        plan2_feat3: "REST API access",
        plan2_feat4: "Scheduled audits",
        plan2_feat5: "Automated email report",
        plan2_feat6: "History archive",
        plan3_feat1: "Unlimited audits",
        plan3_feat2: "Custom integration",
        plan3_feat3: "Priority support",
        plan3_feat4: "Custom report",
        plan3_feat5: "EU representative tracking",
        footer_gizlilik: "Privacy Policy",
        footer_kvkk: "KVKK Disclosure",
        footer_kullanim: "Terms of Service",
        footer_dpa: "Data Processing Agreement",
        footer_disclaimer: "This page presents a technical audit tool. It does not constitute legal advice. Consult a qualified lawyer for final legal assessment.",
        footer_copyright: "© 2026 Veraxio. All rights reserved.",
'''

YENI_BG = '''
        hero_badge_text: "Съвместим с член 50 от AI Act на ЕС",
        social_proof: "Стотици компании управляват съответствието си с Veraxio",
        features_sub_1: "Ръчният консултинг отнема 6-12 седмици и струва 28 000-62 000 €.",
        features_sub_2: "Ние го свеждаме до 5-минутен одит за 4 900 TL/месец.",
        feat1_title: "11 типа AI одити",
        feat1_desc: "Чатбот, генериране на изображения, дълбоки фалшификати, текст от обществен интерес, разпознаване на емоции, KVKK съответствие, представител в ЕС, Shadow AI, кумулативен анализ и още.",
        feat2_title: "4-слойно визуално откриване",
        feat2_desc: "Цялостен анализ с C2PA метаданни + PNG/IPTC + SigLIP модел за дълбоки фалшификати + CLIP общ AI детектор.",
        feat3_title: "Поддръжка на 5 езика",
        feat3_desc: "Турски, английски, български, румънски, хърватски. Готово за пазарите на Балканите и Източна Европа.",
        feat4_title: "Верига на доказателствата",
        feat4_desc: "SHA-256 хеш + времеви печат. PDF доклад, готов за одит. Включва правно основание и отказ от отговорност.",
        plan1_feat1: "1 чатбот одит",
        plan1_feat2: "10 изображения / месец",
        plan1_feat3: "PDF доклад",
        plan1_feat4: "Имейл поддръжка",
        plan2_feat1: "5 чатбот одита",
        plan2_feat2: "50 изображения / месец",
        plan2_feat3: "REST API достъп",
        plan2_feat4: "Планирани одити",
        plan2_feat5: "Автоматичен имейл доклад",
        plan2_feat6: "Архив на историята",
        plan3_feat1: "Неограничени одити",
        plan3_feat2: "Персонализирана интеграция",
        plan3_feat3: "Приоритетна поддръжка",
        plan3_feat4: "Персонализиран доклад",
        plan3_feat5: "Проследяване на представител в ЕС",
        footer_gizlilik: "Политика за поверителност",
        footer_kvkk: "KVKK разкритие",
        footer_kullanim: "Условия за ползване",
        footer_dpa: "Споразумение за обработка на данни",
        footer_disclaimer: "Тази страница представя технически инструмент за одит. Не представлява правен съвет. Консултирайте се с квалифициран адвокат.",
        footer_copyright: "© 2026 Veraxio. Всички права запазени.",
'''

YENI_RO = '''
        hero_badge_text: "Conform cu Articolul 50 din AI Act UE",
        social_proof: "Sute de companii isi gestioneaza conformitatea cu Veraxio",
        features_sub_1: "Consultanța manuala dureaza 6-12 saptamani și costa 28.000-62.000 €.",
        features_sub_2: "Reducem la un audit de 5 minute la 4.900 TL/luna.",
        feat1_title: "11 tipuri de audit AI",
        feat1_desc: "Chatbot, generare de imagini, deepfake, text de interes public, recunoastere a emotiilor, conformitate KVKK, reprezentant UE, Shadow AI, analiza cumulativa și altele.",
        feat2_title: "Detectie vizuala pe 4 straturi",
        feat2_desc: "Analiza cuprinzatoare cu metadate C2PA + PNG/IPTC + model deepfake SigLIP + detector AI general CLIP.",
        feat3_title: "Suport pentru 5 limbi",
        feat3_desc: "Turca, engleza, bulgara, romana, croata. Pregatit pentru piata Balcanilor și Europa de Est.",
        feat4_title: "Lanț de dovezi",
        feat4_desc: "Hash SHA-256 + marca temporala. Raport PDF pregatit pentru audit. Include baza legala și disclaimer.",
        plan1_feat1: "1 audit chatbot",
        plan1_feat2: "10 imagini / luna",
        plan1_feat3: "Raport PDF",
        plan1_feat4: "Suport email",
        plan2_feat1: "5 audituri chatbot",
        plan2_feat2: "50 imagini / luna",
        plan2_feat3: "Acces REST API",
        plan2_feat4: "Audituri programate",
        plan2_feat5: "Raport automatizat prin email",
        plan2_feat6: "Arhiva istoricului",
        plan3_feat1: "Audituri nelimitate",
        plan3_feat2: "Integrare personalizata",
        plan3_feat3: "Suport prioritar",
        plan3_feat4: "Raport personalizat",
        plan3_feat5: "Urmarirea reprezentantului UE",
        footer_gizlilik: "Politica de confidentialitate",
        footer_kvkk: "Divulgare KVKK",
        footer_kullanim: "Termeni de utilizare",
        footer_dpa: "Acord de prelucrare a datelor",
        footer_disclaimer: "Aceasta pagina prezinta un instrument tehnic de audit. Nu constituie consultanta juridica. Consultati un avocat calificat.",
        footer_copyright: "© 2026 Veraxio. Toate drepturile rezervate.",
'''

YENI_HR = '''
        hero_badge_text: "Sukladno s clankom 50. AI Act EU",
        social_proof: "Stotine tvrtki upravljaju svojom sukladnoscu s Veraxio",
        features_sub_1: "Rucno savjetovanje traje 6-12 tjedana i kosta 28.000-62.000 €.",
        features_sub_2: "Svodimo na 5-minutnu reviziju za 4.900 TL/mjesec.",
        feat1_title: "11 tipova AI revizija",
        feat1_desc: "Chatbot, generiranje slika, deepfake, tekst od javnog interesa, prepoznavanje emocija, KVKK sukladnost, predstavnik u EU, Shadow AI, kumulativna analiza i vise.",
        feat2_title: "Viseslojno vizualno otkrivanje",
        feat2_desc: "Sveobuhvatna analiza s C2PA metapodacima + PNG/IPTC + SigLIP deepfake model + CLIP opci AI detektor.",
        feat3_title: "Podrska za 5 jezika",
        feat3_desc: "Turski, engleski, bugarski, rumunjski, hrvatski. Spremno za trziste Balkana i Istocne Europe.",
        feat4_title: "Lanac dokaza",
        feat4_desc: "SHA-256 hash + vremenski zig. PDF izvjesce spremno za reviziju. Ukljucuje pravnu osnovu i odricanje odgovornosti.",
        plan1_feat1: "1 chatbot revizija",
        plan1_feat2: "10 slika / mjesec",
        plan1_feat3: "PDF izvjesce",
        plan1_feat4: "E-posta podrska",
        plan2_feat1: "5 chatbot revizija",
        plan2_feat2: "50 slika / mjesec",
        plan2_feat3: "REST API pristup",
        plan2_feat4: "Zakazane revizije",
        plan2_feat5: "Automatsko izvjesce e-postom",
        plan2_feat6: "Arhiva povijesti",
        plan3_feat1: "Neogranicene revizije",
        plan3_feat2: "Prilagođena integracija",
        plan3_feat3: "Prioritetna podrska",
        plan3_feat4: "Prilagođeno izvjesce",
        plan3_feat5: "Pracenje predstavnika u EU",
        footer_gizlilik: "Politika privatnosti",
        footer_kvkk: "KVKK objava",
        footer_kullanim: "Uvjeti koristenja",
        footer_dpa: "Ugovor o obradi podataka",
        footer_disclaimer: "Ova stranica predstavlja tehnicki alat za reviziju. Ne predstavlja pravni savjet. Posavjetujte se s kvalificiranim odvjetnikom.",
        footer_copyright: "© 2026 Veraxio. Sva prava zadrzana.",
'''

# Her dil blogu icin footer_copyright sonrasi ekle
# tr blogu: footer_copyright: "© 2026 Veraxio. Tüm hakları saklıdır.",

bloklar = [
    ('footer_copyright: "© 2026 Veraxio. Tüm hakları saklıdır.",', YENI_TR),
    ('footer_copyright: "© 2026 Veraxio. All rights reserved.",', YENI_EN),
    ('footer_copyright: "© 2026 Veraxio. Всички права запазени.",', YENI_BG),
    ('footer_copyright: "© 2026 Veraxio. Toate drepturile rezervate.",', YENI_RO),
    ('footer_copyright: "© 2026 Veraxio. Sva prava zadrzana.",', YENI_HR),
]

eklenen = 0
for anchor, ek in bloklar:
    if anchor in icerik:
        icerik = icerik.replace(anchor, anchor + ek, 1)
        eklenen += 1
    else:
        # Bosluk farkli olabilir
        anchor_tirnak = anchor.replace('"', '\\"')
        if anchor_tirnak in icerik:
            icerik = icerik.replace(anchor_tirnak, anchor_tirnak + ek, 1)
            eklenen += 1

print(f"[+] {eklenen}/5 dil blogu genisletildi.")

HEDEF.write_text(icerik, encoding="utf-8")
print("[+] landing.html kaydedildi.")
print()
print("=" * 60)
print("TEST: Tarayicida Ctrl+F5 -> 5 dil test et")
print("=" * 60)