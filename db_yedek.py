"""
db_yedek.py - Veritabani yedekleme modulu
SQLite veritabanini zaman damgali olarak yedekler.
Streamlit Cloud'da kalici depolama olmadigi icin
yedekler gecici olarak tutulur, indirilebilir.
"""
import os
import shutil
from datetime import datetime


def _db_yolu():
    """Veritabani dosyasinin tam yolunu dondurur."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "denetimler.db")


def yedek_klasoru():
    """Yedeklerin tutulacagi klasoru dondurur, yoksa olusturur."""
    klasor = os.path.join(os.path.dirname(os.path.abspath(__file__)), "yedekler")
    os.makedirs(klasor, exist_ok=True)
    return klasor


def yedek_al(etiket=""):
    """
    Veritabaninin yedegini alir.
    Donus: {"durum": "OK"|"HATA", "dosya": "...", "boyut": int, "mesaj": "..."}
    """
    db_yolu = _db_yolu()

    if not os.path.exists(db_yolu):
        return {"durum": "HATA", "mesaj": "Veritabani dosyasi bulunamadi: " + db_yolu}

    try:
        zaman = datetime.now().strftime("%Y%m%d_%H%M%S")
        etiket_temiz = "".join(c for c in etiket if c.isalnum() or c in "_-")[:30]
        dosya_adi = "denetimler_" + zaman
        if etiket_temiz:
            dosya_adi += "_" + etiket_temiz
        dosya_adi += ".db"

        hedef = os.path.join(yedek_klasoru(), dosya_adi)
        shutil.copy2(db_yolu, hedef)

        boyut = os.path.getsize(hedef)
        return {
            "durum": "OK",
            "dosya": hedef,
            "dosya_adi": dosya_adi,
            "boyut": boyut,
            "mesaj": "Yedek alindi: " + dosya_adi,
        }
    except Exception as e:
        return {"durum": "HATA", "mesaj": "Yedek alma hatasi: " + str(e)}


def yedek_listele():
    """Mevcut yedekleri listeler (en yeni once)."""
    klasor = yedek_klasoru()
    if not os.path.exists(klasor):
        return []

    yedekler = []
    for dosya in os.listdir(klasor):
        if dosya.endswith(".db"):
            tam_yol = os.path.join(klasor, dosya)
            try:
                boyut = os.path.getsize(tam_yol)
                tarih = datetime.fromtimestamp(os.path.getmtime(tam_yol))
                yedekler.append({
                    "dosya": dosya,
                    "yol": tam_yol,
                    "boyut": boyut,
                    "tarih": tarih.strftime("%Y-%m-%d %H:%M:%S"),
                })
            except Exception:
                continue

    yedekler.sort(key=lambda x: x["tarih"], reverse=True)
    return yedekler


def yedek_sil(dosya_adi):
    """Belirtilen yedegi siler."""
    tam_yol = os.path.join(yedek_klasoru(), dosya_adi)
    if os.path.exists(tam_yol):
        try:
            os.remove(tam_yol)
            return {"durum": "OK", "mesaj": "Silindi: " + dosya_adi}
        except Exception as e:
            return {"durum": "HATA", "mesaj": "Silme hatasi: " + str(e)}
    return {"durum": "HATA", "mesaj": "Dosya bulunamadi: " + dosya_adi}


def eski_yedekleri_temizle(gun=30):
    """Belirtilen gunden eski yedekleri siler."""
    from datetime import timedelta
    esik = datetime.now() - timedelta(days=gun)
    silinen = 0

    for y in yedek_listele():
        try:
            tarih = datetime.strptime(y["tarih"], "%Y-%m-%d %H:%M:%S")
            if tarih < esik:
                sonuc = yedek_sil(y["dosya"])
                if sonuc["durum"] == "OK":
                    silinen += 1
        except Exception:
            continue

    return {"durum": "OK", "silinen": silinen, "mesaj": str(silinen) + " yedek silindi"}
