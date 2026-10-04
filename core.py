"""
Core Modulu - AI Act Madde 50 is mantigi
Streamlit UI'dan bagimsiz, API tarafindan da kullanilabilir.
"""
"""
Tek Denetim sayfasi - AI Act Madde 50 kapsamli denetim
"""
from pathlib import Path
from utils import tr_to_ascii
import os
import uuid
import hashlib
from datetime import datetime
import db
from fpdf import FPDF
import tempfile

os.environ["SIPHRIX_POLICY_FILE"] = str(Path(__file__).parent / "safe.yaml")

from siphrix.policy_runtime import PolicyManager

from ai_metadata import detect_ai_metadata
from pdf_signer import pdf_imzala, imza_ayarli_mi
from deepfake_detector import deepfake_tespit_et
try:
    from c2pa import Reader
    C2PA_AKTIF = True
except:
    C2PA_AKTIF = False


import json as _json
import csv as _csv
import io as _io


def json_cikti_olustur(rapor_no, musteri_adi, sektor, chatbot_url, iletisim_kisi, denetci_adi, ai_tipi, genel, karar_50_1, c2pa_sonuc, dayaniklilik_sonuc, duygu_sonuc, deepfake_sonuc, kamu_metni_sonuc):
    """Detayli JSON cikti olusturur."""
    def _temizle(d):
        if d is None:
            return None
        return {k: v for k, v in d.items() if k != "oneri"}
    return {
        "rapor_no": rapor_no,
        "musteri": {
            "ad": musteri_adi,
            "sektor": sektor,
            "chatbot_url": chatbot_url,
            "iletisim": iletisim_kisi,
        },
        "denetim": {
            "denetci": denetci_adi,
            "tarih": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "ai_tipi": ai_tipi,
            "kapsam": "AB AI Act Madde 50",
        },
        "genel_sonuc": genel,
        "maddeler": {
            "50_1_chatbot": karar_50_1 if karar_50_1.get("verdict") != "N/A" else None,
            "50_2_c2pa": c2pa_sonuc,
            "50_2_dayaniklilik": dayaniklilik_sonuc,
            "50_3_duygu_biyometrik": _temizle(duygu_sonuc),
            "50_4a_deepfake": _temizle(deepfake_sonuc),
            "50_4b_kamu_metni": _temizle(kamu_metni_sonuc),
        },
        "ceza_riski": "15 milyon Euro veya dunya capinda yillik cironun %3u (hangisi yuksekse)" if genel == "UYUMSUZ" else None,
    }


def csv_cikti_olustur(rapor_no, musteri_adi, sektor, ai_tipi, denetci_adi, genel, karar_50_1, c2pa_sonuc, duygu_sonuc, deepfake_sonuc, kamu_metni_sonuc):
    """CSV cikti olusturur."""
    buf = _io.StringIO()
    w = _csv.writer(buf)
    w.writerow(["rapor_no", "musteri", "sektor", "ai_tipi", "denetci", "genel_sonuc", "karar", "kanit_id", "c2pa", "duygu", "deepfake", "kamu_metni", "tarih"])
    w.writerow([
        rapor_no, musteri_adi, sektor, ai_tipi, denetci_adi, genel,
        karar_50_1.get("verdict", "N/A"),
        karar_50_1.get("decision_id", "N/A"),
        c2pa_sonuc.get("durum", "N/A") if c2pa_sonuc else "N/A",
        duygu_sonuc.get("durum", "N/A") if duygu_sonuc else "N/A",
        deepfake_sonuc.get("durum", "N/A") if deepfake_sonuc else "N/A",
        kamu_metni_sonuc.get("durum", "N/A") if kamu_metni_sonuc else "N/A",
        datetime.now().strftime("%Y-%m-%d %H:%M"),
    ])
    return buf.getvalue().encode("utf-8-sig")


from ai_metadata import detect_ai_metadata
from deepfake_detector import deepfake_tespit_et


class RaporPDF(FPDF):
    def header(self):
        # ============================================================
        # VERAXIO MARKA HEADER
        # ============================================================
        # En ust mavi serit
        self.set_fill_color(59, 130, 246)  # #3b82f6
        self.rect(0, 0, 210, 4, "F")

        # Bosluk
        self.ln(4)

        # Logo - mavi kare + beyaz diamond cizimi
        x_logo = self.get_x()
        y_logo = self.get_y()

        # Mavi kare (arka plan)
        self.set_fill_color(59, 130, 246)  # #3b82f6
        self.rect(x_logo, y_logo, 8, 8, "F")

        # Beyaz diamond (kare icinde)
        self.set_fill_color(255, 255, 255)
        # Diamond'i 4 noktali poligon olarak ciz
        cx = x_logo + 4
        cy = y_logo + 4
        self.polygon(
            [(cx, cy - 3), (cx + 3, cy), (cx, cy + 3), (cx - 3, cy)],
            style="F"
        )

        # Logo sagina gec
        self.set_x(x_logo + 11)

        # VERAXIO yazisi - mavi, buyuk
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(59, 130, 246)
        self.cell(0, 8, "VERAXIO", align="L", new_x="LMARGIN", new_y="NEXT")

        # Alt yazi - gri, kucuk
        self.set_font("Helvetica", "", 9)
        self.set_text_color(115, 115, 115)
        self.cell(0, 5, "AI Act Compliance Platform  |  veraxio.ai", align="L", new_x="LMARGIN", new_y="NEXT")

        # Bosluk
        self.ln(4)

        # Rapor basligi
        self.set_text_color(0, 0, 0)
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 8, "AI COMPLIANCE AUDIT REPORT", align="C", new_x="LMARGIN", new_y="NEXT")

        # Bosluk
        self.ln(2)

        # Alt gri cizgi
        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.2)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        # Gri cizgi
        self.set_y(-18)
        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.2)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(2)

        # Sol: Veraxio  |  Sag: Sayfa numarasi
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(115, 115, 115)
        self.cell(95, 5, "Veraxio  |  info@veraxio.ai", align="L")
        self.cell(95, 5, "Sayfa " + str(self.page_no()), align="R")


def c2pa_kontrol(dosya_yolu):
    if not C2PA_AKTIF:
        return {"durum": "KUTUPHANE_YOK", "uretim_araci": None}
    if not dosya_yolu or not os.path.exists(dosya_yolu):
        return {"durum": "DOSYA_YOK", "uretim_araci": None}
    uzanti = dosya_yolu.lower().split(".")[-1]
    fmt = {"jpg":"image/jpeg","jpeg":"image/jpeg","png":"image/png","webp":"image/webp"}.get(uzanti, "image/jpeg")
    try:
        with open(dosya_yolu, "rb") as f:
            reader = Reader(fmt, f)
            if reader.is_valid:
                uretici = None
                try:
                    import json
                    data = json.loads(reader.json())
                    active = data.get("active_manifest")
                    manifests = data.get("manifests", {})
                    if active and active in manifests:
                        cg = manifests[active].get("claim_generator_info", [])
                        if cg:
                            uretici = cg[0].get("name")
                except:
                    pass
                return {"durum": "ISARETLI", "uretim_araci": uretici}
            else:
                return {"durum": "GECERSIZ", "uretim_araci": None}
    except:
        return {"durum": "ISARETSIZ", "uretim_araci": None}


def c2pa_dayaniklilik_testi(dosya_yolu):
    if not C2PA_AKTIF or not dosya_yolu:
        return {"durum": "TEST_EDILEMEDI"}
    try:
        from PIL import Image
        uzanti = dosya_yolu.lower().split(".")[-1]
        with tempfile.NamedTemporaryFile(delete=False, suffix="." + uzanti) as tmp:
            sikistirilmis_yol = tmp.name
        img = Image.open(dosya_yolu)
        if uzanti in ["jpg", "jpeg"]:
            img = img.convert("RGB")
            img.save(sikistirilmis_yol, "JPEG", quality=50)
        elif uzanti == "png":
            img.save(sikistirilmis_yol, "PNG", optimize=True)
        else:
            return {"durum": "TEST_EDILEMEDI"}
        sonuc = c2pa_kontrol(sikistirilmis_yol)
        try:
            os.unlink(sikistirilmis_yol)
        except:
            pass
        if sonuc["durum"] == "ISARETLI":
            return {"durum": "DAYANIKLI"}
        else:
            return {"durum": "DAYANIKSIZ"}
    except:
        return {"durum": "TEST_HATASI"}




def pdf_bytes_al(pdf, imzala=True, zaman_damgasi_dondur=False):
    """
    FPDF nesnesinden bytes alir, opsiyonel olarak dijital imza ekler.

    Args:
        pdf: FPDF nesnesi
        imzala: True ise dijital imza eklenir
        zaman_damgasi_dondur: True ise (bytes, zaman_damgasi_dict) dondurur

    Returns:
        bytes veya tuple: PDF bytes (veya bytes + zaman damgasi bilgileri)
    """
    import tempfile
    import os

    # Bos zaman damgasi
    bos_zaman = {
        "hash": None,
        "ots_bytes": None,
        "tsr_bytes": None,
        "tsa": None,
    }

    # Once imzasiz bytes al
    try:
        pdf_bytes = bytes(pdf.output())
    except Exception:
        if zaman_damgasi_dondur:
            return b"", bos_zaman
        return b""

    # Imzalama aktif mi?
    if not imzala or not imza_ayarli_mi():
        if zaman_damgasi_dondur:
            return pdf_bytes, bos_zaman
        return pdf_bytes

    # Gecici dosyaya yaz
    tmp_yolu = None
    imzali_yolu = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(pdf_bytes)
            tmp_yolu = tmp.name

        # Imzala
        sonuc = pdf_imzala(tmp_yolu)

        if sonuc["durum"] == "OK":
            imzali_yolu = sonuc["dosya"]
            with open(imzali_yolu, "rb") as f:
                imzali_bytes = f.read()

            # Zaman damgasi bilgilerini hazirla
            zaman = dict(bos_zaman)
            zd = sonuc.get("zaman_damgasi", {}) or {}

            # OTS
            if zd.get("ots"):
                ots_yolu = zd["ots"].get("dosya")
                if ots_yolu and os.path.exists(ots_yolu):
                    with open(ots_yolu, "rb") as f:
                        zaman["ots_bytes"] = f.read()
                zaman["hash"] = zd["ots"].get("hash")

            # TSA
            if zd.get("tsa"):
                tsr_yolu = zd["tsa"].get("dosya")
                if tsr_yolu and os.path.exists(tsr_yolu):
                    with open(tsr_yolu, "rb") as f:
                        zaman["tsr_bytes"] = f.read()
                zaman["tsa"] = zd["tsa"].get("tsa")
                if not zaman["hash"]:
                    zaman["hash"] = zd["tsa"].get("hash")

            # OTS/TSR gecici dosyalarini sil
            for yol in [
                zd.get("ots", {}).get("dosya") if zd.get("ots") else None,
                zd.get("tsa", {}).get("dosya") if zd.get("tsa") else None,
            ]:
                if yol and os.path.exists(yol):
                    try:
                        os.unlink(yol)
                    except Exception:
                        pass

            if zaman_damgasi_dondur:
                return imzali_bytes, zaman
            return imzali_bytes
        else:
            if zaman_damgasi_dondur:
                return pdf_bytes, bos_zaman
            return pdf_bytes

    except Exception as e:
        if zaman_damgasi_dondur:
            return pdf_bytes, bos_zaman
        return pdf_bytes

    finally:
        # Gecici dosyalari temizle
        for yol in [tmp_yolu, imzali_yolu]:
            if yol and os.path.exists(yol):
                try:
                    os.unlink(yol)
                except Exception:
                    pass


def ai_kapsamli_kontrol(dosya_yolu):
    """
    Kapsamli AI kontrol: C2PA + ai_metadata + deepfake model.
    Uc katmanli tespit yapar.
    """
    sonuc = {
        "c2pa": None,
        "ai_metadata": None,
        "deepfake_model": None,
        "ai_olasi": False,
        "kaynaklar": [],
    }

    # 1) C2PA
    try:
        sonuc["c2pa"] = c2pa_kontrol(dosya_yolu)
        if sonuc["c2pa"] and sonuc["c2pa"].get("durum") == "ISARETLI":
            sonuc["ai_olasi"] = True
            sonuc["kaynaklar"].append("C2PA metadata")
    except Exception as e:
        sonuc["c2pa"] = {"durum": "HATA", "hata": str(e)[:50]}

    # 2) ai_metadata (PNG chunks, IPTC, XMP)
    try:
        with open(dosya_yolu, "rb") as f:
            data = f.read()
        sonuc["ai_metadata"] = detect_ai_metadata(data)
        if sonuc["ai_metadata"] and sonuc["ai_metadata"].get("ai_declared"):
            sonuc["ai_olasi"] = True
            kaynak = sonuc["ai_metadata"].get("source", "ai_metadata")
            if kaynak not in sonuc["kaynaklar"]:
                sonuc["kaynaklar"].append(kaynak)
    except Exception as e:
        sonuc["ai_metadata"] = {"hata": str(e)[:50]}

    # 3) Deepfake model
    try:
        sonuc["deepfake_model"] = deepfake_tespit_et(dosya_yolu)
        if sonuc["deepfake_model"] and sonuc["deepfake_model"].get("durum") == "DEEPFAKE":
            sonuc["ai_olasi"] = True
            sonuc["kaynaklar"].append("Deepfake modeli")
    except Exception as e:
        sonuc["deepfake_model"] = {"durum": "HATA", "hata": str(e)[:50]}

    return sonuc


def ai_bildirimi_var_mi(mesaj):
    if not mesaj:
        return False
    anahtar = ["yapay zeka", "ai", "asistan", "bot", "otomatik", "robot", "chatbot"]
    return any(k in mesaj.lower() for k in anahtar)


def duygu_tanima_kontrol(bildirim_var, hedef_kitle, biyometrik_veri):
    sonuc = {"durum": "UYUMLU", "yasak": False, "bulgular": [], "oneri": []}
    if not bildirim_var:
        sonuc["durum"] = "UYUMSUZ"
        sonuc["bulgular"].append("Kullanicilara duygu tanima bildirimi YAPILMIYOR")
        sonuc["oneri"].append("Ilk etkilesimde acik ve anlasilir bildirim ekleyin.")
    else:
        sonuc["bulgular"].append("Duygu tanima bildirimi VAR")
    if biyometrik_veri:
        sonuc["bulgular"].append("Biyometrik veri isleniyor")
        sonuc["oneri"].append("Irk, siyasi gorus, dini inanc cikarimi YASAK (Madde 5).")
    if hedef_kitle == "Savunmasiz Grup":
        sonuc["bulgular"].append("Hedef kitle savunmasiz grup")
        sonuc["oneri"].append("Bildirim ozellikle acik ve erisilebilir olmali.")
    return sonuc


def deepfake_kontrol(ai_uretim_mi, gercekci_mi, gorunur_etiket_var_mi, sanatsal_eser_mi):
    sonuc = {"durum": "UYUMLU", "bulgular": [], "oneri": []}
    if not ai_uretim_mi:
        sonuc["bulgular"].append("Icerik AI ile uretilmemis - kapsam disi")
        return sonuc
    if not gercekci_mi:
        sonuc["bulgular"].append("Icerik gercekci degil (fantezi/kurgu) - deepfake sayilmaz")
        if sanatsal_eser_mi:
            sonuc["bulgular"].append("Sanatsal eser - hafif etiket yeterli")
        return sonuc
    sonuc["bulgular"].append("Gercekci AI icerigi tespit edildi (deepfake)")
    if sanatsal_eser_mi:
        sonuc["bulgular"].append("Sanatsal/hiciv eser - hafifletilmis etiket yeterli (Madde 50(4) muafiyeti)")
        if not gorunur_etiket_var_mi:
            sonuc["durum"] = "UYUMSUZ"
            sonuc["bulgular"].append("Sanatsal muafiyet icin bile icerigin AI uretimi oldugu belirtilmeli")
            sonuc["oneri"].append("En azindan icerigin AI ile uretildigini belirtin (aciklama, jenerik vb.).")
        else:
            sonuc["bulgular"].append("AI uretimi oldugu belirtilmis - muafiyet gecerli")
        return sonuc
    if not gorunur_etiket_var_mi:
        sonuc["durum"] = "UYUMSUZ"
        sonuc["bulgular"].append("Gorunur etiket YOK")
        sonuc["oneri"].append("Icerige gorunur 'AI ile uretilmistir' etiketi ekleyin.")
        sonuc["oneri"].append("Etiket ilk maruziyette gorunur olmali.")
    else:
        sonuc["bulgular"].append("Gorunur etiket VAR")
    return sonuc


def kamu_metni_kontrol(ai_uretim_mi, kamu_yarari_mi, insan_denetimi_mi, editoryal_sorumlu_mu, gorunur_etiket_var_mi):
    sonuc = {"durum": "UYUMLU", "bulgular": [], "oneri": []}
    if not ai_uretim_mi:
        sonuc["bulgular"].append("Metin AI ile uretilmemis - kapsam disi")
        return sonuc
    if not kamu_yarari_mi:
        sonuc["bulgular"].append("Metin kamu yarari konusunda degil - kapsam disi")
        return sonuc
    sonuc["bulgular"].append("AI uretimi kamu yarari metni tespit edildi")
    if insan_denetimi_mi and editoryal_sorumlu_mu:
        sonuc["bulgular"].append("Insan denetimi ve editoryal sorumluluk VAR - muafiyet uygulanabilir")
        sonuc["oneri"].append("Muafiyet icin insan denetimi kayitlarini saklayin.")
        return sonuc
    if not gorunur_etiket_var_mi:
        sonuc["durum"] = "UYUMSUZ"
        sonuc["bulgular"].append("Gorunur etiket YOK ve muafiyet sartlari saglanmiyor")
        sonuc["oneri"].append("Metne 'AI ile uretilmistir' etiketi ekleyin.")
    else:
        sonuc["bulgular"].append("Gorunur etiket VAR")
    return sonuc









def ai_metin_tespit_kontrol(metin):
    """AI metin tespiti (RoBERTa modeli)."""
    from ai_text_detector import ai_metin_tespit_et
    return ai_metin_tespit_et(metin)


def synthid_kontrol(metin):
    """SynthID filigran dogrulama."""
    from synthid_detector import synthid_dogrula
    return synthid_dogrula(metin)










def kumulatif_kontrol(chatbot, gorsel, duygu, deepfake, kamu_metni, kvkk,
                       ab_musteri, shadow_ai):
    """
    Kumulatif yukumluluk analizi.
    Bir sirkette birden fazla AI sistemi varsa, hangi yukumluluklerin
    ayni anda gecerli oldugunu tespit eder.

    Returns:
        dict: {
            "durum": "UYUMLU" | "KISMI" | "KAPSAMLI",
            "yukumlulukler": [],
            "madde_sayisi": int,
            "risk_skoru": int (0-100),
            "oncelik_sirasi": [],
            "bulgular": []
        }
    """
    sonuc = {
        "durum": "KAPSAM_DISI",
        "yukumlulukler": [],
        "madde_sayisi": 0,
        "risk_skoru": 0,
        "oncelik_sirasi": [],
        "bulgular": [],
    }

    yukumlulukler = []
    oncelik = []

    if chatbot:
        yukumlulukler.append("Madde 50(1) - Chatbot bildirimi")
        oncelik.append("Madde 50(1): Chatbot ilk mesajina AI bildirimi ekleyin")
    if gorsel:
        yukumlulukler.append("Madde 50(2) - Sentetik icerik isaretleme")
        oncelik.append("Madde 50(2): Gorsellere C2PA/watermark ekleyin")
    if duygu:
        yukumlulukler.append("Madde 50(3) - Duygu/biyometrik bildirim")
        oncelik.append("Madde 50(3): Duygu tanima bildirimi ekleyin")
    if deepfake:
        yukumlulukler.append("Madde 50(4)(a) - Deepfake etiketleme")
        oncelik.append("Madde 50(4)(a): Deepfake'lere gorunur etiket ekleyin")
    if kamu_metni:
        yukumlulukler.append("Madde 50(4)(b) - Kamu yarari metni")
        oncelik.append("Madde 50(4)(b): Kamu yarari metinlerini etiketleyin")
    if kvkk:
        yukumlulukler.append("KVKK Madde 11 - Otomatik karar")
        oncelik.append("KVKK Madde 11: Otomatik karara itiraz mekanizmasi kurun")
    if ab_musteri:
        yukumlulukler.append("Madde 22 - AB temsilcisi zorunlulugu")
        oncelik.append("Madde 22: AB'de yetkili temsilci atayin")
    if shadow_ai:
        yukumlulukler.append("Shadow AI - Sirket ici AI kullanimi")
        oncelik.append("Shadow AI: AI kullanim politikasi olusturun")

    madde_sayisi = len(yukumlulukler)

    # Risk skoru (0-100)
    risk = 0
    if chatbot: risk += 15
    if gorsel: risk += 15
    if duygu: risk += 12
    if deepfake: risk += 15
    if kamu_metni: risk += 10
    if kvkk: risk += 15
    if ab_musteri: risk += 10
    if shadow_ai: risk += 8
    risk = min(risk, 100)

    # Durum
    if madde_sayisi == 0:
        sonuc["durum"] = "KAPSAM_DISI"
        sonuc["bulgular"].append("Hicbir AI sistemi secilmedi.")
    elif madde_sayisi <= 2:
        sonuc["durum"] = "UYUMLU"
        sonuc["bulgular"].append(f"{madde_sayisi} yukumluluk tespit edildi. Dusuk risk.")
    elif madde_sayisi <= 5:
        sonuc["durum"] = "KISMI"
        sonuc["bulgular"].append(f"{madde_sayisi} yukumluluk tespit edildi. Orta risk.")
    else:
        sonuc["durum"] = "KAPSAMLI"
        sonuc["bulgular"].append(f"{madde_sayisi} yukumluluk tespit edildi. Yuksek risk - kapsamli uyum gerekli.")

    sonuc["yukumlulukler"] = yukumlulukler
    sonuc["madde_sayisi"] = madde_sayisi
    sonuc["risk_skoru"] = risk
    sonuc["oncelik_sirasi"] = oncelik

    return sonuc

def shadow_ai_kontrol(ai_kullanim, politika, onayli_liste, veri_siniflandirma,
                       veri_izleme, egitim, onay_sureci, dlp):
    """
    Shadow AI taramasi.

    Args:
        ai_kullanim: Calisanlar AI araclarini kullaniyor mu?
        politika: AI kullanim politikasi var mi?
        onayli_liste: Onayli AI araclari listesi var mi?
        veri_siniflandirma: Veri siniflandirmasi yapiliyor mu?
        veri_izleme: AI araclarina veri gonderimi izleniyor mu?
        egitim: Calisanlara AI farkindalik egitimi veriliyor mu?
        onay_sureci: AI araclari icin onay sureci var mi?
        dlp: Veri kaybi onleme (DLP) sistemi var mi?

    Returns:
        dict: {"durum": "...", "bulgular": [], "oneri": [], "risk_seviyesi": "..."}
    """
    sonuc = {"durum": "UYUMLU", "bulgular": [], "oneri": [], "risk_seviyesi": "DUSUK"}

    # AI kullanilmiyorsa kapsam disi
    if not ai_kullanim:
        sonuc["durum"] = "KAPSAM_DISI"
        sonuc["bulgular"].append("Calisanlar AI araclari kullanmiyor - kapsam disi")
        return sonuc

    ihlaller = []
    kritik_risk = False

    if not politika:
        ihlaller.append("AI kullanim politikasi YOK")
        sonuc["oneri"].append("AI kullanim politikasi olusturun.")
        kritik_risk = True

    if not onayli_liste:
        ihlaller.append("Onayli AI araclari listesi YOK")
        sonuc["oneri"].append("Onayli AI araclari listesi olusturun.")
        kritik_risk = True

    if not veri_siniflandirma:
        ihlaller.append("Veri siniflandirmasi YAPILMIYOR")
        sonuc["oneri"].append("Veri siniflandirmasi yapin (kamu, ic, gizli, cok gizli).")

    if not veri_izleme:
        ihlaller.append("AI araclarina veri gonderimi IZLENMIYOR")
        sonuc["oneri"].append("Veri gonderimini izleyin (log, DLP entegrasyonu).")

    if not egitim:
        ihlaller.append("Calisanlara AI farkindalik egitimi VERILMIYOR")
        sonuc["oneri"].append("Calisanlara AI farkindalik egitimi verin.")

    if not onay_sureci:
        ihlaller.append("AI araclari icin onay sureci YOK")
        sonuc["oneri"].append("AI araclari icin onay sureci kurun.")
        kritik_risk = True

    if not dlp:
        ihlaller.append("DLP (veri kaybi onleme) sistemi YOK")
        sonuc["oneri"].append("DLP sistemi kurun (gizli veri sizmasini onleyin).")

    # Risk seviyesi
    if kritik_risk and len(ihlaller) >= 3:
        sonuc["risk_seviyesi"] = "KRITIK"
    elif len(ihlaller) >= 3:
        sonuc["risk_seviyesi"] = "YUKSEK"
    elif len(ihlaller) >= 1:
        sonuc["risk_seviyesi"] = "ORTA"

    sonuc["bulgular"] = ihlaller if ihlaller else ["Shadow AI riski dusuk."]
    if ihlaller:
        sonuc["durum"] = "UYUMSUZ"

    return sonuc

def ab_temsilcisi_kontrol(ab_musteri, ab_ofis, temsilci_var, temsilci_ab, temsilci_yetki, temsilci_ilan):
    """
    AB Temsilcisi kontrolu (AI Act Madde 22).

    Args:
        ab_musteri: AB'de musteri var mi?
        ab_ofis: AB'de ofis var mi?
        temsilci_var: AB merkezli yetkili temsilci var mi?
        temsilci_ab: Temsilci AB'de yerlesik mi?
        temsilci_yetki: Temsilci yazili yetkiye sahip mi?
        temsilci_ilan: Temsilci bilgileri ilan edilmis mi?

    Returns:
        dict: {"durum": "UYUMLU"|"UYUMSUZ"|"KAPSAM_DISI", "bulgular": [], "oneri": []}
    """
    sonuc = {"durum": "UYUMLU", "bulgular": [], "oneri": []}

    # AB musterisi yoksa kapsam disi
    if not ab_musteri and not ab_ofis:
        sonuc["durum"] = "KAPSAM_DISI"
        sonuc["bulgular"].append("AB'de musteri veya ofis yok - kapsam disi")
        return sonuc

    # AB ofisi varsa temsilciye gerek yok
    if ab_ofis:
        sonuc["bulgular"].append("AB'de ofis var - temsilci zorunlu degil")
        return sonuc

    # AB musterisi var ama ofis yok - temsilci kontrolu
    ihlaller = []

    if not temsilci_var:
        ihlaller.append("AB merkezli yetkili temsilci atanmamis (Madde 22)")
        sonuc["oneri"].append("AB'de yerlesik yetkili temsilci atayin.")

    if temsilci_var and not temsilci_ab:
        ihlaller.append("Temsilci AB'de yerlesik degil (Madde 22)")
        sonuc["oneri"].append("Temsilcinin AB'de yerlesik oldugundan emin olun.")

    if temsilci_var and not temsilci_yetki:
        ihlaller.append("Temsilci yazili yetkiye sahip degil (Madde 22)")
        sonuc["oneri"].append("Temsilciye yazili yetki belgesi verin.")

    if temsilci_var and not temsilci_ilan:
        ihlaller.append("Temsilci bilgileri ilan edilmemis (Madde 22)")
        sonuc["oneri"].append("Temsilci bilgilerini web sitenizde ilan edin.")

    sonuc["bulgular"] = ihlaller if ihlaller else ["AB temsilcisi uyumlulugu saglanmis."]
    if ihlaller:
        sonuc["durum"] = "UYUMSUZ"

    return sonuc

def kvkk_kontrol(otomatik_karar, insan_mudahale, acik_riza, itiraz_hakki,
                 aydinlatma, veri_sorumlusu, amac_netligi, yurtdisi_aktarim):
    """
    KVKK uyum kontrolu.

    Args:
        otomatik_karar: Otomatik karar sistemi var mi?
        insan_mudahale: Insan mudahalesi var mi?
        acik_riza: Acik riza aliniyor mu?
        itiraz_hakki: Itiraz hakki taniniyor mu?
        aydinlatma: Aydinlatma yukumlulugu yerine getiriliyor mu?
        veri_sorumlusu: Veri sorumlusu belirli mi?
        amac_netligi: Veri isleme amaci net mi?
        yurtdisi_aktarim: Yurt disina veri aktarimi var mi?

    Returns:
        dict: {"durum": "UYUMLU"|"UYUMSUZ"|"KISMEN_UYUMLU", "bulgular": [], "oneri": []}
    """
    sonuc = {"durum": "UYUMLU", "bulgular": [], "oneri": []}
    ihlaller = []

    if otomatik_karar and not insan_mudahale:
        ihlaller.append("Otomatik karar sistemi var ama insan mudahalesi YOK (KVKK 11)")
        sonuc["oneri"].append("Otomatik karara itiraz mekanizmasi kurun.")

    if not acik_riza:
        ihlaller.append("Acik riza alinmiyor (KVKK 5)")
        sonuc["oneri"].append("Kisisel veri isleme icin acik riza metni ekleyin.")

    if not itiraz_hakki:
        ihlaller.append("Itiraz hakki taninmiyor (KVKK 11)")
        sonuc["oneri"].append("Kullanicilara itiraz hakki taninin.")

    if not aydinlatma:
        ihlaller.append("Aydinlatma yukumlulugu yerine getirilmiyor (KVKK 10)")
        sonuc["oneri"].append("Gizlilik politikasi / aydinlatma metni ekleyin.")

    if not veri_sorumlusu:
        ihlaller.append("Veri sorumlusu belirli degil (KVKK 3)")
        sonuc["oneri"].append("Veri sorumlusunu belirleyin ve ilan edin.")

    if not amac_netligi:
        ihlaller.append("Veri isleme amaci net degil (KVKK 4)")
        sonuc["oneri"].append("Veri isleme amacini netlestirin.")

    if yurtdisi_aktarim:
        ihlaller.append("Yurt disina veri aktarimi var (KVKK 9)")
        sonuc["oneri"].append("Yurt disi aktarim icin uygun guvenceler saglayin.")

    sonuc["bulgular"] = ihlaller if ihlaller else ["KVKK uyumlulugu saglanmis."]
    if ihlaller:
        sonuc["durum"] = "UYUMSUZ"

    return sonuc


def kvkk_dokuman_analiz(dosya_yolu):
    """
    Yuklenen dokumanda KVKK anahtar kelimelerini arar.

    Args:
        dosya_yolu: PDF veya TXT dosya yolu

    Returns:
        dict: {"bulunan": [], "eksik": [], "durum": "..."}
    """
    import os
    metin = ""
    try:
        if dosya_yolu.lower().endswith(".pdf"):
            try:
                from pypdf import PdfReader
                reader = PdfReader(dosya_yolu)
                for page in reader.pages:
                    metin += page.extract_text() or ""
            except ImportError:
                return {"durum": "HATA", "hata": "pypdf yuklu degil. pip install pypdf"}
        else:
            with open(dosya_yolu, "r", encoding="utf-8", errors="ignore") as f:
                metin = f.read()
    except Exception as e:
        return {"durum": "HATA", "hata": str(e)[:100]}

    metin_lower = metin.lower()

    anahtar_kelimeler = {
        "acik riza": ["acik riza", "açık rıza", "explicit consent"],
        "aydinlatma": ["aydinlatma", "aydınlatma", "gizlilik politikasi", "privacy policy"],
        "itiraz hakki": ["itiraz", "objection", "right to object"],
        "veri sorumlusu": ["veri sorumlusu", "data controller"],
        "otomatik karar": ["otomatik karar", "automated decision"],
        "insan mudahale": ["insan mudahale", "human intervention", "human review"],
        "veri isleme amaci": ["veri isleme amaci", "purpose of processing"],
        "yurtdisi aktarim": ["yurt disi", "yurtdışı", "cross-border", "transfer abroad"],
    }

    bulunan = []
    eksik = []
    for anahtar, varyasyonlar in anahtar_kelimeler.items():
        if any(v in metin_lower for v in varyasyonlar):
            bulunan.append(anahtar)
        else:
            eksik.append(anahtar)

    durum = "UYUMLU" if not eksik else ("KISMEN_UYUMLU" if len(bulunan) >= 4 else "UYUMSUZ")

    return {
        "durum": durum,
        "bulunan": bulunan,
        "eksik": eksik,
        "uzunluk": len(metin),
    }

def ai_image_detector_kontrol(dosya_yolu):
    """Genel AI gorsel tespiti (wkaandemir modeli)."""
    from ai_image_detector import ai_image_tespit_et
    return ai_image_tespit_et(dosya_yolu)


def ai_metadata_kontrol(dosya_yolu):
    """
    Gorselin AI-provenance metadata'sini kontrol eder.
    Stable Diffusion, ComfyUI, InvokeAI, Midjourney vb. imzalarini yakalar.
    """
    try:
        with open(dosya_yolu, "rb") as f:
            data = f.read()
        return detect_ai_metadata(data)
    except Exception as e:
        return {"ai_declared": False, "source": None, "c2pa_present": False, "hata": str(e)[:80]}


def deepfake_model_kontrol(dosya_yolu):
    """
    Deepfake modelini kullanarak gorseli analiz eder.
    Yuz deepfake'lerini tespit eder (SigLIP tabanli).
    """
    return deepfake_tespit_et(dosya_yolu)


def rapor_pdf_olustur(musteri_adi, sektor, chatbot_url, iletisim_kisi, denetci_adi, ai_tipi, karar_50_1, c2pa_sonuc, dayaniklilik_sonuc, duygu_sonuc, deepfake_sonuc=None, kamu_metni_sonuc=None, ai_metadata_sonuc=None, deepfake_model_sonuc=None, ai_image_detector_sonuc=None, metin_sonuc=None, synthid_sonuc=None, kvkk_sonuc=None, ab_sonuc=None, shadow_sonuc=None, kumulatif_sonuc=None):
    musteri_adi = tr_to_ascii(musteri_adi)
    sektor = tr_to_ascii(sektor)
    chatbot_url = tr_to_ascii(chatbot_url)
    iletisim_kisi = tr_to_ascii(iletisim_kisi)
    denetci_adi = tr_to_ascii(denetci_adi)
    ai_tipi_ascii = tr_to_ascii(ai_tipi)

    rapor_no = "AIACT-" + datetime.now().strftime("%Y%m%d") + "-" + str(uuid.uuid4())[:6].upper()

    pdf = RaporPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "Rapor No: " + rapor_no, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "CLIENT INFORMATION", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=11)
    pdf.cell(0, 7, "  Client: " + musteri_adi, new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "  Sector: " + sektor, new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "  Chatbot/Product URL: " + chatbot_url, new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "  Contact: " + iletisim_kisi, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "AUDIT INFORMATION", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=11)
    pdf.cell(0, 7, "  Auditor: " + denetci_adi, new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "  Date: " + datetime.now().strftime("%Y-%m-%d %H:%M"), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "  AI Type: " + ai_tipi_ascii, new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "  Scope: EU AI Act Article 50", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    if ai_tipi == "Chatbot / AI Asistan":
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "ARTICLE 50(1) - INTERACTION DISCLOSURE", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", size=11)
        if karar_50_1["bildirim_var"]:
            pdf.cell(0, 7, "  Status: COMPLIANT", new_x="LMARGIN", new_y="NEXT")
            pdf.cell(0, 7, "  Findings: AI disclosure PRESENT", new_x="LMARGIN", new_y="NEXT")
        else:
            pdf.cell(0, 7, "  Status: NON-COMPLIANT", new_x="LMARGIN", new_y="NEXT")
            pdf.cell(0, 7, "  Findings: AI disclosure MISSING", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 7, "  Evidence ID: " + str(karar_50_1["decision_id"]), new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 7, "  Decision: " + str(karar_50_1["verdict"]), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

    if ai_tipi == "Gorsel Uretimi (C2PA)":
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "ARTICLE 50(2) - SYNTHETIC CONTENT MARKING", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", size=11)
        if c2pa_sonuc:
            if c2pa_sonuc["durum"] == "KAPSAM_DISI":
                pdf.cell(0, 7, "  Durum: KAPSAM DISI", new_x="LMARGIN", new_y="NEXT")
                pdf.cell(0, 7, "  Not: Sadece yardimci duzenleme - muaf", new_x="LMARGIN", new_y="NEXT")
            elif c2pa_sonuc["durum"] == "ISARETLI":
                # LAYER 1: C2PA
                pdf.cell(0, 7, "  Layer 1: C2PA Metadata", new_x="LMARGIN", new_y="NEXT")
                pdf.cell(0, 7, "    C2PA metadata: PRESENT", new_x="LMARGIN", new_y="NEXT")
                uretici = tr_to_ascii(c2pa_sonuc.get("uretim_araci")) or "Bilinmiyor"
                pdf.cell(0, 7, "    Producer: " + uretici, new_x="LMARGIN", new_y="NEXT")

                # LAYER 2: AI Metadata
                if ai_metadata_sonuc:
                    pdf.cell(0, 7, "  Layer 2: AI Metadata (PNG/IPTC/XMP)", new_x="LMARGIN", new_y="NEXT")
                    if ai_metadata_sonuc.get("ai_declared"):
                        pdf.cell(0, 7, "    AI declared: YES", new_x="LMARGIN", new_y="NEXT")
                        src = tr_to_ascii(str(ai_metadata_sonuc.get("source", "")))[:55]
                        pdf.cell(0, 7, "    Source: " + src, new_x="LMARGIN", new_y="NEXT")
                    else:
                        pdf.cell(0, 7, "    AI declared: NO", new_x="LMARGIN", new_y="NEXT")

                # LAYER 3: Deepfake Model
                if deepfake_model_sonuc and deepfake_model_sonuc.get("durum") in ["DEEPFAKE", "GERCEK"]:
                    pdf.cell(0, 7, "  Layer 3: Deepfake Model (SigLIP, face-focused)", new_x="LMARGIN", new_y="NEXT")
                    if deepfake_model_sonuc["durum"] == "DEEPFAKE":
                        olasilik = round(deepfake_model_sonuc.get("fake_olasilik", 0) * 100, 1)
                        pdf.cell(0, 7, "    Result: DEEPFAKE (probability: " + str(olasilik) + "%)", new_x="LMARGIN", new_y="NEXT")
                    else:
                        olasilik = round(deepfake_model_sonuc.get("gercek_olasilik", 0) * 100, 1)
                        pdf.cell(0, 7, "    Result: REAL (probability: " + str(olasilik) + "%)", new_x="LMARGIN", new_y="NEXT")

                # LAYER 4: General AI Image Detector
                if ai_image_detector_sonuc and ai_image_detector_sonuc.get("durum") in ["YAPAY", "GERCEK", "BELIRSIZ"]:
                    pdf.cell(0, 7, "  Layer 4: General AI Image Detector (CLIP)", new_x="LMARGIN", new_y="NEXT")
                    if ai_image_detector_sonuc["durum"] == "YAPAY":
                        p = round(ai_image_detector_sonuc.get("p_fake", 0) * 100, 1)
                        pdf.cell(0, 7, "    Result: SYNTHETIC (p_fake: " + str(p) + "%)", new_x="LMARGIN", new_y="NEXT")
                    elif ai_image_detector_sonuc["durum"] == "BELIRSIZ":
                        pdf.cell(0, 7, "    Result: UNCERTAIN (p_real: " + str(ai_image_detector_sonuc.get("p_real")) + ")", new_x="LMARGIN", new_y="NEXT")
                    else:
                        p = round(ai_image_detector_sonuc.get("p_real", 0) * 100, 1)
                        pdf.cell(0, 7, "    Result: REAL (p_real: " + str(p) + "%)", new_x="LMARGIN", new_y="NEXT")

                # CELISKI KONTROLU (akilli)
                if ai_metadata_sonuc and ai_metadata_sonuc.get("ai_declared"):
                    yuz_yapay = deepfake_model_sonuc and deepfake_model_sonuc.get("durum") == "DEEPFAKE"
                    genel_yapay = ai_image_detector_sonuc and ai_image_detector_sonuc.get("durum") == "YAPAY"
                    if not (yuz_yapay or genel_yapay):
                        pdf.set_text_color(200, 100, 0)
                        pdf.cell(0, 7, "    WARNING: Metadata says AI, both models say REAL - conflict!", new_x="LMARGIN", new_y="NEXT")
                        pdf.set_text_color(0, 0, 0)

                # DAYANIKLILIK
                if dayaniklilik_sonuc:
                    if dayaniklilik_sonuc["durum"] == "DAYANIKLI":
                        pdf.cell(0, 7, "  Durability: DURABLE", new_x="LMARGIN", new_y="NEXT")
                        pdf.cell(0, 7, "  Status: COMPLIANT", new_x="LMARGIN", new_y="NEXT")
                    elif dayaniklilik_sonuc["durum"] == "DAYANIKSIZ":
                        pdf.cell(0, 7, "  Durability: NOT DURABLE", new_x="LMARGIN", new_y="NEXT")
                        pdf.cell(0, 7, "  Status: NON-COMPLIANT (not durable)", new_x="LMARGIN", new_y="NEXT")
            else:
                pdf.cell(0, 7, "  Status: NON-COMPLIANT", new_x="LMARGIN", new_y="NEXT")
                pdf.cell(0, 7, "  C2PA: " + str(c2pa_sonuc["durum"]), new_x="LMARGIN", new_y="NEXT")
        else:
            pdf.cell(0, 7, "  Status: NOT AUDITED", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

    if duygu_sonuc:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "ARTICLE 50(3) - EMOTION RECOGNITION / BIOMETRIC", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", size=11)
        if duygu_sonuc["durum"] == "YASAK":
            pdf.set_text_color(200, 0, 0)
            pdf.cell(0, 7, "  Status: PROHIBITED", new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(0, 0, 0)
        elif duygu_sonuc["durum"] == "UYUMSUZ":
            pdf.cell(0, 7, "  Status: NON-COMPLIANT", new_x="LMARGIN", new_y="NEXT")
        else:
            pdf.cell(0, 7, "  Status: COMPLIANT", new_x="LMARGIN", new_y="NEXT")
        for b in duygu_sonuc["bulgular"]:
            pdf.cell(0, 7, "  - " + tr_to_ascii(b), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

    if deepfake_sonuc:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "ARTICLE 50(4)(a) - DEEPFAKE LABELLING", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", size=11)
        if deepfake_sonuc["durum"] == "UYUMSUZ":
            pdf.cell(0, 7, "  Status: NON-COMPLIANT", new_x="LMARGIN", new_y="NEXT")
        else:
            pdf.cell(0, 7, "  Status: COMPLIANT", new_x="LMARGIN", new_y="NEXT")
        for b in deepfake_sonuc["bulgular"]:
            pdf.cell(0, 7, "  - " + tr_to_ascii(b), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

    if kamu_metni_sonuc:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "ARTICLE 50(4)(b) - PUBLIC INTEREST TEXT", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", size=11)
        if kamu_metni_sonuc["durum"] == "UYUMSUZ":
            pdf.cell(0, 7, "  Status: NON-COMPLIANT", new_x="LMARGIN", new_y="NEXT")
        else:
            pdf.cell(0, 7, "  Status: COMPLIANT", new_x="LMARGIN", new_y="NEXT")
        for b in kamu_metni_sonuc["bulgular"]:
            pdf.cell(0, 7, "  - " + tr_to_ascii(b), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

    genel = "UYUMLU"
    if ai_tipi == "Chatbot / AI Asistan":
        if not karar_50_1["bildirim_var"]:
            genel = "UYUMSUZ"
    elif ai_tipi == "Gorsel Uretimi (C2PA)":
        if c2pa_sonuc and c2pa_sonuc["durum"] not in ["ISARETLI", "KAPSAM_DISI"]:
            genel = "UYUMSUZ"
        if dayaniklilik_sonuc and dayaniklilik_sonuc["durum"] == "DAYANIKSIZ":
            genel = "UYUMSUZ"
    elif duygu_sonuc:
        if duygu_sonuc["durum"] in ["YASAK", "UYUMSUZ"]:
            genel = "UYUMSUZ"
    if deepfake_sonuc and deepfake_sonuc["durum"] == "UYUMSUZ":
        genel = "UYUMSUZ"
    if kamu_metni_sonuc and kamu_metni_sonuc["durum"] == "UYUMSUZ":
        genel = "UYUMSUZ"
    if metin_sonuc and metin_sonuc.get("durum") == "AI":
        genel = "UYUMSUZ"
    if kvkk_sonuc and kvkk_sonuc.get("durum") == "UYUMSUZ":
        genel = "UYUMSUZ"
    if ab_sonuc and ab_sonuc.get("durum") == "UYUMSUZ":
        genel = "UYUMSUZ"
    if shadow_sonuc and shadow_sonuc.get("durum") == "UYUMSUZ":
        genel = "UYUMSUZ"
    if kumulatif_sonuc and kumulatif_sonuc.get("durum") in ["KISMI", "KAPSAMLI"]:
        genel = "UYUMSUZ"

    if metin_sonuc:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "ARTICLE 50 - TEXT AUDIT (AI DETECTION)", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", size=11)
        if metin_sonuc.get("durum") == "AI":
            p = round(metin_sonuc.get("ai_olasilik", 0) * 100, 1)
            pdf.cell(0, 7, "  Result: AI-GENERATED (probability: " + str(p) + "%)", new_x="LMARGIN", new_y="NEXT")
        elif metin_sonuc.get("durum") == "INSAN":
            p = round(metin_sonuc.get("insan_olasilik", 0) * 100, 1)
            pdf.cell(0, 7, "  Result: HUMAN-WRITTEN (probability: " + str(p) + "%)", new_x="LMARGIN", new_y="NEXT")
        else:
            pdf.cell(0, 7, "  Result: ERROR", new_x="LMARGIN", new_y="NEXT")
        if synthid_sonuc:
            synthid_en = {"DOGRULANAMADI": "NOT VERIFIABLE", "FILIGRANLI": "WATERMARKED", "FILIGRANSIZ": "NO WATERMARK", "HATA": "ERROR"}.get(synthid_sonuc.get("durum", "?"), synthid_sonuc.get("durum", "?"))
            pdf.cell(0, 7, "  SynthID: " + synthid_en, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

    if kvkk_sonuc:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "KVKK COMPLIANCE AUDIT", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", size=11)
        if kvkk_sonuc.get("durum") == "UYUMSUZ":
            pdf.cell(0, 7, "  Status: NON-COMPLIANT", new_x="LMARGIN", new_y="NEXT")
        else:
            pdf.cell(0, 7, "  Status: COMPLIANT", new_x="LMARGIN", new_y="NEXT")
        for b in kvkk_sonuc.get("bulgular", []):
            pdf.cell(0, 6, "  - " + tr_to_ascii(b)[:80], new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

    if ab_sonuc:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "EU REPRESENTATIVE CHECK (Article 22)", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", size=11)
        if ab_sonuc.get("durum") == "KAPSAM_DISI":
            pdf.cell(0, 7, "  Status: OUT OF SCOPE", new_x="LMARGIN", new_y="NEXT")
        elif ab_sonuc.get("durum") == "UYUMSUZ":
            pdf.cell(0, 7, "  Status: NON-COMPLIANT", new_x="LMARGIN", new_y="NEXT")
        else:
            pdf.cell(0, 7, "  Status: COMPLIANT", new_x="LMARGIN", new_y="NEXT")
        for b in ab_sonuc.get("bulgular", []):
            pdf.cell(0, 6, "  - " + tr_to_ascii(b)[:80], new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

    if shadow_sonuc:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "SHADOW AI SCAN", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", size=11)
        if shadow_sonuc.get("durum") == "KAPSAM_DISI":
            pdf.cell(0, 7, "  Status: OUT OF SCOPE", new_x="LMARGIN", new_y="NEXT")
        elif shadow_sonuc.get("durum") == "UYUMSUZ":
            risk = shadow_sonuc.get("risk_seviyesi", "?")
            pdf.cell(0, 7, "  Status: NON-COMPLIANT (Risk: " + risk + ")", new_x="LMARGIN", new_y="NEXT")
        else:
            pdf.cell(0, 7, "  Status: COMPLIANT", new_x="LMARGIN", new_y="NEXT")
        for b in shadow_sonuc.get("bulgular", []):
            pdf.cell(0, 6, "  - " + tr_to_ascii(b)[:80], new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

    if kumulatif_sonuc and kumulatif_sonuc.get("madde_sayisi", 0) > 0:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "CUMULATIVE OBLIGATION ANALYSIS", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", size=11)
        pdf.cell(0, 7, "  Total obligations: " + str(kumulatif_sonuc["madde_sayisi"]), new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 7, "  Risk score: %" + str(kumulatif_sonuc["risk_skoru"]), new_x="LMARGIN", new_y="NEXT")
        for y in kumulatif_sonuc.get("yukumlulukler", []):
            pdf.cell(0, 6, "  - " + tr_to_ascii(y)[:80], new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

    # AI CONTENT LABELS (EU AI Act Article 50(2))
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "AI CONTENT LABELS (EU AI Act Article 50(2)):", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=9)

    # Etiket belirleme
    ai_generated = "NO"
    ai_modified = "NO"
    ai_deepfake = "NO"

    # C2PA / metadata kontrolu
    if c2pa_sonuc and c2pa_sonuc.get("durum") == "ISARETLI":
        ai_generated = "YES"
    if ai_metadata_sonuc and ai_metadata_sonuc.get("ai_declared"):
        ai_generated = "YES"
    if deepfake_sonuc and deepfake_sonuc.get("durum") == "UYUMSUZ":
        ai_deepfake = "YES"
    if deepfake_model_sonuc and deepfake_model_sonuc.get("durum") == "DEEPFAKE":
        ai_deepfake = "YES"
    if ai_image_detector_sonuc and ai_image_detector_sonuc.get("durum") == "YAPAY":
        ai_generated = "YES"
    if metin_sonuc and metin_sonuc.get("durum") == "AI":
        ai_generated = "YES"

    pdf.cell(0, 5, "  [AI-GENERATED]  : " + ai_generated, new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, "  [AI-MODIFIED]   : " + ai_modified, new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, "  [AI-DEEPFAKE]   : " + ai_deepfake, new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, "  Suggested label: " + ("AI-GENERATED CONTENT" if ai_generated == "YES" else ("AI-DEEPFAKE" if ai_deepfake == "YES" else "NONE")), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    pdf.set_font("Helvetica", "B", 13)
    if genel == "UYUMSUZ":
        pdf.set_text_color(200, 0, 0)
    else:
        pdf.set_text_color(0, 150, 0)
    genel_en = "COMPLIANT" if genel == "UYUMLU" else "NON-COMPLIANT"
    pdf.cell(0, 9, "OVERALL RESULT: " + genel_en, new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)

    if genel == "UYUMSUZ":
        pdf.ln(3)
        pdf.set_font("Helvetica", size=11)
        pdf.cell(0, 7, "RECOMMENDED ACTIONS:", new_x="LMARGIN", new_y="NEXT")
        if ai_tipi == "Chatbot / AI Asistan" and not karar_50_1["bildirim_var"]:
            pdf.cell(0, 7, "  - Add AI disclosure to chatbot first message.", new_x="LMARGIN", new_y="NEXT")
        if ai_tipi == "Gorsel Uretimi (C2PA)":
            if not c2pa_sonuc or c2pa_sonuc["durum"] != "ISARETLI":
                pdf.cell(0, 7, "  - Add C2PA marking to images.", new_x="LMARGIN", new_y="NEXT")
            elif dayaniklilik_sonuc and dayaniklilik_sonuc["durum"] == "DAYANIKSIZ":
                pdf.cell(0, 7, "  - Use more durable marking (SynthID etc.).", new_x="LMARGIN", new_y="NEXT")
        if duygu_sonuc and duygu_sonuc["oneri"]:
            for o in duygu_sonuc["oneri"]:
                pdf.cell(0, 7, "  - " + tr_to_ascii(o), new_x="LMARGIN", new_y="NEXT")
        if deepfake_sonuc and deepfake_sonuc["oneri"]:
            for o in deepfake_sonuc["oneri"]:
                pdf.cell(0, 7, "  - " + tr_to_ascii(o), new_x="LMARGIN", new_y="NEXT")
        if kamu_metni_sonuc and kamu_metni_sonuc["oneri"]:
            for o in kamu_metni_sonuc["oneri"]:
                pdf.cell(0, 7, "  - " + tr_to_ascii(o), new_x="LMARGIN", new_y="NEXT")
        if metin_sonuc and metin_sonuc.get("durum") == "AI":
            pdf.cell(0, 7, "  - Disclose that the text was AI-generated (Article 50(2)).", new_x="LMARGIN", new_y="NEXT")
            pdf.cell(0, 7, "  - Add machine-readable marking if applicable.", new_x="LMARGIN", new_y="NEXT")
        if kvkk_sonuc and kvkk_sonuc.get("oneri"):
            for o in kvkk_sonuc["oneri"]:
                pdf.cell(0, 7, "  - " + tr_to_ascii(o)[:80], new_x="LMARGIN", new_y="NEXT")
        if ab_sonuc and ab_sonuc.get("oneri"):
            for o in ab_sonuc["oneri"]:
                pdf.cell(0, 7, "  - " + tr_to_ascii(o)[:80], new_x="LMARGIN", new_y="NEXT")
        if shadow_sonuc and shadow_sonuc.get("oneri"):
            for o in shadow_sonuc["oneri"]:
                pdf.cell(0, 7, "  - " + tr_to_ascii(o)[:80], new_x="LMARGIN", new_y="NEXT")
        if kumulatif_sonuc and kumulatif_sonuc.get("oncelik_sirasi"):
            for o in kumulatif_sonuc["oncelik_sirasi"]:
                pdf.cell(0, 7, "  - " + tr_to_ascii(o)[:80], new_x="LMARGIN", new_y="NEXT")
        if metin_sonuc and metin_sonuc.get("durum") == "AI":
            pdf.cell(0, 7, "  - Disclose that the text was AI-generated (Article 50(2)).", new_x="LMARGIN", new_y="NEXT")
            pdf.cell(0, 7, "  - Add machine-readable marking if applicable.", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(200, 0, 0)
        pdf.cell(0, 8, "PENALTY RISK: Up to EUR 15 million or 3% of global annual turnover", new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)

    # HUKUKI BOLUMLER
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "LEGAL BASIS:", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=9)
    pdf.cell(0, 5, "  - EU AI Act Article 50(1): Transparency obligation", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, "  - EU AI Act Article 50(2): Synthetic content marking", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, "  - EU AI Act Article 50(5): First interaction disclosure", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, "  - KVKK Article 11: Automated decision systems", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, "  - Commission Article 50 Guidelines (2026)", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, "  - Code of Practice on Transparency (2026)", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "DISCLAIMER:", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=9)
    pdf.cell(0, 5, "  This report is a technical audit output. It does not constitute legal advice.", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, "  Consult a qualified lawyer for final legal assessment.", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    # Delil zinciri
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "CHAIN OF CUSTODY:", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=9)
    hash_input = f"{rapor_no}|{datetime.now().strftime('%Y-%m-%d %H:%M')}|{musteri_adi}|{ai_tipi}|{genel}".encode('utf-8')
    rapor_hash = hashlib.sha256(hash_input).hexdigest()[:16]
    pdf.cell(0, 5, f"  Report No: {rapor_no}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, f"  Hash (SHA-256): {rapor_hash}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, f"  Auditor: {denetci_adi}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, f"  Version: 1.4", new_x="LMARGIN", new_y="NEXT")

    return pdf, rapor_no


# ============================================================
# SAYFA ICERIGI
# ============================================================
db.init_db()

