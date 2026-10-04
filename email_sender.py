"""
email_sender.py - Gmail SMTP ile PDF rapor gonderimi
"""
import os
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from pathlib import Path
from dotenv import load_dotenv

# .env dosyasini yukle (varsa)
load_dotenv(Path(__file__).parent / ".env")


SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")


def _ceviri_yukle(dil="tr"):
    """Dile gore e-posta cevirilerini yukler."""
    try:
        dosya = os.path.join(os.path.dirname(os.path.abspath(__file__)), "locales", f"{dil}.json")
        if not os.path.exists(dosya):
            dosya = os.path.join(os.path.dirname(os.path.abspath(__file__)), "locales", "tr.json")
        with open(dosya, encoding="utf-8") as f:
            data = json.load(f)
        return data.get("email", {})
    except Exception:
        return {}


def ceviri(dil, anahtar, *args):
    """Ceviri anahtarini dondurur ve format uygular."""
    ceviriler = _ceviri_yukle(dil)
    metin = ceviriler.get(anahtar, anahtar)
    if args:
        try:
            return metin.format(*args)
        except Exception:
            return metin
    return metin


def email_ayarli_mi():
    """SMTP ayarlarinin yapilip yapilmadigini kontrol eder."""
    return bool(SMTP_USER and SMTP_PASS)


def email_gonder(alici, konu, icerik, pdf_yolu=None):
    """Gmail SMTP ile e-posta gonderir."""
    if not email_ayarli_mi():
        return {
            "durum": "HATA",
            "hata": "SMTP ayarlari eksik. SMTP_USER ve SMTP_PASS ayarlayin.",
        }

    if not alici or "@" not in alici:
        return {"durum": "HATA", "hata": "Gecersiz alici e-posta adresi."}

    try:
        msg = MIMEMultipart()
        msg["From"] = SMTP_USER
        msg["To"] = alici
        msg["Subject"] = konu

        msg.attach(MIMEText(icerik, "plain", "utf-8"))

        if pdf_yolu and Path(pdf_yolu).exists():
            with open(pdf_yolu, "rb") as f:
                pdf_data = f.read()
            pdf_ek = MIMEApplication(pdf_data, _subtype="pdf")
            pdf_ek.add_header(
                "Content-Disposition",
                "attachment",
                filename=Path(pdf_yolu).name,
            )
            msg.attach(pdf_ek)

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)

        return {"durum": "OK"}

    except smtplib.SMTPAuthenticationError:
        return {
            "durum": "HATA",
            "hata": "SMTP kimlik dogrulama hatasi. Uygulama sifresini kontrol edin.",
        }
    except smtplib.SMTPException as e:
        return {"durum": "HATA", "hata": f"SMTP hatasi: {str(e)[:100]}"}
    except Exception as e:
        return {"durum": "HATA", "hata": f"Beklenmeyen hata: {str(e)[:100]}"}


def deneme_emaili_gonder(alici):
    """Test e-postasi gonderir."""
    return email_gonder(
        alici=alici,
        konu="AI Uyumluluk Kutusu - Test E-postasi",
        icerik=(
            "Merhaba,\n\n"
            "Bu bir test e-postasidir. AI Uyumluluk Kutusu "
            "otomatik rapor gonderim sistemi calisiyor.\n\n"
            "Saygilarimizla,\n"
            "AI Uyumluluk Kutusu"
        ),
        pdf_yolu=None,
    )

# ============================================================
# SIFRE SIFIRLAMA VE DOGRULAMA E-POSTALARI
# ============================================================
def sifre_sifirlama_emaili_gonder(alici, kullanici_adi, token, dil="tr"):
    """Sifre sifirlama e-postasi gonderir."""
    # URL
    url = f"http://localhost:8501/?sifre_sifirla={token}"

    mesajlar = {
        "tr": {
            "konu": "AI Uyumluluk Kutusu - Sifre Sifirlama",
            "icerik": f"""Merhaba {kullanici_adi},

Sifrenizi sifirlamak icin asagidaki linke tiklayin:

{url}

Bu link 24 saat gecerlidir.

Eger bu talebi siz yapmadiysaniz, bu e-postayi dikkate almayin.

Saygilarimizla,
AI Uyumluluk Kutusu
"""
        },
        "en": {
            "konu": "AI Compliance Box - Password Reset",
            "icerik": f"""Hello {kullanici_adi},

Click the link below to reset your password:

{url}

This link is valid for 24 hours.

If you didn't request this, please ignore this email.

Best regards,
AI Compliance Box
"""
        },
        "bg": {
            "konu": "AI Compliance Box - Нулиране на парола",
            "icerik": f"""Здравейте {kullanici_adi},

Кликнете на линка по-долу, за да нулирате паролата си:

{url}

Този линк е валиден 24 часа.

Ако не сте поискали това, игнорирайте имейла.

С уважение,
AI Compliance Box
"""
        },
        "ro": {
            "konu": "AI Compliance Box - Resetare parola",
            "icerik": f"""Buna {kullanici_adi},

Faceți clic pe linkul de mai jos pentru a reseta parola:

{url}

Acest link este valabil 24 de ore.

Dacă nu ați solicitat acest lucru, ignorați acest email.

Cu respect,
AI Compliance Box
"""
        },
        "hr": {
            "konu": "AI Compliance Box - Resetiranje lozinke",
            "icerik": f"""Pozdrav {kullanici_adi},

Kliknite na link ispod za resetiranje lozinke:

{url}

Ovaj link vrijedi 24 sata.

Ako niste zatrazili ovo, ignorirajte ovaj email.

S postovanjem,
AI Compliance Box
"""
        }
    }

    m = mesajlar.get(dil, mesajlar["tr"])

    return email_gonder(
        alici=alici,
        konu=m["konu"],
        icerik=m["icerik"],
        pdf_yolu=None,
    )


def email_dogrulama_gonder(alici, kullanici_adi, token, dil="tr"):
    """Email dogrulama e-postasi gonderir."""
    url = f"http://localhost:8501/?email_dogrula={token}"

    mesajlar = {
        "tr": {
            "konu": "AI Uyumluluk Kutusu - E-posta Dogrulama",
            "icerik": f"""Merhaba {kullanici_adi},

Hesabinizi aktiflestirmek icin asagidaki linke tiklayin:

{url}

Bu link 24 saat gecerlidir.

Saygilarimizla,
AI Uyumluluk Kutusu
"""
        },
        "en": {
            "konu": "AI Compliance Box - Email Verification",
            "icerik": f"""Hello {kullanici_adi},

Click the link below to activate your account:

{url}

This link is valid for 24 hours.

Best regards,
AI Compliance Box
"""
        },
        "bg": {
            "konu": "AI Compliance Box - Потвърждение на имейл",
            "icerik": f"""Здравейте {kullanici_adi},

Кликнете на линка по-долу, за да активирате акаунта си:

{url}

Този линк е валиден 24 часа.

С уважение,
AI Compliance Box
"""
        },
        "ro": {
            "konu": "AI Compliance Box - Verificare email",
            "icerik": f"""Buna {kullanici_adi},

Faceți clic pe linkul de mai jos pentru a vă activa contul:

{url}

Acest link este valabil 24 de ore.

Cu respect,
AI Compliance Box
"""
        },
        "hr": {
            "konu": "AI Compliance Box - Verifikacija emaila",
            "icerik": f"""Pozdrav {kullanici_adi},

Kliknite na link ispod za aktivaciju racuna:

{url}

Ovaj link vrijedi 24 sata.

S postovanjem,
AI Compliance Box
"""
        }
    }

    m = mesajlar.get(dil, mesajlar["tr"])

    return email_gonder(
        alici=alici,
        konu=m["konu"],
        icerik=m["icerik"],
        pdf_yolu=None,
    )

# ============================================================
# AYLIK OZET RAPORU
# ============================================================
def aylik_ozet_emaili_gonder(alici, firma_adi, istatistik, dil="tr"):
    """
    Aylik ozet e-postasi gonderir.

    Args:
        alici: Alici e-posta
        firma_adi: Firma adi
        istatistik: db.aylik_istatistik() cikti
        dil: Dil kodu
    """
    ay_adlari = {
        "tr": ["Ocak", "Subat", "Mart", "Nisan", "Mayis", "Haziran",
               "Temmuz", "Agustos", "Eylul", "Ekim", "Kasim", "Aralik"],
        "en": ["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"],
        "bg": ["Януари", "Февруари", "Март", "Април", "Май", "Юни",
               "Юли", "Август", "Септември", "Октомври", "Ноември", "Декември"],
        "ro": ["Ianuarie", "Februarie", "Martie", "Aprilie", "Mai", "Iunie",
               "Iulie", "August", "Septembrie", "Octombrie", "Noiembrie", "Decembrie"],
        "hr": ["Sijecanj", "Veljaca", "Ozujak", "Travanj", "Svibanj", "Lipanj",
               "Srpanj", "Kolovoz", "Rujan", "Listopad", "Studeni", "Prosinac"],
    }

    ay_adi = ay_adlari.get(dil, ay_adlari["tr"])[istatistik["ay"] - 1]
    yil = istatistik["yil"]

    # Tip dagilimi metni
    tip_metni = ""
    if istatistik.get("tip_dagilimi"):
        tip_metni = "\n"
        for tip in istatistik["tip_dagilimi"][:5]:
            tip_metni += f"  - {tip['ai_tipi']}: {tip['n']} denetim\n"

    # Trend ikonu
    uyum_orani = istatistik["uyum_orani"]
    if uyum_orani >= 80:
        trend = "🟢"
    elif uyum_orani >= 50:
        trend = "🟡"
    else:
        trend = "🔴"

    mesajlar = {
        "tr": {
            "konu": f"AI Uyumluluk Ozeti - {ay_adi} {yil}",
            "icerik": f"""Merhaba {firma_adi},

{ay_adi} {yil} aylik uyumluluk ozetiniz:

📊 AYLIK OZET
  Toplam denetim: {istatistik['toplam']}
  Uyumlu: {istatistik['uyumlu']}
  Uyumsuz: {istatistik['uyumsuz']}
  Uyum orani: {trend} %{uyum_orani}

📋 AI TIPI DAGILIMI{tip_metni}

💡 ONERILER
  - Uyumsuz denetimleri inceleyin
  - Eksikleri duzeltin
  - Bir sonraki ay icin hedef: %100 uyumluluk

Detayli rapor icin panele giris yapin.

Saygilarimizla,
AI Uyumluluk Kutusu
"""
        },
        "en": {
            "konu": f"AI Compliance Summary - {ay_adi} {yil}",
            "icerik": f"""Hello {firma_adi},

Your monthly compliance summary for {ay_adi} {yil}:

📊 MONTHLY SUMMARY
  Total audits: {istatistik['toplam']}
  Compliant: {istatistik['uyumlu']}
  Non-compliant: {istatistik['uyumsuz']}
  Compliance rate: {trend} {uyum_orani}%

📋 AI TYPE DISTRIBUTION{tip_metni}

💡 RECOMMENDATIONS
  - Review non-compliant audits
  - Fix the gaps
  - Target for next month: 100% compliance

Log in to the panel for the detailed report.

Best regards,
AI Compliance Box
"""
        },
        "bg": {
            "konu": f"AI съответствие - {ay_adi} {yil}",
            "icerik": f"""Здравейте {firma_adi},

Месечен отчет за съответствие {ay_adi} {yil}:

📊 МЕСЕЧЕН ОБОБЩЕНИЕ
  Общо одити: {istatistik['toplam']}
  Съвместими: {istatistik['uyumlu']}
  Несъвместими: {istatistik['uyumsuz']}
  Степен: {trend} {uyum_orani}%

📋 РАЗПРЕДЕЛЕНИЕ ПО ТИП{tip_metni}

💡 ПРЕПОРЪКИ
  - Прегледайте несъвместимите одити
  - Отстранете пропуските
  - Цел за следващия месец: 100% съвместимост

Влезте в панела за подробен доклад.

С уважение,
AI Compliance Box
"""
        },
        "ro": {
            "konu": f"Rezumat conformitate AI - {ay_adi} {yil}",
            "icerik": f"""Buna {firma_adi},

Rezumatul lunar de conformitate pentru {ay_adi} {yil}:

📊 REZUMAT LUNAR
  Total audituri: {istatistik['toplam']}
  Conforme: {istatistik['uyumlu']}
  Neconforme: {istatistik['uyumsuz']}
  Rata de conformitate: {trend} {uyum_orani}%

📋 DISTRIBUTIA PE TIPURI{tip_metni}

💡 RECOMANDARI
  - Revizuiti auditurile neconforme
  - Corectati lipsurile
  - Tinta pentru luna urmatoare: 100% conformitate

Conectati-va la panou pentru raportul detaliat.

Cu respect,
AI Compliance Box
"""
        },
        "hr": {
            "konu": f"AI sazetak uskladenosti - {ay_adi} {yil}",
            "icerik": f"""Pozdrav {firma_adi},

Mjesečni sazetak uskladenosti za {ay_adi} {yil}:

📊 MJESECNI SAZETAK
  Ukupno audita: {istatistik['toplam']}
  Uskladeno: {istatistik['uyumlu']}
  Neusklađeno: {istatistik['uyumsuz']}
  Stopa usklađenosti: {trend} {uyum_orani}%

📋 DISTRIBUCIJA PO TIPU{tip_metni}

💡 PREPORUKE
  - Pregledajte neusklađene audite
  - Ispravite nedostatke
  - Cilj za sljedeci mjesec: 100% usklađenost

Prijavite se u panel za detaljno izvjesce.

S postovanjem,
AI Compliance Box
"""
        },
    }

    m = mesajlar.get(dil, mesajlar["tr"])

    return email_gonder(
        alici=alici,
        konu=m["konu"],
        icerik=m["icerik"],
        pdf_yolu=None,
    )
