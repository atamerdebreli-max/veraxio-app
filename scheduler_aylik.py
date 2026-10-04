"""scheduler_thread.py'ye aylik rapor tetikleyicisi ekle"""

with open("scheduler_thread.py", encoding="utf-8") as f:
    c = f.read()

# 1. Aylik rapor fonksiyonu ekle (_bekleyenleri_calistir oncesine)
eski = '''def _bekleyenleri_calistir():'''

yeni = '''def _aylik_rapor_gonder():
    """
    Aylik ozet raporlarini gonderir.
    Sadece ayin 1'inde ve daha once gonderilmemisse.
    """
    from datetime import datetime
    import db

    simdi = datetime.now()

    # Sadece ayin 1'inde calisir
    if simdi.day != 1:
        return 0

    # Bu ay zaten gonderildi mi? (audit log kontrolu)
    ay_baslangic = simdi.strftime("%Y-%m-01 00:00:00")

    try:
        with db._baglanti() as conn:
            cur = conn.execute("""
                SELECT COUNT(*) as n FROM audit_log
                WHERE eylem = 'aylik_rapor_gonderildi'
                AND tarih >= ?
            """, (ay_baslangic,))
            if cur.fetchone()["n"] > 0:
                return 0  # Bu ay zaten gonderildi
    except Exception:
        pass

    # Firmalari al
    try:
        firmalar = db.aylik_rapor_gonderilecekler()
    except Exception as e:
        print(f"[AylikRapor] Firma listesi alinamadi: {str(e)[:100]}")
        return 0

    if not firmalar:
        return 0

    from email_sender import aylik_ozet_emaili_gonder

    gonderilen = 0
    for firma in firmalar:
        try:
            istatistik = db.aylik_istatistik(firma_id=firma["id"])
            if istatistik["toplam"] == 0:
                continue  # Denetimi olmayan firmaya gonderme

            # Firmaya ozel dil (varsa)
            dil = "tr"

            sonuc = aylik_ozet_emaili_gonder(
                alici=firma["eposta"],
                firma_adi=firma["firma_adi"],
                istatistik=istatistik,
                dil=dil,
            )

            if sonuc.get("durum") == "OK":
                gonderilen += 1
                print(f"[AylikRapor] Gonderildi: {firma['firma_adi']} -> {firma['eposta']}")

        except Exception as e:
            print(f"[AylikRapor] Hata ({firma.get('firma_adi')}): {str(e)[:100]}")

    # Audit log
    if gonderilen > 0:
        try:
            db.audit_kaydet(
                eylem="aylik_rapor_gonderildi",
                kullanici_adi="sistem",
                detay=f"{gonderilen} firmaya aylik rapor gonderildi",
            )
        except Exception:
            pass

    return gonderilen


def _bekleyenleri_calistir():'''

if eski in c:
    c = c.replace(eski, yeni, 1)
    print("1) Aylik rapor fonksiyonu eklendi.")
else:
    print("1) UYARI: _bekleyenleri_calistir marker bulunamadi.")

# 2. Worker dongusune aylik rapor cagrisi ekle
eski2 = '''            sayi = _bekleyenleri_calistir()
            if sayi > 0:
                print(f"[Scheduler] {sayi} denetim calistirildi.")'''

yeni2 = '''            sayi = _bekleyenleri_calistir()
            if sayi > 0:
                print(f"[Scheduler] {sayi} denetim calistirildi.")

            # Aylik rapor kontrolu (ayin 1'inde)
            aylik_sayi = _aylik_rapor_gonder()
            if aylik_sayi > 0:
                print(f"[Scheduler] {aylik_sayi} firmaya aylik rapor gonderildi.")'''

if eski2 in c:
    c = c.replace(eski2, yeni2, 1)
    print("2) Worker dongusune aylik rapor eklendi.")
else:
    print("2) UYARI: worker dongusu bulunamadi.")

with open("scheduler_thread.py", "w", encoding="utf-8") as f:
    f.write(c)

print("scheduler_thread.py kaydedildi.")