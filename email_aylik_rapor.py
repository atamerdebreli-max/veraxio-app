"""email_sender.py'ye aylik rapor sablonu ekle"""

with open("email_sender.py", encoding="utf-8") as f:
    c = f.read()

# Fonksiyonlari dosyanin sonuna ekle
yeni_fonksiyonlar = '''

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
        tip_metni = "\\n"
        for tip in istatistik["tip_dagilimi"][:5]:
            tip_metni += f"  - {tip['ai_tipi']}: {tip['n']} denetim\\n"

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
'''

if "aylik_ozet_emaili_gonder" not in c:
    c = c.rstrip() + yeni_fonksiyonlar
    print("BASARILI: Aylik ozet emaili fonksiyonu eklendi.")
else:
    print("UYARI: Fonksiyon zaten var.")

with open("email_sender.py", "w", encoding="utf-8") as f:
    f.write(c)

print("email_sender.py kaydedildi.")