"""
Landing.html'de kalan TUM Turkce metinlere data-i18n ekler.
"""
import shutil
from pathlib import Path
from datetime import datetime

KOK = Path(".")
HEDEF = KOK / "landing.html"

icerik = HEDEF.read_text(encoding="utf-8")

zaman = datetime.now().strftime("%Y%m%d_%H%M%S")
yedek = KOK / f"landing_i18n_tam_oncesi_{zaman}.html.bak"
shutil.copy2(HEDEF, yedek)
print(f"[+] Yedek: {yedek.name}")

# ============================================================
# DEGISIKLIKLER
# ============================================================
DEGISIKLIKLER = [
    # 1) HERO BADGE
    ('<div class="hero-badge">',
     '<div class="hero-badge" data-i18n="hero_badge">'),
    ('<span class="dot"></span>\n                AB AI Act Madde 50 Uyumlu',
     '<span class="dot"></span>\n                <span data-i18n="hero_badge_text">AB AI Act Madde 50 Uyumlu</span>'),

    # 2) SOCIAL PROOF
    ('<span>Yüzlerce şirket uyumluluğunu Veraxio ile yönetiyor</span>',
     '<span data-i18n="social_proof">Yüzlerce şirket uyumluluğunu Veraxio ile yönetiyor</span>'),

    # 3) FEATURES SUB
    ('<p>Manuel danışmanlığın 6-12 hafta ve 28.000-62.000 € maliyetini,<br>5 dakikalık ve 4.900 TL/ay\'lık yazılım denetimine indirgiyoruz.</p>',
     '<p><span data-i18n="features_sub_1">Manuel danışmanlığın 6-12 hafta ve 28.000-62.000 € maliyetini,</span><br><span data-i18n="features_sub_2">5 dakikalık ve 4.900 TL/ay\'lık yazılım denetimine indirgiyoruz.</span></p>'),

    # 4) FEATURE CARDS - Title ve Desc
    ('<div class="feature-title">11 AI Tipi Denetimi</div>',
     '<div class="feature-title" data-i18n="feat1_title">11 AI Tipi Denetimi</div>'),
    ('<div class="feature-desc">Chatbot, görsel üretimi, deepfake, kamu yararı metni, duygu tanıma, KVKK uyumu, AB temsilcisi, Shadow AI, kümülatif analiz ve daha fazlası.</div>',
     '<div class="feature-desc" data-i18n="feat1_desc">Chatbot, görsel üretimi, deepfake, kamu yararı metni, duygu tanıma, KVKK uyumu, AB temsilcisi, Shadow AI, kümülatif analiz ve daha fazlası.</div>'),
    ('<div class="feature-title">4 Katmanlı Görsel Tespit</div>',
     '<div class="feature-title" data-i18n="feat2_title">4 Katmanlı Görsel Tespit</div>'),
    ('<div class="feature-desc">C2PA metadata + PNG/IPTC + SigLIP deepfake modeli + CLIP genel AI detektörü ile kapsamlı analiz.</div>',
     '<div class="feature-desc" data-i18n="feat2_desc">C2PA metadata + PNG/IPTC + SigLIP deepfake modeli + CLIP genel AI detektörü ile kapsamlı analiz.</div>'),
    ('<div class="feature-title">5 Dil Desteği</div>',
     '<div class="feature-title" data-i18n="feat3_title">5 Dil Desteği</div>'),
    ('<div class="feature-desc">Türkçe, İngilizce, Bulgarca, Romence, Hırvatça. Balkanlar ve Doğu Avrupa pazarına hazır altyapı.</div>',
     '<div class="feature-desc" data-i18n="feat3_desc">Türkçe, İngilizce, Bulgarca, Romence, Hırvatça. Balkanlar ve Doğu Avrupa pazarına hazır altyapı.</div>'),
    ('<div class="feature-title">Kanıt Zinciri</div>',
     '<div class="feature-title" data-i18n="feat4_title">Kanıt Zinciri</div>'),
    ('<div class="feature-desc">SHA-256 hash + zaman damgası. Denetime hazır PDF raporu. Hukuki dayanak ve sorumluluk reddi dahil.</div>',
     '<div class="feature-desc" data-i18n="feat4_desc">SHA-256 hash + zaman damgası. Denetime hazır PDF raporu. Hukuki dayanak ve sorumluluk reddi dahil.</div>'),

    # 5) PRICING - STARTER
    ('<li>1 chatbot denetimi</li>',
     '<li data-i18n="plan1_feat1">1 chatbot denetimi</li>'),
    ('<li>10 görsel / ay</li>',
     '<li data-i18n="plan1_feat2">10 görsel / ay</li>'),
    ('<li>PDF rapor</li>',
     '<li data-i18n="plan1_feat3">PDF rapor</li>'),
    ('<li>E-posta desteği</li>',
     '<li data-i18n="plan1_feat4">E-posta desteği</li>'),
    ('<div class="plan-target">Mikro KOBİ · Tek AI ürünü</div>',
     '<div class="plan-target" data-i18n="plan_target1">Mikro KOBİ · Tek AI ürünü</div>'),

    # 6) PRICING - PRO
    ('<li>5 chatbot denetimi</li>',
     '<li data-i18n="plan2_feat1">5 chatbot denetimi</li>'),
    ('<li>50 görsel / ay</li>',
     '<li data-i18n="plan2_feat2">50 görsel / ay</li>'),
    ('<li>REST API erişimi</li>',
     '<li data-i18n="plan2_feat3">REST API erişimi</li>'),
    ('<li>Zamanlanmış denetim</li>',
     '<li data-i18n="plan2_feat4">Zamanlanmış denetim</li>'),
    ('<li>Otomatik e-posta raporu</li>',
     '<li data-i18n="plan2_feat5">Otomatik e-posta raporu</li>'),
    ('<li>Geçmiş arşivi</li>',
     '<li data-i18n="plan2_feat6">Geçmiş arşivi</li>'),
    ('<div class="plan-target">KOBİ · Çoklu AI ürünü</div>',
     '<div class="plan-target" data-i18n="plan_target2">KOBİ · Çoklu AI ürünü</div>'),

    # 7) PRICING - ENTERPRISE
    ('<li>Sınırsız denetim</li>',
     '<li data-i18n="plan3_feat1">Sınırsız denetim</li>'),
    ('<li>Özel entegrasyon</li>',
     '<li data-i18n="plan3_feat2">Özel entegrasyon</li>'),
    ('<li>Öncelikli destek</li>',
     '<li data-i18n="plan3_feat3">Öncelikli destek</li>'),
    ('<li>Özel rapor</li>',
     '<li data-i18n="plan3_feat4">Özel rapor</li>'),
    ('<li>AB temsilcisi takibi</li>',
     '<li data-i18n="plan3_feat5">AB temsilcisi takibi</li>'),
    ('<div class="plan-target">Kurumsal · Çoklu lokasyon</div>',
     '<div class="plan-target" data-i18n="plan_target3">Kurumsal · Çoklu lokasyon</div>'),

    # 8) EARLY BIRD
    ('<div class="early-bird-title">Erken Kuş İndirimi</div>',
     '<div class="early-bird-title" data-i18n="early_bird_title">Erken Kuş İndirimi</div>'),
    ('<div class="early-bird-desc">\n                İlk 10 müşteriye Pro paket <strong>6.900 TL/ay</strong> (%47 indirim) — 12 aylık taahhüt ile\n            </div>',
     '<div class="early-bird-desc" data-i18n="early_bird_desc">\n                İlk 10 müşteriye Pro paket <strong>6.900 TL/ay</strong> (%47 indirim) — 12 aylık taahhüt ile\n            </div>'),

    # 9) FORM LABELS
    ('<label for="ad">Adınız Soyadınız *</label>',
     '<label for="ad" data-i18n="form_name">Adınız Soyadınız *</label>'),
    ('<label for="email">E-posta *</label>',
     '<label for="email" data-i18n="form_email">E-posta *</label>'),
    ('<label for="sirket">Şirket Adı</label>',
     '<label for="sirket" data-i18n="form_company">Şirket Adı</label>'),
    ('<label for="telefon">Telefon</label>',
     '<label for="telefon" data-i18n="form_phone">Telefon</label>'),
    ('<label for="mesaj">Mesajınız (opsiyonel)</label>',
     '<label for="mesaj" data-i18n="form_message">Mesajınız (opsiyonel)</label>'),
    ('<button type="submit" class="btn btn-primary">📩 Demo Talebi Gönder</button>',
     '<button type="submit" class="btn btn-primary" data-i18n="form_send">📩 Demo Talebi Gönder</button>'),

    # 10) FOOTER HUKUKI LINKS
    ('<a href="gizlilik.html">Gizlilik Politikası</a>',
     '<a href="gizlilik.html" data-i18n="footer_gizlilik">Gizlilik Politikası</a>'),
    ('<a href="kvkk.html">KVKK Aydınlatma</a>',
     '<a href="kvkk.html" data-i18n="footer_kvkk">KVKK Aydınlatma</a>'),
    ('<a href="kullanim.html">Kullanım Şartları</a>',
     '<a href="kullanim.html" data-i18n="footer_kullanim">Kullanım Şartları</a>'),
    ('<a href="dpa.html">Veri İşleme Sözleşmesi</a>',
     '<a href="dpa.html" data-i18n="footer_dpa">Veri İşleme Sözleşmesi</a>'),

    # 11) FOOTER DISCLAIMER
    ('<div class="footer-disclaimer">\n            Bu sayfa teknik bir denetim aracını tanıtır. Hukuki görüş niteliği taşımaz.\n            Nihai hukuki değerlendirme için uzman bir avukata başvurun.\n        </div>',
     '<div class="footer-disclaimer" data-i18n="footer_disclaimer">\n            Bu sayfa teknik bir denetim aracını tanıtır. Hukuki görüş niteliği taşımaz.\n            Nihai hukuki değerlendirme için uzman bir avukata başvurun.\n        </div>'),

    # 12) FOOTER COPYRIGHT
    ('<div class="footer-copyright">\n            © 2026 Veraxio. Tüm hakları saklıdır.\n        </div>',
     '<div class="footer-copyright" data-i18n="footer_copyright">\n            © 2026 Veraxio. Tüm hakları saklıdır.\n        </div>'),
]

eklenen = 0
bulunamayan = []

for eski, yeni in DEGISIKLIKLER:
    if eski in icerik:
        icerik = icerik.replace(eski, yeni, 1)
        eklenen += 1
    else:
        bulunamayan.append(eski[:60])

print(f"[+] {eklenen} degisiklik yapildi.")
if bulunamayan:
    print(f"[!] {len(bulunamayan)} degisiklik bulunamadi:")
    for b in bulunamayan[:10]:
        print(f"    - {b}")
    print()

HEDEF.write_text(icerik, encoding="utf-8")
print("[+] landing.html kaydedildi.")
print()
print("=" * 60)
print("SONRAKI: I18N objesini genislet")
print("=" * 60)