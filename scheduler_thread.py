"""
scheduler_thread.py - Streamlit arka plan zamanlayici
Streamlit acikken, belirli araliklarla bekleyen denetimleri calistirir.
"""

import threading
import time
from datetime import datetime

# Global kontrol
_baslatildi = False
_durdur = False
_thread = None


def _gunluk_yedek_kontrol():
    """
    Gunluk DB yedegi alir.
    Her gun 03:00 civarinda 1 kez calisir, ayni gun tekrar calismaz.
    """
    import db

    simdi = datetime.now()

    # Sadece 03:00 - 03:15 arasinda tetikle
    if simdi.hour != 3:
        return 0

    # Bugun zaten alinmis mi?
    bugun_baslangic = simdi.strftime("%Y-%m-%d 00:00:00")

    try:
        with db._baglanti() as conn:
            cur = conn.execute("""
                SELECT COUNT(*) as n FROM audit_log
                WHERE eylem = 'db_yedek_alindi'
                AND tarih >= ?
            """, (bugun_baslangic,))
            if cur.fetchone()["n"] > 0:
                return 0  # Bugun zaten alindi
    except Exception:
        pass

    # Yedek al
    try:
        import db_yedek
        yedek = db_yedek.gunluk_yedek()
        if yedek:
            print(f"[Scheduler] DB yedek alindi: {yedek.name}")
            try:
                db.audit_kaydet(
                    eylem="db_yedek_alindi",
                    kullanici_adi="sistem",
                    detay=f"Gunluk yedek: {yedek.name}",
                )
            except Exception:
                pass
            return 1
    except Exception as e:
        print(f"[Scheduler] Yedek hatasi: {str(e)[:100]}")

    return 0


def _aylik_rapor_gonder():
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


def _bekleyenleri_calistir():
    """Bekleyen zamanlanmis denetimleri calistirir."""
    try:
        import db
        db.init_db()

        bekleyenler = db.zamanlanmis_bekleyenler()
        if not bekleyenler:
            return 0

        # zamanlanmis_calistir.py'deki fonksiyonu import et
        from zamanlanmis_calistir import _denetim_calistir
        import uuid

        calistirilan = 0
        for kayit in bekleyenler:
            try:
                sonuc = _denetim_calistir(kayit)
                durum = sonuc.get("durum", "BILINMEYEN")

                if durum != "HATA":
                    rapor_no = (
                        "AIACT-AUTO-"
                        + datetime.now().strftime("%Y%m%d")
                        + "-"
                        + str(uuid.uuid4())[:6].upper()
                    )
                    db.kaydet(
                        rapor_no=rapor_no,
                        modul="Otomatik",
                        musteri=kayit.get("musteri", ""),
                        ai_tipi=kayit.get("ai_tipi", ""),
                        denetci="Otomatik Zamanlayici",
                        genel_sonuc=durum,
                        karar="AUTO",
                        kanit_id=rapor_no,
                        ceza_riski="15 milyon Euro veya cironun %3u" if durum == "UYUMSUZ" else "",
                        json_veri=sonuc,
                    )

                db.zamanlanmis_guncelle_son_calisma(kayit["id"])
                calistirilan += 1

            except Exception as e:
                print(f"[Scheduler] Denetim hatasi (id={kayit.get('id')}): {str(e)[:100]}")

        return calistirilan

    except Exception as e:
        print(f"[Scheduler] Genel hata: {str(e)[:100]}")
        return 0


def _worker(interval_saniye=300):
    """
    Arka plan worker thread'i.
    Her interval_saniye saniyede bir bekleyen denetimleri kontrol eder.
    """
    global _durdur

    print(f"[Scheduler] Baslatildi. Interval: {interval_saniye} saniye")

    # Ilk calistirmada bekleme (Streamlit baslangicta yavas olabilir)
    time.sleep(10)

    while not _durdur:
        try:
            simdi = datetime.now().strftime("%H:%M:%S")
            print(f"[Scheduler] Kontrol: {simdi}")

            sayi = _bekleyenleri_calistir()
            if sayi > 0:
                print(f"[Scheduler] {sayi} denetim calistirildi.")

            # Gunluk DB yedek kontrolu (her gun 03:00)
            yedek_sayi = _gunluk_yedek_kontrol()
            if yedek_sayi > 0:
                print(f"[Scheduler] {yedek_sayi} yedek alindi.")

            # Aylik rapor kontrolu (ayin 1'inde)
            aylik_sayi = _aylik_rapor_gonder()
            if aylik_sayi > 0:
                print(f"[Scheduler] {aylik_sayi} firmaya aylik rapor gonderildi.")

        except Exception as e:
            print(f"[Scheduler] Worker hatasi: {str(e)[:100]}")

        # Interval bekle (kucuk parcalara bol, _durdur kontrolu icin)
        for _ in range(interval_saniye):
            if _durdur:
                break
            time.sleep(1)

    print("[Scheduler] Durduruldu.")


def baslat(interval_saniye=300):
    """
    Scheduler'i baslatir (eger zaten baslatilmamissa).
    Streamlit'in cache_resource'i ile bir kez cagirilir.
    """
    global _baslatildi, _thread, _durdur

    if _baslatildi:
        return False

    _baslatildi = True
    _durdur = False

    _thread = threading.Thread(
        target=_worker,
        args=(interval_saniye,),
        daemon=True,  # Streamlit kapaninca otomatik durur
        name="AIScheduler",
    )
    _thread.start()

    return True


def durdur():
    """Scheduler'i durdurur."""
    global _durdur
    _durdur = True


def durum():
    """Scheduler durumunu dondurur."""
    return {
        "baslatildi": _baslatildi,
        "calisiyor": _thread.is_alive() if _thread else False,
        "thread_adi": _thread.name if _thread else None,
    }