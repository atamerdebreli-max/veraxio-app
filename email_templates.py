"""
Veraxio Email Sablonlari - HTML
Koyu tema + mavi vurgu (landing ile uyumlu)
5 dil destegi
"""
from datetime import datetime


# ============================================================
# ORTAK HEADER / FOOTER
# ============================================================
def _header(baslik=""):
    return f'''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Veraxio</title>
</head>
<body style="margin:0; padding:0; background:#0a0a0a; font-family: 'Helvetica Neue', Arial, sans-serif; color:#fafafa;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#0a0a0a; padding: 40px 20px;">
<tr>
<td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="max-width:600px; background:#171717; border-radius:12px; border:1px solid #262626; overflow:hidden;">

<!-- UST MAVI SERIT -->
<tr>
<td style="background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%); height: 6px; line-height: 6px; font-size: 6px;">&nbsp;</td>
</tr>

<!-- LOGO -->
<tr>
<td style="padding: 32px 40px 16px 40px;">
<table cellpadding="0" cellspacing="0">
<tr>
<td style="width: 32px; height: 32px; background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%); border-radius: 8px; text-align: center; vertical-align: middle; color: #ffffff; font-size: 18px; font-weight: bold;">&#9670;</td>
<td style="padding-left: 12px; font-size: 22px; font-weight: 800; color: #fafafa; letter-spacing: -0.5px;">Veraxio</td>
</tr>
</table>
<div style="color: #737373; font-size: 12px; margin-top: 8px;">AI Act Compliance Platform | veraxio.ai</div>
</td>
</tr>

<!-- BASLIK -->
<tr>
<td style="padding: 8px 40px 0 40px;">
<h1 style="color: #fafafa; font-size: 24px; font-weight: 700; margin: 0; letter-spacing: -0.5px;">{baslik}</h1>
</td>
</tr>

<!-- AYIRICI -->
<tr>
<td style="padding: 20px 40px 0 40px;">
<div style="height: 1px; background: #262626;"></div>
</td>
</tr>

<!-- ICERIK -->
<tr>
<td style="padding: 24px 40px 32px 40px; color: #d4d4d4; font-size: 15px; line-height: 1.7;">
'''


def _footer(dil="tr"):
    yil = datetime.now().year

    FOOTER_METIN = {
        "tr": {
            "kapanis": "Sorularınız için: info@veraxio.ai",
            "telif": f"© {yil} Veraxio. Tüm hakları saklıdır.",
            "hukuki": "Bu e-posta teknik bir bildirimdir. Hukuki görüş niteliği taşımaz.",
        },
        "en": {
            "kapanis": "Questions? Contact: info@veraxio.ai",
            "telif": f"© {yil} Veraxio. All rights reserved.",
            "hukuki": "This email is a technical notification. It does not constitute legal advice.",
        },
        "bg": {
            "kapanis": "Въпроси? Пишете на: info@veraxio.ai",
            "telif": f"© {yil} Veraxio. Всички права запазени.",
            "hukuki": "Този имейл е техническо известие. Не представлява правен съвет.",
        },
        "ro": {
            "kapanis": "Intrebari? Contactati: info@veraxio.ai",
            "telif": f"© {yil} Veraxio. Toate drepturile rezervate.",
            "hukuki": "Acest email este o notificare tehnica. Nu constituie consultanta juridica.",
        },
        "hr": {
            "kapanis": "Pitanja? Kontaktirajte: info@veraxio.ai",
            "telif": f"© {yil} Veraxio. Sva prava zadrzana.",
            "hukuki": "Ovaj email je tehnicka obavijest. Ne predstavlja pravni savjet.",
        },
    }

    m = FOOTER_METIN.get(dil, FOOTER_METIN["tr"])

    return f'''
</td>
</tr>

<!-- AYIRICI -->
<tr>
<td style="padding: 0 40px;">
<div style="height: 1px; background: #262626;"></div>
</td>
</tr>

<!-- FOOTER -->
<tr>
<td style="padding: 24px 40px 32px 40px; text-align: center; color: #737373; font-size: 13px; line-height: 1.6;">
<div style="margin-bottom: 12px;">{m["kapanis"]}</div>
<div style="margin-bottom: 16px;">
<a href="https://veraxio.ai" style="color: #60a5fa; text-decoration: none; font-weight: 500;">veraxio.ai</a>
</div>
<div style="color: #525252; font-size: 11px; margin-bottom: 8px;">{m["hukuki"]}</div>
<div style="color: #404040; font-size: 11px;">{m["telif"]}</div>
</td>
</tr>

</table>
</td>
</tr>
</table>
</body>
</html>'''


# ============================================================
# BUTON
# ============================================================
def _buton(metin, link):
    return f'''
<table cellpadding="0" cellspacing="0" style="margin: 24px 0;">
<tr>
<td style="background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); border-radius: 10px;">
<a href="{link}" style="display: inline-block; padding: 14px 32px; color: #ffffff; text-decoration: none; font-weight: 600; font-size: 15px;">{metin}</a>
</td>
</tr>
</table>'''


# ============================================================
# BILGI KUTUSU
# ============================================================
def _bilgi_kutusu(metin, tip="info"):
    renkler = {
        "info": ("rgba(59,130,246,0.1)", "rgba(59,130,246,0.3)", "#3b82f6"),
        "success": ("rgba(34,197,94,0.1)", "rgba(34,197,94,0.3)", "#22c55e"),
        "warning": ("rgba(245,158,11,0.1)", "rgba(245,158,11,0.3)", "#f59e0b"),
        "error": ("rgba(239,68,68,0.1)", "rgba(239,68,68,0.3)", "#ef4444"),
    }
    bg, br, bl = renkler.get(tip, renkler["info"])
    return f'''
<div style="background: {bg}; border: 1px solid {br}; border-left: 4px solid {bl}; padding: 16px 20px; border-radius: 10px; margin: 20px 0; color: #d4d4d4; font-size: 14px; line-height: 1.6;">
{metin}
</div>'''


# ============================================================
# 1) HOS GELDIN EMAILI
# ============================================================
def hos_geldin_email(kullanici_adi, firma_adi, dil="tr"):
    S = {
        "tr": {
            "baslik": f"Veraxio'ya Hoş Geldiniz, {kullanici_adi}!",
            "selam": f"Merhaba <strong>{kullanici_adi}</strong>,",
            "metin": f"<strong>{firma_adi}</strong> firması için Veraxio hesabınız oluşturuldu. 7 günlük ücretsiz deneme süreniz başladı.",
            "ozellik": "<strong>Şimdi ne yapabilirsiniz?</strong>",
            "adim1": "✅ İlk denetiminizi yapın (5 dakika)",
            "adim2": "✅ PDF raporu indirin (Blockchain zaman damgalı)",
            "adim3": "✅ Zamanlanmış denetim kurun (haftalık otomatik)",
            "buton": "Dashboard'a Git",
            "kutu": "💡 <strong>İpucu:</strong> Tek Denetim sayfasından chatbot, görsel veya deepfake denetimi yapabilirsiniz.",
        },
        "en": {
            "baslik": f"Welcome to Veraxio, {kullanici_adi}!",
            "selam": f"Hello <strong>{kullanici_adi}</strong>,",
            "metin": f"Your Veraxio account for <strong>{firma_adi}</strong> has been created. Your 7-day free trial has started.",
            "ozellik": "<strong>What can you do now?</strong>",
            "adim1": "✅ Run your first audit (5 minutes)",
            "adim2": "✅ Download PDF report (Blockchain timestamped)",
            "adim3": "✅ Set up scheduled audit (weekly automatic)",
            "buton": "Go to Dashboard",
            "kutu": "💡 <strong>Tip:</strong> Audit chatbots, images, or deepfakes from the Single Audit page.",
        },
        "bg": {
            "baslik": f"Добре дошли в Veraxio, {kullanici_adi}!",
            "selam": f"Здравейте <strong>{kullanici_adi}</strong>,",
            "metin": f"Вашият Veraxio акаунт за <strong>{firma_adi}</strong> е създаден. Започна 7-дневният ви безплатен пробен период.",
            "ozellik": "<strong>Какво можете да направите сега?</strong>",
            "adim1": "✅ Направете първия си одит (5 минути)",
            "adim2": "✅ Изтеглете PDF доклад (с блокчейн времеви печат)",
            "adim3": "✅ Настройте планиран одит (автоматично седмично)",
            "buton": "Към таблото",
            "kutu": "💡 <strong>Съвет:</strong> Одитирайте чатботове, изображения или дълбоки фалшификати от страницата за единичен одит.",
        },
        "ro": {
            "baslik": f"Bine ati venit la Veraxio, {kullanici_adi}!",
            "selam": f"Buna <strong>{kullanici_adi}</strong>,",
            "metin": f"Contul dvs. Veraxio pentru <strong>{firma_adi}</strong> a fost creat. Perioada de proba gratuita de 7 zile a inceput.",
            "ozellik": "<strong>Ce puteti face acum?</strong>",
            "adim1": "✅ Efectuati primul audit (5 minute)",
            "adim2": "✅ Descarcati raportul PDF (cu marca temporala blockchain)",
            "adim3": "✅ Configurati audit programat (automat saptamanal)",
            "buton": "Mergi la Tablou",
            "kutu": "💡 <strong>Sfat:</strong> Auditati chatboturi, imagini sau deepfake-uri din pagina de audit simplu.",
        },
        "hr": {
            "baslik": f"Dobrodosli u Veraxio, {kullanici_adi}!",
            "selam": f"Pozdrav <strong>{kullanici_adi}</strong>,",
            "metin": f"Vas Veraxio racun za <strong>{firma_adi}</strong> je stvoren. Započelo je vase 7-dnevno besplatno probno razdoblje.",
            "ozellik": "<strong>Sto mozete uciniti sada?</strong>",
            "adim1": "✅ Obavite prvu reviziju (5 minuta)",
            "adim2": "✅ Preuzmite PDF izvjesce (s blockchain vremenskim zigom)",
            "adim3": "✅ Postavite zakazanu reviziju (automatski tjedno)",
            "buton": "Idi na Nadzornu plocu",
            "kutu": "💡 <strong>Savjet:</strong> Revizirajte chatbotove, slike ili deepfake iz stranice za pojedinacnu reviziju.",
        },
    }
    s = S.get(dil, S["tr"])

    icerik = _header(s["baslik"])
    icerik += f'''
<p style="margin: 0 0 16px 0;">{s["selam"]}</p>
<p style="margin: 0 0 20px 0;">{s["metin"]}</p>

<p style="margin: 0 0 12px 0;">{s["ozellik"]}</p>
<table cellpadding="0" cellspacing="0" style="margin: 0 0 20px 0;">
<tr><td style="padding: 6px 0; color: #d4d4d4;">{s["adim1"]}</td></tr>
<tr><td style="padding: 6px 0; color: #d4d4d4;">{s["adim2"]}</td></tr>
<tr><td style="padding: 6px 0; color: #d4d4d4;">{s["adim3"]}</td></tr>
</table>
'''
    icerik += _buton(s["buton"], "https://wandering-scene-8c0a.a-tamerdebreli.workers.dev/")
    icerik += _bilgi_kutusu(s["kutu"], "info")
    icerik += _footer(dil)

    return icerik


# ============================================================
# 2) SIFRE SIFIRLAMA EMAILI
# ============================================================
def sifre_sifirla_email(kullanici_adi, sifirlama_linki, dil="tr"):
    S = {
        "tr": {
            "baslik": "Şifre Sıfırlama Talebi",
            "selam": f"Merhaba <strong>{kullanici_adi}</strong>,",
            "metin": "Veraxio hesabınız için şifre sıfırlama talebinde bulundunuz. Aşağıdaki butona tıklayarak yeni şifrenizi belirleyebilirsiniz.",
            "buton": "Şifreyi Sıfırla",
            "sure": "Bu link <strong>24 saat</strong> geçerlidir.",
            "guvenlik": "🔒 <strong>Güvenlik:</strong> Eğer bu talebi siz yapmadıysanız, bu e-postayı görmezden gelebilirsiniz. Şifreniz değişmeyecektir.",
        },
        "en": {
            "baslik": "Password Reset Request",
            "selam": f"Hello <strong>{kullanici_adi}</strong>,",
            "metin": "You requested a password reset for your Veraxio account. Click the button below to set a new password.",
            "buton": "Reset Password",
            "sure": "This link is valid for <strong>24 hours</strong>.",
            "guvenlik": "🔒 <strong>Security:</strong> If you didn't request this, you can safely ignore this email. Your password will not change.",
        },
        "bg": {
            "baslik": "Заявка за нулиране на парола",
            "selam": f"Здравейте <strong>{kullanici_adi}</strong>,",
            "metin": "Заявихте нулиране на паролата за вашия Veraxio акаунт. Щракнете върху бутона по-долу, за да зададете нова парола.",
            "buton": "Нулирай паролата",
            "sure": "Тази връзка е валидна <strong>24 часа</strong>.",
            "guvenlik": "🔒 <strong>Сигурност:</strong> Ако не сте направили тази заявка, можете да игнорирате този имейл. Паролата ви няма да се промени.",
        },
        "ro": {
            "baslik": "Cerere de resetare a parolei",
            "selam": f"Buna <strong>{kullanici_adi}</strong>,",
            "metin": "Ati solicitat resetarea parolei pentru contul dvs. Veraxio. Faceti clic pe butonul de mai jos pentru a seta o parola noua.",
            "buton": "Reseteaza parola",
            "sure": "Acest link este valabil <strong>24 de ore</strong>.",
            "guvenlik": "🔒 <strong>Securitate:</strong> Daca nu ati solicitat acest lucru, puteti ignora acest email. Parola dvs. nu se va schimba.",
        },
        "hr": {
            "baslik": "Zahtjev za ponistavanje lozinke",
            "selam": f"Pozdrav <strong>{kullanici_adi}</strong>,",
            "metin": "Zatrazili ste ponistavanje lozinke za vas Veraxio racun. Kliknite gumb ispod za postavljanje nove lozinke.",
            "buton": "Ponisti lozinku",
            "sure": "Ova poveznica vrijedi <strong>24 sata</strong>.",
            "guvenlik": "🔒 <strong>Sigurnost:</strong> Ako niste zatrazili ovo, mozete zanemariti ovaj email. Vasa lozinka nece biti promijenjena.",
        },
    }
    s = S.get(dil, S["tr"])

    icerik = _header(s["baslik"])
    icerik += f'''
<p style="margin: 0 0 16px 0;">{s["selam"]}</p>
<p style="margin: 0 0 20px 0;">{s["metin"]}</p>
'''
    icerik += _buton(s["buton"], sifirlama_linki)
    icerik += f'<p style="margin: 12px 0; color: #a3a3a3; font-size: 14px;">{s["sure"]}</p>'
    icerik += _bilgi_kutusu(s["guvenlik"], "warning")
    icerik += _footer(dil)

    return icerik


# ============================================================
# 3) DENETIM RAPORU EMAILI
# ============================================================
def denetim_rapor_email(musteri, ai_tipi, durum, rapor_no, dil="tr"):
    DURUM_RENK = {
        "UYUMLU": "#22c55e",
        "UYUMSUZ": "#ef4444",
    }
    renk = DURUM_RENK.get(durum, "#f59e0b")

    S = {
        "tr": {
            "baslik": "Denetim Sonucu",
            "selam": f"Merhaba <strong>{musteri}</strong>,",
            "metin": f"AI Act Madde 50 kapsamında otomatik denetiminiz tamamlandı.",
            "ai_tipi": "AI Tipi",
            "sonuc": "Sonuç",
            "rapor_no": "Rapor No",
            "kutu": "💡 Raporunuzun tam PDF çıktısını Veraxio panelinden indirebilirsiniz.",
        },
        "en": {
            "baslik": "Audit Result",
            "selam": f"Hello <strong>{musteri}</strong>,",
            "metin": f"Your automatic audit under AI Act Article 50 is complete.",
            "ai_tipi": "AI Type",
            "sonuc": "Result",
            "rapor_no": "Report No",
            "kutu": "💡 Download the full PDF output from the Veraxio panel.",
        },
        "bg": {
            "baslik": "Резултат от одита",
            "selam": f"Здравейте <strong>{musteri}</strong>,",
            "metin": "Вашият автоматичен одит по член 50 от AI Act е завършен.",
            "ai_tipi": "Тип AI",
            "sonuc": "Резултат",
            "rapor_no": "No доклад",
            "kutu": "💡 Изтеглете пълния PDF от панела Veraxio.",
        },
        "ro": {
            "baslik": "Rezultatul auditului",
            "selam": f"Buna <strong>{musteri}</strong>,",
            "metin": "Auditul dvs. automat in temeiul articolului 50 din AI Act este complet.",
            "ai_tipi": "Tip AI",
            "sonuc": "Rezultat",
            "rapor_no": "Nr. raport",
            "kutu": "💡 Descarcati PDF-ul complet din panoul Veraxio.",
        },
        "hr": {
            "baslik": "Rezultat revizije",
            "selam": f"Pozdrav <strong>{musteri}</strong>,",
            "metin": "Vasa automatska revizija prema clanku 50 AI Act je zavrsena.",
            "ai_tipi": "Tip AI",
            "sonuc": "Rezultat",
            "rapor_no": "Br. izvjesca",
            "kutu": "💡 Preuzmite potpuni PDF iz Veraxio panela.",
        },
    }
    s = S.get(dil, S["tr"])

    icerik = _header(s["baslik"])
    icerik += f'''
<p style="margin: 0 0 16px 0;">{s["selam"]}</p>
<p style="margin: 0 0 20px 0;">{s["metin"]}</p>

<table cellpadding="0" cellspacing="0" style="margin: 0 0 20px 0; width: 100%;">
<tr>
<td style="padding: 10px 0; color: #737373; font-size: 13px; width: 130px;">{s["ai_tipi"]}:</td>
<td style="padding: 10px 0; color: #fafafa; font-size: 14px;">{ai_tipi}</td>
</tr>
<tr>
<td style="padding: 10px 0; color: #737373; font-size: 13px;">{s["sonuc"]}:</td>
<td style="padding: 10px 0; color: {renk}; font-size: 18px; font-weight: 700;">{durum}</td>
</tr>
<tr>
<td style="padding: 10px 0; color: #737373; font-size: 13px;">{s["rapor_no"]}:</td>
<td style="padding: 10px 0; color: #60a5fa; font-family: monospace; font-size: 13px;">{rapor_no}</td>
</tr>
</table>
'''
    icerik += _bilgi_kutusu(s["kutu"], "info")
    icerik += _footer(dil)

    return icerik


# ============================================================
# 4) DEMO TALEBI EMAILI (Formspree icin degil, kendi mailimiz icin)
# ============================================================
def demo_talebi_email(veri, dil="tr"):
    S = {
        "tr": {
            "baslik": "🎯 Yeni Demo Talebi",
            "metin": "Landing sayfasından yeni bir demo talebi geldi.",
            "ad": "Ad Soyad",
            "eposta": "E-posta",
            "sirket": "Şirket",
            "telefon": "Telefon",
            "mesaj": "Mesaj",
            "kutu": "⚡ Bu talebi <strong>24 saat içinde</strong> yanıtlayın.",
        },
        "en": {
            "baslik": "🎯 New Demo Request",
            "metin": "A new demo request came from the landing page.",
            "ad": "Full Name",
            "eposta": "Email",
            "sirket": "Company",
            "telefon": "Phone",
            "mesaj": "Message",
            "kutu": "⚡ Respond to this request within <strong>24 hours</strong>.",
        },
    }
    s = S.get(dil, S["tr"])

    icerik = _header(s["baslik"])
    icerik += f'<p style="margin: 0 0 20px 0;">{s["metin"]}</p>'
    icerik += f'''
<table cellpadding="0" cellspacing="0" style="margin: 0 0 20px 0; width: 100%;">
<tr><td style="padding: 8px 0; color: #737373; font-size: 13px; width: 130px;">{s["ad"]}:</td><td style="padding: 8px 0; color: #fafafa;">{veri.get("ad", "-")}</td></tr>
<tr><td style="padding: 8px 0; color: #737373; font-size: 13px;">{s["eposta"]}:</td><td style="padding: 8px 0; color: #60a5fa;">{veri.get("email", "-")}</td></tr>
<tr><td style="padding: 8px 0; color: #737373; font-size: 13px;">{s["sirket"]}:</td><td style="padding: 8px 0; color: #fafafa;">{veri.get("sirket", "-")}</td></tr>
<tr><td style="padding: 8px 0; color: #737373; font-size: 13px;">{s["telefon"]}:</td><td style="padding: 8px 0; color: #fafafa;">{veri.get("telefon", "-")}</td></tr>
</table>
'''
    if veri.get("mesaj"):
        icerik += f'<p style="margin: 0 0 6px 0; color: #737373; font-size: 13px;">{s["mesaj"]}:</p>'
        icerik += f'<div style="background: #0f0f0f; padding: 14px 18px; border-radius: 8px; color: #d4d4d4; font-size: 14px; line-height: 1.6; margin-bottom: 20px;">{veri["mesaj"]}</div>'

    icerik += _bilgi_kutusu(s["kutu"], "success")
    icerik += _footer(dil)

    return icerik