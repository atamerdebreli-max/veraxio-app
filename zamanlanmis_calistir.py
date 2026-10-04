"""
zamanlanmis_calistir.py - Bekleyen zamanlanmis denetimleri calistirir.
Windows Task Scheduler veya cron ile periyodik calistirilir.

Kullanim:
    py zamanlanmis_calistir.py
"""

import json
import uuid
import os
import tempfile
from datetime import datetime

import db
from email_sender import email_gonder, email_ayarli_mi, ceviri
from core import (
    ai_bildirimi_var_mi, ai_metin_tespit_kontrol, deepfake_kontrol,
    kamu_metni_kontrol, duygu_tanima_kontrol, kvkk_kontrol,
    ab_temsilcisi_kontrol, shadow_ai_kontrol, kumulatif_kontrol,
    c2pa_kontrol, c2pa_dayaniklilik_testi,
)
from chatbot_scraper import chatbot_url_denetle


def _chatbot_denetle(url, manuel_mesaj=""):
    """Chatbot URL'sini denetler. Manuel mesaj varsa oncelikli kullanir."""
    # Manuel mesaj varsa, dogrudan onu kullan
    if manuel_mesaj:
        bildirim = ai_bildirimi_var_mi(manuel_mesaj)
        return {
            "durum": "UYUMLU" if bildirim else "UYUMSUZ",
            "ai_bildirimi": bildirim,
            "kaynak": "manuel_mesaj",
            "mesaj": manuel_mesaj[:200],
        }

    # URL'den cekmeyi dene
    sonuc = chatbot_url_denetle(url)
    if sonuc["durum"] != "OK":
        return {"durum": "HATA", "mesaj": sonuc.get("hata", "Chatbot bulunamadi")}
    mesaj = sonuc.get("chatbot_mesaji", "")
    if not mesaj or mesaj.startswith("("):
        return {"durum": "HATA", "mesaj": "Chatbot mesaji cikarilamadi. Manuel mesaj girin."}
    bildirim = ai_bildirimi_var_mi(mesaj)
    return {
        "durum": "UYUMLU" if bildirim else "UYUMSUZ",
        "ai_bildirimi": bildirim,
        "kaynak": "url",
        "mesaj": mesaj[:200],
    }


def _gorsel_denetle(url):
    """Gorsel URL'sini denetler."""
    from image_downloader import gorsel_url_indir, gecici_dosya_sil
    indir = gorsel_url_indir(url)
    if indir["durum"] != "OK":
        return {"durum": "HATA", "mesaj": indir.get("hata", "Gorsel indirilemedi")}
    try:
        c2pa = c2pa_kontrol(indir["dosya_yolu"])
        dayaniklilik = c2pa_dayaniklilik_testi(indir["dosya_yolu"])
        return {
            "durum": "UYUMLU" if c2pa.get("durum") == "ISARETLI" else "UYUMSUZ",
            "c2pa": c2pa,
            "dayaniklilik": dayaniklilik,
        }
    finally:
        gecici_dosya_sil(indir["dosya_yolu"])


def _metin_denetle(metin):
    """Metni denetler."""
    sonuc = ai_metin_tespit_kontrol(metin)
    return {
        "durum": "UYUMSUZ" if sonuc.get("durum") == "AI" else "UYUMLU",
        "metin_sonuc": sonuc,
    }


def _denetim_calistir(kayit):
    """Bir zamanlanmis denetimi calistirir."""
    ai_tipi = kayit.get("ai_tipi", "")
    url = kayit.get("url", "") or ""

    try:
        ek = json.loads(kayit.get("ek_bilgi") or "{}")
    except Exception:
        ek = {}

    if ai_tipi == "Chatbot / AI Asistan":
        return _chatbot_denetle(url, ek.get("chatbot_mesaji", ""))
    elif ai_tipi == "Gorsel Uretimi (C2PA)":
        return _gorsel_denetle(url)
    elif ai_tipi == "Metin Denetimi (AI Tespiti)":
        return _metin_denetle(ek.get("metin", ""))
    elif ai_tipi == "Deepfake Icerik":
        return {"durum": "UYUMSUZ", "not": "Manuel denetim gerekli"}
    elif ai_tipi == "Kamu Yarari Metni":
        return {"durum": "UYUMSUZ", "not": "Manuel denetim gerekli"}
    elif ai_tipi == "KVKK Uyum Denetimi":
        return {"durum": "UYUMSUZ", "not": "Manuel denetim gerekli"}
    else:
        return {"durum": "BILINMEYEN", "mesaj": f"Desteklenmeyen tip: {ai_tipi}"}


def _ascii_cevir(text):
    """Turkce karakterleri ASCII'ye cevirir."""
    if text is None:
        return ""
    cevir = {
        "ş": "s", "Ş": "S",
        "ı": "i", "İ": "I",
        "ğ": "g", "Ğ": "G",
        "ü": "u", "Ü": "U",
        "ö": "o", "Ö": "O",
        "ç": "c", "Ç": "C",
        "â": "a", "Â": "A",
        "î": "i", "Î": "I",
        "û": "u", "Û": "U",
    }
    text = str(text)
    for tr, a in cevir.items():
        text = text.replace(tr, a)
    return text


def _basit_pdf_olustur(musteri, ai_tipi, durum, sonuc, dil="tr"):
    """Basit bir PDF rapor olusturur (gecici dosya, dil destekli)."""
    try:
        from fpdf import FPDF

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, _ascii_cevir(ceviri(dil, "pdf_baslik")), align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)

        pdf.set_font("Helvetica", size=11)
        pdf.cell(0, 7, _ascii_cevir(ceviri(dil, "pdf_musteri")) + ": " + _ascii_cevir(musteri)[:50], new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 7, _ascii_cevir(ceviri(dil, "pdf_ai_tipi")) + ": " + _ascii_cevir(ai_tipi)[:50], new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 7, _ascii_cevir(ceviri(dil, "pdf_tarih")) + ": " + datetime.now().strftime("%Y-%m-%d %H:%M"), new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 7, _ascii_cevir(ceviri(dil, "pdf_modul")) + ": Scheduled Audit", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)

        pdf.set_font("Helvetica", "B", 13)
        if durum == "UYUMSUZ":
            pdf.set_text_color(200, 0, 0)
        elif durum == "UYUMLU":
            pdf.set_text_color(0, 150, 0)
        pdf.cell(0, 9, _ascii_cevir(ceviri(dil, "pdf_sonuc")) + ": " + _ascii_cevir(durum), new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)

        pdf.ln(3)
        pdf.set_font("Helvetica", size=10)
        for k, v in (sonuc or {}).items():
            if k in ["durum", "bulgular", "oneri"]:
                continue
            metin = _ascii_cevir(f"  {k}: {str(v)[:70]}")
            pdf.cell(0, 6, metin, new_x="LMARGIN", new_y="NEXT")

        if sonuc.get("mesaj"):
            pdf.ln(2)
            pdf.set_font("Helvetica", "I", 9)
            pdf.cell(0, 6, "Message: " + _ascii_cevir(str(sonuc["mesaj"])[:80]), new_x="LMARGIN", new_y="NEXT")

        # Gecici dosya
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        pdf.output(tmp.name)
        return tmp.name
    except Exception as e:
        print(f"    PDF olusturma hatasi: {str(e)[:80]}")
        return None


def _email_gonder(musteri, eposta, ai_tipi, durum, sonuc, dil="tr"):
    """Denetim sonucunu e-posta ile gonderir (coklu dil destekli)."""
    if not eposta:
        return False

    if not email_ayarli_mi():
        print("    E-posta ayarlari yapilmamis, atlaniyor.")
        return False

    try:
        # PDF olustur (dil destekli)
        pdf_yolu = _basit_pdf_olustur(musteri, ai_tipi, durum, sonuc, dil)

        konu = ceviri(dil, "konu", musteri)
        icerik = (
            ceviri(dil, "selamlama", musteri) + "\n\n"
            + ceviri(dil, "aciklama") + "\n\n"
            + ceviri(dil, "denetim_tipi") + ": " + str(ai_tipi) + "\n"
            + ceviri(dil, "sonuc") + ": " + str(durum) + "\n"
            + ceviri(dil, "tarih") + ": " + datetime.now().strftime('%Y-%m-%d %H:%M') + "\n\n"
            + ceviri(dil, "rapor_eki") + "\n\n"
            + ceviri(dil, "kapanis") + "\n"
            + ceviri(dil, "imza")
        )

        sonuc_email = email_gonder(
            alici=eposta,
            konu=konu,
            icerik=icerik,
            pdf_yolu=pdf_yolu,
        )

        # Gecici PDF'i sil
        if pdf_yolu and os.path.exists(pdf_yolu):
            try:
                os.unlink(pdf_yolu)
            except Exception:
                pass

        return sonuc_email.get("durum") == "OK"
    except Exception as e:
        print(f"    E-posta hatasi: {str(e)[:80]}")
        return False


def main():
    """Bekleyen tum denetimleri calistirir."""
    import sys
    force = "--force" in sys.argv
    
    db.init_db()
    if force:
        bekleyenler = db.zamanlanmis_listele(aktif_only=True)
        print("!!! FORCE MODE: Tum aktif denetimler calistirilacak !!!")
    else:
        bekleyenler = db.zamanlanmis_bekleyenler()

    print(f"=== ZAMANLANMIS DENETIM CALISTIRICI ===")
    print(f"Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Bekleyen denetim: {len(bekleyenler)}")
    print()

    basarili = 0
    basarisiz = 0

    for kayit in bekleyenler:
        kid = kayit["id"]
        musteri = kayit["musteri"]
        ai_tipi = kayit["ai_tipi"]

        print(f"[{kid}] {musteri} - {ai_tipi}")

        try:
            sonuc = _denetim_calistir(kayit)
            durum = sonuc.get("durum", "BILINMEYEN")
            mesaj = sonuc.get("mesaj", "")
            if mesaj:
                print(f"    Sonuc: {durum} ({mesaj[:80]})")
            else:
                print(f"    Sonuc: {durum}")

            # Veritabanina kaydet (sadece HATA olmayan durumlarda)
            if durum != "HATA":
                rapor_no = "AIACT-SCH-" + datetime.now().strftime("%Y%m%d") + "-" + str(uuid.uuid4())[:6].upper()
                db.kaydet(
                    rapor_no=rapor_no,
                    modul="Zamanlanmis",
                    musteri=musteri,
                    ai_tipi=ai_tipi,
                    denetci="Otomatik",
                    genel_sonuc=durum,
                    karar="AUTO",
                    kanit_id=rapor_no,
                    ceza_riski="15 milyon Euro veya cironun %3u" if durum == "UYUMSUZ" else "",
                    json_veri=sonuc,
                )

            # E-posta gonder (eger eposta varsa ve durum HATA degilse)
            if durum != "HATA":
                eposta = kayit.get("eposta", "")
                kayit_dil = kayit.get("dil", "tr") or "tr"
                if eposta:
                    email_ok = _email_gonder(musteri, eposta, ai_tipi, durum, sonuc, kayit_dil)
                    if email_ok:
                        print(f"    E-posta gonderildi: {eposta}")
                    else:
                        print(f"    E-posta gonderilemedi: {eposta}")

            # Sonraki calismayi guncelle
            db.zamanlanmis_guncelle_son_calisma(kid)
            if durum == "HATA":
                basarisiz += 1
            else:
                basarili += 1

        except Exception as e:
            print(f"    HATA: {str(e)[:100]}")
            basarisiz += 1

        print()

    print(f"=== SONUC ===")
    print(f"Basarili: {basarili}")
    print(f"Basarisiz: {basarisiz}")
    print(f"Toplam: {len(bekleyenler)}")


if __name__ == "__main__":
    main()