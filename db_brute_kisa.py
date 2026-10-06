"""db.py'ye kisa brute force fonksiyonlari ekler."""
import shutil
from pathlib import Path
from datetime import datetime

KOK = Path(".")
HEDEF = KOK / "db.py"

icerik = HEDEF.read_text(encoding="utf-8")

if "def giris_denemesi_kaydet" in icerik:
    print("[i] Zaten var.")
    raise SystemExit(0)

zaman = datetime.now().strftime("%Y%m%d_%H%M%S")
yedek = KOK / f"db_brute_oncesi_{zaman}.py.bak"
shutil.copy2(HEDEF, yedek)
print(f"[+] Yedek: {yedek.name}")

BLOK = '''

# ============================================================
# BRUTE FORCE
# ============================================================
BRUTE_FORCE_MAX_DENEME = 5
BRUTE_FORCE_KILIT_DK = 15


def _bf_tablo_olustur():
    with _baglanti() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS giris_denemeleri (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kullanici_adi TEXT NOT NULL,
            ip_adresi TEXT,
            tarih TEXT NOT NULL,
            basarili INTEGER DEFAULT 0
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS hesap_kilitleri (
            kullanici_adi TEXT PRIMARY KEY,
            kilit_tarih TEXT NOT NULL,
            sebep TEXT DEFAULT 'brute_force',
            deneme_sayisi INTEGER DEFAULT 0
        )""")
        conn.commit()


try:
    _bf_tablo_olustur()
except Exception as e:
    print(f"[db] BF tablo hatasi: {e}")


def _son_basarisiz_denemeler(kullanici_adi, dakika=15):
    sinir = (datetime.now() - timedelta(minutes=dakika)).strftime("%Y-%m-%d %H:%M:%S")
    try:
        with _baglanti() as conn:
            cur = conn.execute("""SELECT COUNT(*) as n FROM giris_denemeleri
                WHERE kullanici_adi = ? AND basarili = 0 AND tarih >= ?""",
                (kullanici_adi, sinir))
            return cur.fetchone()["n"]
    except Exception:
        return 0


def _kilit_uygula(kullanici_adi, deneme_sayisi):
    simdi = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with _baglanti() as conn:
            conn.execute("""INSERT OR REPLACE INTO hesap_kilitleri
                (kullanici_adi, kilit_tarih, sebep, deneme_sayisi)
                VALUES (?, ?, 'brute_force', ?)""",
                (kullanici_adi, simdi, deneme_sayisi))
            conn.commit()
    except Exception:
        pass


def giris_denemesi_kaydet(kullanici_adi, ip_adresi=None, basarili=False):
    simdi = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with _baglanti() as conn:
            conn.execute("""INSERT INTO giris_denemeleri
                (kullanici_adi, ip_adresi, tarih, basarili) VALUES (?, ?, ?, ?)""",
                (kullanici_adi, ip_adresi, simdi, 1 if basarili else 0))
            conn.commit()
    except Exception:
        pass

    if basarili:
        giris_kilit_ac(kullanici_adi)
        return

    if _son_basarisiz_denemeler(kullanici_adi) >= BRUTE_FORCE_MAX_DENEME:
        _kilit_uygula(kullanici_adi, BRUTE_FORCE_MAX_DENEME)


def giris_kilitli_mi(kullanici_adi):
    try:
        with _baglanti() as conn:
            cur = conn.execute("""SELECT kilit_tarih FROM hesap_kilitleri
                WHERE kullanici_adi = ?""", (kullanici_adi,))
            row = cur.fetchone()
            if not row:
                return {"kilitli": False, "kalan_dk": 0}
            try:
                kilit_dt = datetime.strptime(row["kilit_tarih"], "%Y-%m-%d %H:%M:%S")
            except Exception:
                return {"kilitli": False, "kalan_dk": 0}
            gecen = (datetime.now() - kilit_dt).total_seconds() / 60
            kalan = BRUTE_FORCE_KILIT_DK - gecen
            if kalan <= 0:
                giris_kilit_ac(kullanici_adi)
                return {"kilitli": False, "kalan_dk": 0}
            return {"kilitli": True, "kalan_dk": int(kalan) + 1}
    except Exception:
        return {"kilitli": False, "kalan_dk": 0}


def giris_kilit_ac(kullanici_adi):
    try:
        with _baglanti() as conn:
            conn.execute("DELETE FROM hesap_kilitleri WHERE kullanici_adi = ?", (kullanici_adi,))
            conn.execute("DELETE FROM giris_denemeleri WHERE kullanici_adi = ?", (kullanici_adi,))
            conn.commit()
    except Exception:
        pass


def kalan_deneme_hakki(kullanici_adi):
    return max(0, BRUTE_FORCE_MAX_DENEME - _son_basarisiz_denemeler(kullanici_adi))
'''

icerik = icerik.rstrip() + "\n" + BLOK + "\n"
HEDEF.write_text(icerik, encoding="utf-8")
print("[+] db.py guncellendi.")
print(f"[i] Yeni satir sayisi: {len(icerik.splitlines())}")