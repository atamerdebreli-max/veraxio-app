"""
Toplu Denetim Modulu
CSV'den birden fazla musteriyi okuyup toplu denetim yapar.
"""
from utils import tr_to_ascii
import io
import json
import uuid
import csv as _csv
from datetime import datetime
from fpdf import FPDF




# CSV SABLONU
CSV_SABLONU = """musteri,sektor,ai_tipi,chatbot_mesaji,ai_uretim,gercekci,etiket,sanatsal
Ornek Musteri A.S.,Fintech,Chatbot / AI Asistan,"Merhaba! Size nasil yardimci olabilirim?",,,,
Ornek Musteri B.S.,SaaS,Chatbot / AI Asistan,"Ben bir yapay zeka asistaniyim.",,,,
Ornek Medya A.S.,Medya,Deepfake Icerik,,evet,evet,hayir,hayir
Ornek Sanat A.S.,Medya,Deepfake Icerik,,evet,evet,evet,evet
Ornek Haber A.S.,Medya,Kamu Yarari Metni,,evet,,evet,
"""


def csv_sablonu_indir():
    """CSV sablonunu bytes olarak dondurur."""
    return CSV_SABLONU.encode("utf-8-sig")


# None_FIX - None degerler icin guvenli erisim
def csv_isle(icerik_bytes, ai_bildirimi_var_mi, c2pa_kontrol, deepfake_kontrol, kamu_metni_kontrol, duygu_tanima_kontrol):
    """
    CSV icerigini alir, her satiri denetler, sonuclari listeler.
    """
    metin = icerik_bytes.decode("utf-8-sig")
    reader = _csv.DictReader(io.StringIO(metin))
    sonuclar = []

    for i, satir in enumerate(reader, start=1):
        musteri = (satir.get("musteri") or "").strip()
        sektor = (satir.get("sektor") or "").strip()
        ai_tipi = (satir.get("ai_tipi") or "").strip()
        chatbot_mesaji = (satir.get("chatbot_mesaji") or "").strip()
        ai_uretim = (satir.get("ai_uretim") or "").strip().lower() in ["evet", "var", "yes", "true", "1"]
        gercekci = (satir.get("gercekci") or "").strip().lower() in ["evet", "var", "yes", "true", "1"]
        etiket = (satir.get("etiket") or "").strip().lower() in ["evet", "var", "yes", "true", "1"]
        sanatsal = (satir.get("sanatsal") or "").strip().lower() in ["evet", "var", "yes", "true", "1"]

        if not musteri:
            continue

        sonuc = {
            "no": i,
            "musteri": musteri,
            "sektor": sektor,
            "ai_tipi": ai_tipi,
            "sonuc": "DENETLENMEDI",
            "detay": "",
        }

        try:
            if ai_tipi == "Chatbot / AI Asistan":
                if not chatbot_mesaji:
                    sonuc["sonuc"] = "HATA"
                    sonuc["detay"] = "Chatbot mesaji bos"
                else:
                    bildirim = ai_bildirimi_var_mi(chatbot_mesaji)
                    sonuc["sonuc"] = "UYUMLU" if bildirim else "UYUMSUZ"
                    sonuc["detay"] = "AI bildirimi VAR" if bildirim else "AI bildirimi YOK"

            elif ai_tipi == "Deepfake Icerik":
                df = deepfake_kontrol(ai_uretim, gercekci, etiket, sanatsal)
                sonuc["sonuc"] = df["durum"]
                sonuc["detay"] = "; ".join(df["bulgular"][:2])

            elif ai_tipi == "Kamu Yarari Metni":
                km = kamu_metni_kontrol(ai_uretim, True, etiket, etiket, etiket)
                sonuc["sonuc"] = km["durum"]
                sonuc["detay"] = "; ".join(km["bulgular"][:2])

            else:
                sonuc["sonuc"] = "ATLANDI"
                sonuc["detay"] = f"Desteklenmeyen AI tipi: {ai_tipi}"

        except Exception as e:
            sonuc["sonuc"] = "HATA"
            sonuc["detay"] = str(e)[:80]

        sonuclar.append(sonuc)

    return sonuclar


def ozet_istatistik(sonuclar):
    """Sonuclardan ozet istatistik cikarir."""
    toplam = len(sonuclar)
    uyumlu = sum(1 for s in sonuclar if s["sonuc"] == "UYUMLU")
    uyumsuz = sum(1 for s in sonuclar if s["sonuc"] == "UYUMSUZ")
    hata = sum(1 for s in sonuclar if s["sonuc"] in ["HATA", "ATLANDI", "DENETLENMEDI"])
    return {
        "toplam": toplam,
        "uyumlu": uyumlu,
        "uyumsuz": uyumsuz,
        "hata": hata,
        "uyum_orani": round(100 * uyumlu / toplam, 1) if toplam else 0,
    }


def toplu_json_olustur(sonuclar, istatistik, denetci_adi, rapor_no):
    """Toplu denetim sonuclarindan detayli JSON olusturur."""
    return {
        "rapor_no": rapor_no,
        "tarih": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "denetci": denetci_adi,
        "kapsam": "AB AI Act Madde 50 (Toplu Denetim)",
        "istatistik": istatistik,
        "sonuclar": sonuclar,
    }


def toplu_csv_olustur(sonuclar):
    """Toplu denetim sonuclarindan CSV olusturur."""
    buf = io.StringIO()
    if not sonuclar:
        return buf.getvalue().encode("utf-8-sig")
    fieldnames = list(sonuclar[0].keys())
    w = _csv.DictWriter(buf, fieldnames=fieldnames)
    w.writeheader()
    for s in sonuclar:
        w.writerow(s)
    return buf.getvalue().encode("utf-8-sig")


class TopluRaporPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, "TOPLU AI UYUMLULUK DENETIM RAPORU", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(3)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, "Sayfa " + str(self.page_no()), align="C")


def toplu_rapor_pdf_olustur(sonuclar, denetci_adi, istatistik):
    """Toplu denetim sonuclarindan PDF rapor uretir."""
    rapor_no = "AIACT-TOPLU-" + datetime.now().strftime("%Y%m%d") + "-" + str(uuid.uuid4())[:6].upper()

    pdf = TopluRaporPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "Rapor No: " + rapor_no, new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, "Tarih: " + datetime.now().strftime("%Y-%m-%d %H:%M"), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, "Denetci: " + tr_to_ascii(denetci_adi), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, "Kapsam: AB AI Act Madde 50 (Toplu Denetim)", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "OZET ISTATISTIK", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=11)
    pdf.cell(0, 7, "  Toplam Denetim: " + str(istatistik["toplam"]), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "  Uyumlu: " + str(istatistik["uyumlu"]), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "  Uyumsuz: " + str(istatistik["uyumsuz"]), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "  Hata/Atlanan: " + str(istatistik["hata"]), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "  Uyum Orani: %" + str(istatistik["uyum_orani"]), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "DETAYLI SONUCLAR", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    for s in sonuclar:
        pdf.set_font("Helvetica", "B", 10)
        baslik = f"{s['no']}. {tr_to_ascii(s['musteri'])} ({tr_to_ascii(s['ai_tipi'])})"
        pdf.cell(0, 7, baslik, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", size=10)
        if s["sonuc"] == "UYUMLU":
            pdf.set_text_color(0, 150, 0)
        elif s["sonuc"] == "UYUMSUZ":
            pdf.set_text_color(200, 0, 0)
        else:
            pdf.set_text_color(150, 100, 0)
        pdf.cell(0, 6, "   Sonuc: " + tr_to_ascii(s["sonuc"]), new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)
        if s["detay"]:
            pdf.cell(0, 6, "   Detay: " + tr_to_ascii(s["detay"])[:90], new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

    return pdf, rapor_no