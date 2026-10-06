"""
SQLite Veritabani Modulu
Denetim gecmisini saklar ve sorgular.
"""
import os
import json
import sqlite3
from datetime import datetime, timedelta


DB_YOLU = os.path.join(os.path.dirname(os.path.abspath(__file__)), "denetimler.db")


def _baglanti():
    """Yeni bir SQLite baglantisi dondurur."""
    conn = sqlite3.connect(DB_YOLU)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Veritabani tablolarini olusturur (yoksa)."""
    with _baglanti() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS denetimler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rapor_no TEXT UNIQUE NOT NULL,
                tarih TEXT NOT NULL,
                modul TEXT NOT NULL,
                musteri TEXT,
                sektor TEXT,
                ai_tipi TEXT,
                denetci TEXT,
                genel_sonuc TEXT,
                karar TEXT,
                kanit_id TEXT,
                ceza_riski TEXT,
                json_veri TEXT,
                firma_id INTEGER
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS zamanlanmis_denetimler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                musteri TEXT NOT NULL,
                eposta TEXT,
                dil TEXT DEFAULT 'tr',
                ai_tipi TEXT NOT NULL,
                url TEXT,
                ek_bilgi TEXT,
                siklik TEXT DEFAULT 'haftalik',
                son_calisma TEXT,
                sonraki_calisma TEXT,
                aktif INTEGER DEFAULT 1,
                olusturma TEXT,
                firma_id INTEGER
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS api_anahtarlari (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                musteri TEXT NOT NULL,
                anahtar TEXT UNIQUE NOT NULL,
                aktif INTEGER DEFAULT 1,
                olusturma TEXT,
                son_kullanim TEXT,
                toplam_istek INTEGER DEFAULT 0
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS webhook_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                anahtar TEXT,
                musteri TEXT,
                ai_tipi TEXT,
                durum TEXT,
                ip_adresi TEXT,
                tarih TEXT,
                json_veri TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS firma (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                firma_adi TEXT NOT NULL,
                vergi_no TEXT,
                sektor TEXT,
                adres TEXT,
                telefon TEXT,
                eposta TEXT,
                aktif INTEGER DEFAULT 1,
                olusturma TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kullanici_adi TEXT UNIQUE NOT NULL,
                sifre_hash TEXT NOT NULL,
                ad_soyad TEXT,
                eposta TEXT,
                rol TEXT DEFAULT 'user',
                firma_id INTEGER,
                firma_rol TEXT DEFAULT 'user',
                aktif INTEGER DEFAULT 1,
                olusturma TEXT,
                son_giris TEXT,
                totp_secret TEXT,
                totp_aktif INTEGER DEFAULT 0,
                plan TEXT DEFAULT 'free',
                trial_baslangic TEXT,
                trial_bitis TEXT,
                email_dogrulandi INTEGER DEFAULT 0,
                FOREIGN KEY (firma_id) REFERENCES firma(id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kullanici_adi TEXT,
                firma_id INTEGER,
                eylem TEXT NOT NULL,
                detay TEXT,
                ip_adresi TEXT,
                tarih TEXT NOT NULL,
                basarili INTEGER DEFAULT 1
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_audit_tarih ON audit_log(tarih DESC)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_audit_kullanici ON audit_log(kullanici_adi)
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS token (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kullanici_adi TEXT NOT NULL,
                eposta TEXT NOT NULL,
                token TEXT UNIQUE NOT NULL,
                tip TEXT NOT NULL,
                durum TEXT DEFAULT 'bekliyor',
                olusturma TEXT,
                son_kullanma TEXT,
                kullanildi TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS davet (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                firma_id INTEGER NOT NULL,
                eposta TEXT NOT NULL,
                rol TEXT DEFAULT 'user',
                token TEXT UNIQUE NOT NULL,
                durum TEXT DEFAULT 'bekliyor',
                gonderen TEXT,
                olusturma TEXT,
                kabul_tarih TEXT,
                FOREIGN KEY (firma_id) REFERENCES firma(id)
            )
        """)
        conn.commit()

        # ============================================================
        # OTOMATIK MIGRATION - Eksik sutunlari ekle (Streamlit Cloud icin)
        # ============================================================
        _mevcut_users = [r[1] for r in conn.execute("PRAGMA table_info(users)").fetchall()]
        _yeni_sutunlar = [
            ("plan", "TEXT DEFAULT 'free'"),
            ("trial_baslangic", "TEXT"),
            ("trial_bitis", "TEXT"),
            ("email_dogrulandi", "INTEGER DEFAULT 0"),
        ]
        for _isim, _tip in _yeni_sutunlar:
            if _isim not in _mevcut_users:
                try:
                    conn.execute(f"ALTER TABLE users ADD COLUMN {_isim} {_tip}")
                    print(f"[db migration] users.{_isim} eklendi")
                except Exception as _e:
                    print(f"[db migration] {_isim} hatasi: {_e}")
        conn.commit()


# ============================================================
# 2FA FONKSIYONLARI
# ============================================================
def totp_secret_guncelle(kullanici_adi, secret):
    """Kullanicinin TOTP secret'ini kaydeder."""
    with _baglanti() as conn:
        conn.execute(
            "UPDATE users SET totp_secret = ? WHERE kullanici_adi = ?",
            (secret, kullanici_adi)
        )
        conn.commit()


def totp_aktiflestir(kullanici_adi):
    """2FA'yi aktiflestirir."""
    with _baglanti() as conn:
        conn.execute(
            "UPDATE users SET totp_aktif = 1 WHERE kullanici_adi = ?",
            (kullanici_adi,)
        )
        conn.commit()


def totp_devre_disi_birak(kullanici_adi):
    """2FA'yi devre disi birakir."""
    with _baglanti() as conn:
        conn.execute(
            "UPDATE users SET totp_aktif = 0, totp_secret = NULL WHERE kullanici_adi = ?",
            (kullanici_adi,)
        )
        conn.commit()


def totp_bilgisi(kullanici_adi):
    """Kullanicinin 2FA bilgilerini dondurur."""
    with _baglanti() as conn:
        cur = conn.execute(
            "SELECT totp_secret, totp_aktif FROM users WHERE kullanici_adi = ?",
            (kullanici_adi,)
        )
        row = cur.fetchone()
        if row:
            return {
                "totp_secret": row["totp_secret"],
                "totp_aktif": bool(row["totp_aktif"]),
            }
        return {"totp_secret": None, "totp_aktif": False}


# ============================================================
# FIRMA FONKSIYONLARI
# ============================================================
def firma_ekle(firma_adi, vergi_no="", sektor="", adres="", telefon="", eposta=""):
    """Yeni firma ekler ve ID dondurur."""
    from datetime import datetime
    with _baglanti() as conn:
        cur = conn.execute("""
            INSERT INTO firma (firma_adi, vergi_no, sektor, adres, telefon, eposta, aktif, olusturma)
            VALUES (?, ?, ?, ?, ?, ?, 1, ?)
        """, (
            firma_adi, vergi_no, sektor, adres, telefon, eposta,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ))
        conn.commit()
        return cur.lastrowid


def firma_bul(firma_id):
    """Firma ID'ye gore firma dondurur."""
    with _baglanti() as conn:
        cur = conn.execute("SELECT * FROM firma WHERE id = ?", (firma_id,))
        row = cur.fetchone()
        return dict(row) if row else None


def firma_listele(aktif_only=True):
    """Tum firmalari listeler."""
    sql = "SELECT * FROM firma"
    if aktif_only:
        sql += " WHERE aktif = 1"
    sql += " ORDER BY firma_adi ASC"
    with _baglanti() as conn:
        cur = conn.execute(sql)
        return [dict(row) for row in cur.fetchall()]


def firma_kullanicilari(firma_id):
    """Bir firmanin kullanicilarini listeler."""
    with _baglanti() as conn:
        cur = conn.execute("""
            SELECT id, kullanici_adi, ad_soyad, eposta, firma_rol, aktif, olusturma, son_giris
            FROM users WHERE firma_id = ?
            ORDER BY olusturma ASC
        """, (firma_id,))
        return [dict(row) for row in cur.fetchall()]


def firma_sil(firma_id):
    """Firmayi siler."""
    with _baglanti() as conn:
        conn.execute("DELETE FROM firma WHERE id = ?", (firma_id,))
        conn.commit()


# ============================================================
# KULLANICI GUNCELLEME (firma_id ile)
# ============================================================
def kullanici_ekle_firma(kullanici_adi, sifre_hash, ad_soyad, eposta, firma_id, firma_rol="user", rol="user"):
    """Firma ile birlikte kullanici ekler."""
    from datetime import datetime
    with _baglanti() as conn:
        try:
            conn.execute("""
                INSERT INTO users
                (kullanici_adi, sifre_hash, ad_soyad, eposta, rol, firma_id, firma_rol, aktif, olusturma)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?)
            """, (
                kullanici_adi, sifre_hash, ad_soyad, eposta, rol,
                firma_id, firma_rol,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False


# ============================================================
# AYLIK ISTATISTIK
# ============================================================
def aylik_istatistik(firma_id=None, yil=None, ay=None):
    """
    Belirtilen ay icin istatistik dondurur.

    Args:
        firma_id: Firma ID (None ise tum firmalar)
        yil: Yil (None ise bu yil)
        ay: Ay (None ise bu ay)

    Returns:
        dict: Aylik istatistikler
    """
    from datetime import datetime

    if yil is None:
        yil = datetime.now().year
    if ay is None:
        ay = datetime.now().month

    # Ay baslangic ve bitis
    baslangic = f"{yil:04d}-{ay:02d}-01 00:00:00"
    if ay == 12:
        bitis = f"{yil+1:04d}-01-01 00:00:00"
    else:
        bitis = f"{yil:04d}-{ay+1:02d}-01 00:00:00"

    with _baglanti() as conn:
        # Firma filtresi
        if firma_id is not None:
            firma_where = " AND firma_id = ?"
            firma_params = (firma_id,)
        else:
            firma_where = ""
            firma_params = ()

        # Toplam denetim
        toplam = conn.execute(
            f"""SELECT COUNT(*) as n FROM denetimler
                WHERE tarih >= ? AND tarih < ? {firma_where}""",
            (baslangic, bitis) + firma_params,
        ).fetchone()["n"]

        # Uyumlu
        uyumlu = conn.execute(
            f"""SELECT COUNT(*) as n FROM denetimler
                WHERE tarih >= ? AND tarih < ? AND genel_sonuc = 'UYUMLU' {firma_where}""",
            (baslangic, bitis) + firma_params,
        ).fetchone()["n"]

        # Uyumsuz
        uyumsuz = conn.execute(
            f"""SELECT COUNT(*) as n FROM denetimler
                WHERE tarih >= ? AND tarih < ? AND genel_sonuc = 'UYUMSUZ' {firma_where}""",
            (baslangic, bitis) + firma_params,
        ).fetchone()["n"]

        # AI tipi dagilimi
        tip_dagilimi = conn.execute(
            f"""SELECT ai_tipi, COUNT(*) as n FROM denetimler
                WHERE tarih >= ? AND tarih < ? {firma_where}
                GROUP BY ai_tipi ORDER BY n DESC""",
            (baslangic, bitis) + firma_params,
        ).fetchall()

        return {
            "yil": yil,
            "ay": ay,
            "toplam": toplam,
            "uyumlu": uyumlu,
            "uyumsuz": uyumsuz,
            "uyum_orani": round(100 * uyumlu / toplam, 1) if toplam else 0,
            "tip_dagilimi": [dict(r) for r in tip_dagilimi],
        }


def aylik_rapor_gonderilecekler():
    """
    Aylik rapor gonderilecek firmalari dondurur.
    Aktif firmalar (denetimi olanlar).
    """
    with _baglanti() as conn:
        cur = conn.execute("""
            SELECT DISTINCT f.id, f.firma_adi, f.eposta
            FROM firma f
            INNER JOIN denetimler d ON d.firma_id = f.id
            WHERE f.aktif = 1 AND f.eposta IS NOT NULL AND f.eposta != ''
        """)
        return [dict(row) for row in cur.fetchall()]


# ============================================================
# AUDIT LOG FONKSIYONLARI
# ============================================================
def audit_kaydet(eylem, kullanici_adi=None, firma_id=None, detay=None, ip_adresi=None, basarili=True):
    """
    Audit log kaydi ekler.

    Args:
        eylem: "giris", "denetim", "kaydet", "sil" vb.
        kullanici_adi: Islem yapan kullanici
        firma_id: Firma ID
        detay: Ek bilgi (JSON string veya metin)
        ip_adresi: Istemci IP
        basarili: Islem basarili mi?
    """
    from datetime import datetime
    with _baglanti() as conn:
        conn.execute("""
            INSERT INTO audit_log
            (kullanici_adi, firma_id, eylem, detay, ip_adresi, tarih, basarili)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            kullanici_adi, firma_id, eylem, detay, ip_adresi,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            1 if basarili else 0,
        ))
        conn.commit()


def audit_listele(limit=100, kullanici_adi=None, firma_id=None, eylem=None):
    """Audit log kayitlarini listeler."""
    sql = "SELECT * FROM audit_log WHERE 1=1"
    params = []

    if kullanici_adi:
        sql += " AND kullanici_adi = ?"
        params.append(kullanici_adi)
    if firma_id is not None:
        sql += " AND firma_id = ?"
        params.append(firma_id)
    if eylem:
        sql += " AND eylem = ?"
        params.append(eylem)

    sql += " ORDER BY tarih DESC LIMIT ?"
    params.append(limit)

    with _baglanti() as conn:
        cur = conn.execute(sql, params)
        return [dict(row) for row in cur.fetchall()]


def audit_istatistik(firma_id=None):
    """Audit log istatistigi."""
    with _baglanti() as conn:
        if firma_id is not None:
            toplam = conn.execute(
                "SELECT COUNT(*) as n FROM audit_log WHERE firma_id = ?", (firma_id,)
            ).fetchone()["n"]
        else:
            toplam = conn.execute("SELECT COUNT(*) as n FROM audit_log").fetchone()["n"]

        return {"toplam": toplam}


def audit_temizle(gun=90):
    """Eski audit log kayitlarini siler (varsayilan: 90 gun)."""
    from datetime import datetime, timedelta
    esik = (datetime.now() - timedelta(days=gun)).strftime("%Y-%m-%d %H:%M:%S")

    with _baglanti() as conn:
        cur = conn.execute("DELETE FROM audit_log WHERE tarih < ?", (esik,))
        conn.commit()
        return cur.rowcount


# ============================================================
# TOKEN FONKSIYONLARI (sifre sifirlama + email dogrulama)
# ============================================================
def token_olustur(kullanici_adi, eposta, tip, sure_saat=24):
    """
    Yeni token olusturur.
    tip: 'sifre_sifirlama' | 'email_dogrulama'
    """
    import secrets
    from datetime import datetime, timedelta

    token = secrets.token_urlsafe(32)
    son_kullanma = datetime.now() + timedelta(hours=sure_saat)

    with _baglanti() as conn:
        # Ayni tip icin eski bekleyen tokenlari iptal et
        conn.execute("""
            UPDATE token SET durum = 'iptal'
            WHERE kullanici_adi = ? AND tip = ? AND durum = 'bekliyor'
        """, (kullanici_adi, tip))

        conn.execute("""
            INSERT INTO token
            (kullanici_adi, eposta, token, tip, durum, olusturma, son_kullanma)
            VALUES (?, ?, ?, ?, 'bekliyor', ?, ?)
        """, (
            kullanici_adi, eposta, token, tip,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            son_kullanma.strftime("%Y-%m-%d %H:%M:%S"),
        ))
        conn.commit()
        return token


def token_bul(token_str, tip=None):
    """Token'i bulur ve gecerliligi kontrol eder."""
    from datetime import datetime

    with _baglanti() as conn:
        if tip:
            cur = conn.execute("""
                SELECT * FROM token
                WHERE token = ? AND tip = ? AND durum = 'bekliyor'
            """, (token_str, tip))
        else:
            cur = conn.execute("""
                SELECT * FROM token
                WHERE token = ? AND durum = 'bekliyor'
            """, (token_str,))

        row = cur.fetchone()
        if not row:
            return None

        # Suresi dolmus mu?
        son_kullanma = row["son_kullanma"]
        if son_kullanma:
            simdi = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if simdi > son_kullanma:
                # Suresi dolmus, iptal et
                conn.execute("UPDATE token SET durum = 'suresi_doldu' WHERE id = ?", (row["id"],))
                conn.commit()
                return None

        return dict(row)


def token_kullanildi(token_str):
    """Token'i kullanildi olarak isaretler."""
    from datetime import datetime
    with _baglanti() as conn:
        conn.execute("""
            UPDATE token SET durum = 'kullanildi', kullanildi = ?
            WHERE token = ?
        """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), token_str))
        conn.commit()


def token_listele(kullanici_adi=None):
    """Tokenlari listeler."""
    with _baglanti() as conn:
        if kullanici_adi:
            cur = conn.execute("""
                SELECT * FROM token WHERE kullanici_adi = ?
                ORDER BY olusturma DESC LIMIT 50
            """, (kullanici_adi,))
        else:
            cur = conn.execute("SELECT * FROM token ORDER BY olusturma DESC LIMIT 50")
        return [dict(row) for row in cur.fetchall()]


def sifre_guncelle(kullanici_adi, yeni_sifre_hash):
    """Kullanici sifresini gunceller."""
    with _baglanti() as conn:
        conn.execute(
            "UPDATE users SET sifre_hash = ? WHERE kullanici_adi = ?",
            (yeni_sifre_hash, kullanici_adi)
        )
        conn.commit()


def kullanici_dogrula(kullanici_adi):
    """Email dogrulamasini tamamlar."""
    with _baglanti() as conn:
        conn.execute(
            "UPDATE users SET aktif = 1 WHERE kullanici_adi = ?",
            (kullanici_adi,)
        )
        conn.commit()


# ============================================================
# DAVET FONKSIYONLARI
# ============================================================
def davet_olustur(firma_id, eposta, rol="user", gonderen=""):
    """Yeni davet olusturur."""
    import secrets
    from datetime import datetime

    token = secrets.token_urlsafe(24)

    with _baglanti() as conn:
        # Ayni eposta icin bekleyen davet var mi?
        cur = conn.execute("""
            SELECT id FROM davet
            WHERE firma_id = ? AND eposta = ? AND durum = 'bekliyor'
        """, (firma_id, eposta))
        if cur.fetchone():
            return None  # Zaten bekleyen davet var

        conn.execute("""
            INSERT INTO davet (firma_id, eposta, rol, token, durum, gonderen, olusturma)
            VALUES (?, ?, ?, ?, 'bekliyor', ?, ?)
        """, (
            firma_id, eposta, rol, token, gonderen,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ))
        conn.commit()
        return token


def davet_bul(token):
    """Token ile davet dondurur."""
    with _baglanti() as conn:
        cur = conn.execute("""
            SELECT d.*, f.firma_adi
            FROM davet d
            JOIN firma f ON d.firma_id = f.id
            WHERE d.token = ? AND d.durum = 'bekliyor'
        """, (token,))
        row = cur.fetchone()
        return dict(row) if row else None


def davet_listele(firma_id):
    """Bir firmanin davetlerini listeler."""
    with _baglanti() as conn:
        cur = conn.execute("""
            SELECT * FROM davet WHERE firma_id = ?
            ORDER BY olusturma DESC
        """, (firma_id,))
        return [dict(row) for row in cur.fetchall()]


def davet_kabul_et(token):
    """Daveti kabul edildi olarak isaretler."""
    from datetime import datetime
    with _baglanti() as conn:
        conn.execute("""
            UPDATE davet
            SET durum = 'kabul_edildi', kabul_tarih = ?
            WHERE token = ?
        """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), token))
        conn.commit()


def davet_iptal_et(davet_id):
    """Daveti iptal eder."""
    with _baglanti() as conn:
        conn.execute("DELETE FROM davet WHERE id = ?", (davet_id,))
        conn.commit()


def kullanici_ekle(kullanici_adi, sifre_hash, ad_soyad="", eposta="", rol="user"):
    """Yeni kullanici ekler."""
    from datetime import datetime
    with _baglanti() as conn:
        try:
            conn.execute("""
                INSERT INTO users
                (kullanici_adi, sifre_hash, ad_soyad, eposta, rol, aktif, olusturma)
                VALUES (?, ?, ?, ?, ?, 1, ?)
            """, (
                kullanici_adi, sifre_hash, ad_soyad, eposta, rol,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False


def kullanici_bul(kullanici_adi):
    """Kullanici adina gore kullanici dondurur."""
    with _baglanti() as conn:
        cur = conn.execute(
            "SELECT * FROM users WHERE kullanici_adi = ? AND aktif = 1",
            (kullanici_adi,)
        )
        row = cur.fetchone()
        return dict(row) if row else None


def kullanici_giris_guncelle(kullanici_adi):
    """Son giris zamanini gunceller."""
    from datetime import datetime
    with _baglanti() as conn:
        conn.execute(
            "UPDATE users SET son_giris = ? WHERE kullanici_adi = ?",
            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), kullanici_adi)
        )
        conn.commit()


def kullanicilari_listele():
    """Tum kullanicilari listeler."""
    with _baglanti() as conn:
        cur = conn.execute("SELECT id, kullanici_adi, ad_soyad, eposta, rol, firma_id, firma_rol, aktif, olusturma, son_giris, plan, trial_baslangic, trial_bitis FROM users ORDER BY olusturma DESC")
        return [dict(row) for row in cur.fetchall()]


def kullanici_sil(kullanici_adi):
    """Kullaniciyi siler."""
    with _baglanti() as conn:
        conn.execute("DELETE FROM users WHERE kullanici_adi = ?", (kullanici_adi,))
        conn.commit()


def api_anahtari_olustur(musteri):
    """Yeni API anahtari olusturur."""
    import secrets
    from datetime import datetime

    anahtar = "aiuk_" + secrets.token_urlsafe(32)

    with _baglanti() as conn:
        conn.execute("""
            INSERT INTO api_anahtarlari (musteri, anahtar, aktif, olusturma)
            VALUES (?, ?, 1, ?)
        """, (musteri, anahtar, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()

    return anahtar


def api_anahtari_dogrula(anahtar):
    """API anahtarini dogrular ve musteri bilgisi dondurur."""
    if not anahtar:
        return None

    with _baglanti() as conn:
        cur = conn.execute("""
            SELECT * FROM api_anahtarlari
            WHERE anahtar = ? AND aktif = 1
        """, (anahtar,))
        row = cur.fetchone()
        if not row:
            return None

        # Son kullanim ve toplam istek guncelle
        from datetime import datetime
        conn.execute("""
            UPDATE api_anahtarlari
            SET son_kullanim = ?, toplam_istek = toplam_istek + 1
            WHERE anahtar = ?
        """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), anahtar))
        conn.commit()

        return dict(row)


def api_anahtarlari_listele(aktif_only=True):
    """API anahtarlarini listeler."""
    sql = "SELECT * FROM api_anahtarlari"
    if aktif_only:
        sql += " WHERE aktif = 1"
    sql += " ORDER BY olusturma DESC"
    with _baglanti() as conn:
        cur = conn.execute(sql)
        return [dict(row) for row in cur.fetchall()]


def api_anahtari_sil(anahtar):
    """API anahtarini siler."""
    with _baglanti() as conn:
        conn.execute("DELETE FROM api_anahtarlari WHERE anahtar = ?", (anahtar,))
        conn.commit()


def webhook_log_ekle(anahtar, musteri, ai_tipi, durum, ip_adresi, json_veri=None):
    """Webhook log kaydi ekler."""
    import json as _json
    from datetime import datetime

    with _baglanti() as conn:
        conn.execute("""
            INSERT INTO webhook_log
            (anahtar, musteri, ai_tipi, durum, ip_adresi, tarih, json_veri)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            anahtar, musteri, ai_tipi, durum, ip_adresi,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            _json.dumps(json_veri, ensure_ascii=False) if json_veri else None,
        ))
        conn.commit()


def webhook_log_listele(limit=100):
    """Webhook loglarini listeler."""
    with _baglanti() as conn:
        cur = conn.execute("""
            SELECT * FROM webhook_log
            ORDER BY tarih DESC
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in cur.fetchall()]


def zamanlanmis_ekle(musteri, ai_tipi, url="", ek_bilgi=None, siklik="haftalik", eposta="", dil="tr", firma_id=None):
    """Yeni zamanlanmis denetim ekler."""
    import json as _json
    from datetime import datetime, timedelta

    simdi = datetime.now()
    if siklik == "gunluk":
        sonraki = simdi + timedelta(days=1)
    elif siklik == "haftalik":
        sonraki = simdi + timedelta(days=7)
    elif siklik == "aylik":
        sonraki = simdi + timedelta(days=30)
    else:
        sonraki = simdi + timedelta(days=7)

    with _baglanti() as conn:
        conn.execute("""
            INSERT INTO zamanlanmis_denetimler
            (musteri, eposta, dil, ai_tipi, url, ek_bilgi, siklik, sonraki_calisma, aktif, olusturma, firma_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
        """, (
            musteri, eposta, dil, ai_tipi, url,
            _json.dumps(ek_bilgi or {}, ensure_ascii=False),
            siklik, sonraki.strftime("%Y-%m-%d %H:%M:%S"),
            simdi.strftime("%Y-%m-%d %H:%M:%S"),
            firma_id,
        ))
        conn.commit()
        return True


def zamanlanmis_listele(aktif_only=True):
    """Zamanlanmis denetimleri listeler."""
    sql = "SELECT * FROM zamanlanmis_denetimler"
    if aktif_only:
        sql += " WHERE aktif = 1"
    sql += " ORDER BY sonraki_calisma ASC"
    with _baglanti() as conn:
        cur = conn.execute(sql)
        return [dict(row) for row in cur.fetchall()]


def zamanlanmis_sil(id):
    """Zamanlanmis denetimi siler."""
    with _baglanti() as conn:
        conn.execute("DELETE FROM zamanlanmis_denetimler WHERE id = ?", (id,))
        conn.commit()


def zamanlanmis_guncelle_son_calisma(id):
    """Son calisma zamanini gunceller ve sonraki calismayi hesaplar."""
    from datetime import datetime, timedelta
    simdi = datetime.now()

    with _baglanti() as conn:
        cur = conn.execute(
            "SELECT siklik FROM zamanlanmis_denetimler WHERE id = ?", (id,)
        )
        row = cur.fetchone()
        if not row:
            return False
        siklik = row["siklik"]

        if siklik == "gunluk":
            sonraki = simdi + timedelta(days=1)
        elif siklik == "haftalik":
            sonraki = simdi + timedelta(days=7)
        elif siklik == "aylik":
            sonraki = simdi + timedelta(days=30)
        else:
            sonraki = simdi + timedelta(days=7)

        conn.execute("""
            UPDATE zamanlanmis_denetimler
            SET son_calisma = ?, sonraki_calisma = ?
            WHERE id = ?
        """, (
            simdi.strftime("%Y-%m-%d %H:%M:%S"),
            sonraki.strftime("%Y-%m-%d %H:%M:%S"),
            id,
        ))
        conn.commit()
        return True


def zamanlanmis_bekleyenler():
    """
    Calisma zamani gelmis denetimleri dondurur.
    Ayrica hic calismamis (son_calisma NULL) kayitlari da dahil eder.
    """
    from datetime import datetime
    simdi = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with _baglanti() as conn:
        cur = conn.execute("""
            SELECT * FROM zamanlanmis_denetimler
            WHERE aktif = 1 AND (
                son_calisma IS NULL
                OR sonraki_calisma IS NULL
                OR sonraki_calisma <= ?
            )
            ORDER BY sonraki_calisma ASC
        """, (simdi,))
        return [dict(row) for row in cur.fetchall()]


def kaydet(rapor_no, modul, musteri="", sektor="", ai_tipi="", denetci="",
           genel_sonuc="", karar="", kanit_id="", ceza_riski="", json_veri=None,
           firma_id=None):
    """Yeni denetim kaydi ekler. Ayni rapor_no varsa gunceller."""
    tarih = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    json_str = json.dumps(json_veri, ensure_ascii=False) if json_veri else None

    with _baglanti() as conn:
        try:
            conn.execute("""
                INSERT INTO denetimler
                (rapor_no, tarih, modul, musteri, sektor, ai_tipi, denetci,
                 genel_sonuc, karar, kanit_id, ceza_riski, json_veri, firma_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (rapor_no, tarih, modul, musteri, sektor, ai_tipi, denetci,
                  genel_sonuc, karar, kanit_id, ceza_riski, json_str, firma_id))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Ayni rapor_no zaten var - guncelle
            conn.execute("""
                UPDATE denetimler SET
                    tarih = ?, modul = ?, musteri = ?, sektor = ?, ai_tipi = ?,
                    denetci = ?, genel_sonuc = ?, karar = ?, kanit_id = ?,
                    ceza_riski = ?, json_veri = ?
                WHERE rapor_no = ?
            """, (tarih, modul, musteri, sektor, ai_tipi, denetci,
                  genel_sonuc, karar, kanit_id, ceza_riski, json_str, rapor_no))
            conn.commit()
            return True
        except Exception as e:
            print(f"DB kayit hatasi: {e}")
            return False


def listele(limit=None, filtre_musteri=None, filtre_ai_tipi=None, filtre_sonuc=None,
            filtre_tarih_bas=None, filtre_tarih_son=None, filtre_firma_id=None):
    """Kayitlari listeler."""
    sql = "SELECT * FROM denetimler WHERE 1=1"
    params = []

    if filtre_firma_id is not None:
        sql += " AND firma_id = ?"
        params.append(filtre_firma_id)

    if filtre_musteri:
        sql += " AND musteri LIKE ?"
        params.append(f"%{filtre_musteri}%")
    if filtre_ai_tipi:
        sql += " AND ai_tipi = ?"
        params.append(filtre_ai_tipi)
    if filtre_sonuc:
        sql += " AND genel_sonuc = ?"
        params.append(filtre_sonuc)
    if filtre_tarih_bas:
        sql += " AND tarih >= ?"
        params.append(filtre_tarih_bas + " 00:00:00")
    if filtre_tarih_son:
        sql += " AND tarih <= ?"
        params.append(filtre_tarih_son + " 23:59:59")

    sql += " ORDER BY tarih DESC"

    if limit:
        sql += " LIMIT ?"
        params.append(limit)

    with _baglanti() as conn:
        cur = conn.execute(sql, params)
        return [dict(row) for row in cur.fetchall()]


def sil(rapor_no):
    """Bir kaydi siler."""
    with _baglanti() as conn:
        conn.execute("DELETE FROM denetimler WHERE rapor_no = ?", (rapor_no,))
        conn.commit()


def toplam_sayisi():
    """Toplam kayit sayisini dondurur."""
    with _baglanti() as conn:
        cur = conn.execute("SELECT COUNT(*) as n FROM denetimler")
        return cur.fetchone()["n"]


def istatistik(firma_id=None):
    """Genel istatistik dondurur."""
    with _baglanti() as conn:
        if firma_id is not None:
            where = "WHERE firma_id = ?"
            params = (firma_id,)
        else:
            where = ""
            params = ()

        toplam = conn.execute(f"SELECT COUNT(*) as n FROM denetimler {where}", params).fetchone()["n"]

        if firma_id is not None:
            uyumlu = conn.execute("SELECT COUNT(*) as n FROM denetimler WHERE genel_sonuc='UYUMLU' AND firma_id = ?", params).fetchone()["n"]
            uyumsuz = conn.execute("SELECT COUNT(*) as n FROM denetimler WHERE genel_sonuc='UYUMSUZ' AND firma_id = ?", params).fetchone()["n"]
        else:
            uyumlu = conn.execute("SELECT COUNT(*) as n FROM denetimler WHERE genel_sonuc='UYUMLU'").fetchone()["n"]
            uyumsuz = conn.execute("SELECT COUNT(*) as n FROM denetimler WHERE genel_sonuc='UYUMSUZ'").fetchone()["n"]

        return {
            "toplam": toplam,
            "uyumlu": uyumlu,
            "uyumsuz": uyumsuz,
            "diger": toplam - uyumlu - uyumsuz,
        }


# ============================================================
# TRIAL / PLAN YONETIMI
# ============================================================
TRIAL_GUN = 7  # Kac gun ucretsiz deneme


def trial_baslat(kullanici_adi, gun=TRIAL_GUN):
    """
    Kullaniciya ucretsiz deneme baslatir.
    Zaten baslatilmissa uzerine yazmaz.
    """
    kullanici = kullanici_bul(kullanici_adi)
    if not kullanici:
        return {"durum": "HATA", "mesaj": "Kullanici bulunamadi"}

    if kullanici.get("trial_baslangic"):
        return {"durum": "ZATEN", "mesaj": "Trial zaten aktif"}

    simdi = datetime.now()
    baslangic = simdi.strftime("%Y-%m-%d %H:%M:%S")
    bitis = (simdi + timedelta(days=gun)).strftime("%Y-%m-%d %H:%M:%S")

    with _baglanti() as conn:
        conn.execute("""
            UPDATE users
            SET trial_baslangic = ?, trial_bitis = ?, plan = 'trial'
            WHERE kullanici_adi = ?
        """, (baslangic, bitis, kullanici_adi))
        conn.commit()

    return {
        "durum": "OK",
        "baslangic": baslangic,
        "bitis": bitis,
        "gun": gun,
    }


def trial_durum(kullanici_adi):
    """
    Trial durumunu dondurur.
    Donus: {
        durum: 'YOK' | 'AKTIF' | 'SURESI_DOLDU',
        plan, baslangic, bitis, kalan_gun, kalan_saat
    }
    """
    kullanici = kullanici_bul(kullanici_adi)
    if not kullanici:
        return {"durum": "YOK"}

    plan = kullanici.get("plan") or "free"

    # Plan trial degilse YOK don (pro/enterprise/free)
    if plan != "trial":
        return {"durum": "YOK", "plan": plan}

    baslangic = kullanici.get("trial_baslangic")
    bitis = kullanici.get("trial_bitis")

    if not baslangic or not bitis:
        return {"durum": "YOK", "plan": plan}

    try:
        bitis_dt = datetime.strptime(bitis, "%Y-%m-%d %H:%M:%S")
    except Exception:
        return {"durum": "YOK", "plan": plan}

    simdi = datetime.now()
    kalan = bitis_dt - simdi

    if kalan.total_seconds() <= 0:
        return {
            "durum": "SURESI_DOLDU",
            "plan": plan,
            "baslangic": baslangic,
            "bitis": bitis,
            "kalan_gun": 0,
            "kalan_saat": 0,
        }

    return {
        "durum": "AKTIF",
        "plan": plan,
        "baslangic": baslangic,
        "bitis": bitis,
        "kalan_gun": kalan.days,
        "kalan_saat": int(kalan.total_seconds() // 3600),
    }


def plan_guncelle(kullanici_adi, yeni_plan):
    """Kullanicinin planini gunceller (free/trial/pro/enterprise)."""
    gecerli = {"free", "trial", "pro", "enterprise"}
    if yeni_plan not in gecerli:
        return {"durum": "HATA", "mesaj": f"Gecersiz plan: {yeni_plan}"}

    with _baglanti() as conn:
        conn.execute(
            "UPDATE users SET plan = ? WHERE kullanici_adi = ?",
            (yeni_plan, kullanici_adi),
        )
        conn.commit()

    return {"durum": "OK", "plan": yeni_plan}


def plan_dagilimi():
    """Plan bazli kullanici sayisini dondurur."""
    with _baglanti() as conn:
        satirlar = conn.execute("""
            SELECT COALESCE(plan, 'free') as p, COUNT(*) as n
            FROM users
            WHERE aktif = 1
            GROUP BY p
        """).fetchall()
    return {r["p"]: r["n"] for r in satirlar}


# ============================================================
# PLAN LIMITLERI
# ============================================================
# Aylik denetim limitleri (0 = sinirsiz)
PLAN_LIMITLERI = {
    "free":       3,
    "trial":      10,
    "pro":        100,
    "enterprise": 0,   # sinirsiz
}

PLAN_ADLARI = {
    "free":       "Ucretsiz",
    "trial":      "Deneme",
    "pro":        "Pro",
    "enterprise": "Kurumsal",
}


def plan_limitleri(plan=None):
    """Plan limitlerini dondurur."""
    if plan is None:
        return PLAN_LIMITLERI.copy()
    return PLAN_LIMITLERI.get(plan, PLAN_LIMITLERI["free"])


def bu_ay_denetim_sayisi(firma_id):
    """Firmanin bu ay yaptigi denetim sayisini dondurur."""
    simdi = datetime.now()
    ay_bas = simdi.strftime("%Y-%m-01 00:00:00")

    with _baglanti() as conn:
        cur = conn.execute("""
            SELECT COUNT(*) as n FROM denetimler
            WHERE firma_id = ?
            AND tarih >= ?
            AND modul IN ('Tek Denetim', 'Toplu Denetim')
        """, (firma_id, ay_bas))
        return cur.fetchone()["n"]


def limit_kontrol(kullanici_adi):
    """
    Kullanicinin plan limitini kontrol eder.
    Donus: {
        durum: 'OK' | 'LIMIT_DOLDU' | 'PLAN_YOK' | 'TRIAL_BITTI',
        plan, plan_adi, kullanilan, limit, kalan, mesaj
    }
    """
    kullanici = kullanici_bul(kullanici_adi)
    if not kullanici:
        return {"durum": "PLAN_YOK", "mesaj": "Kullanici bulunamadi"}

    plan = kullanici.get("plan") or "free"
    firma_id = kullanici.get("firma_id")

    # Trial kontrolu
    if plan == "trial":
        trial = trial_durum(kullanici_adi)
        if trial.get("durum") == "SURESI_DOLDU":
            return {
                "durum": "TRIAL_BITTI",
                "plan": plan,
                "plan_adi": PLAN_ADLARI.get(plan, plan),
                "kullanilan": 0,
                "limit": 0,
                "kalan": 0,
                "mesaj": "Deneme sureniz doldu. Lutfen plan yukseltin.",
            }

    if not firma_id:
        return {
            "durum": "PLAN_YOK",
            "plan": plan,
            "plan_adi": PLAN_ADLARI.get(plan, plan),
            "mesaj": "Firma atanmamis",
        }

    limit = PLAN_LIMITLERI.get(plan, PLAN_LIMITLERI["free"])
    kullanilan = bu_ay_denetim_sayisi(firma_id)

    # Sinirsiz plan
    if limit == 0:
        return {
            "durum": "OK",
            "plan": plan,
            "plan_adi": PLAN_ADLARI.get(plan, plan),
            "kullanilan": kullanilan,
            "limit": 0,
            "kalan": -1,  # sinirsiz
            "mesaj": "Sinirsiz plan",
        }

    kalan = max(0, limit - kullanilan)

    if kullanilan >= limit:
        return {
            "durum": "LIMIT_DOLDU",
            "plan": plan,
            "plan_adi": PLAN_ADLARI.get(plan, plan),
            "kullanilan": kullanilan,
            "limit": limit,
            "kalan": 0,
            "mesaj": f"Aylik limit doldu ({kullanilan}/{limit})",
        }

    return {
        "durum": "OK",
        "plan": plan,
        "plan_adi": PLAN_ADLARI.get(plan, plan),
        "kullanilan": kullanilan,
        "limit": limit,
        "kalan": kalan,
        "mesaj": f"{kalan} denetim hakkiniz kaldi",
    }


# ============================================================
# YUKSELTME TALEPLERI
# ============================================================
def yukseltme_talep_ekle(kullanici_adi, istenen_plan, odeme_yontemi="",
                         fatura_bilgi="", notlar=""):
    """
    Kullanicinin plan yukseltme talebini kaydeder.
    """
    kullanici = kullanici_bul(kullanici_adi)
    if not kullanici:
        return {"durum": "HATA", "mesaj": "Kullanici bulunamadi"}

    firma_id = kullanici.get("firma_id")
    firma_adi = ""
    if firma_id:
        f = firma_bul(firma_id)
        if f:
            firma_adi = f.get("firma_adi", "")

    simdi = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with _baglanti() as conn:
        cur = conn.execute("""
            INSERT INTO yukseltme_talepleri
            (kullanici_adi, firma_id, firma_adi, eposta,
             mevcut_plan, istenen_plan, odeme_yontemi, fatura_bilgi,
             notlar, durum, olusturma)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'bekliyor', ?)
        """, (
            kullanici_adi,
            firma_id,
            firma_adi,
            kullanici.get("eposta", ""),
            kullanici.get("plan") or "free",
            istenen_plan,
            odeme_yontemi,
            fatura_bilgi,
            notlar,
            simdi,
        ))
        talep_id = cur.lastrowid
        conn.commit()

    return {"durum": "OK", "talep_id": talep_id, "olusturma": simdi}


def yukseltme_listele(durum=None, limit=200):
    """
    Yukseltme taleplerini listeler.
    durum: 'bekliyor' | 'onaylandi' | 'reddedildi' | None (hepsi)
    """
    with _baglanti() as conn:
        if durum:
            cur = conn.execute("""
                SELECT * FROM yukseltme_talepleri
                WHERE durum = ?
                ORDER BY olusturma DESC
                LIMIT ?
            """, (durum, limit))
        else:
            cur = conn.execute("""
                SELECT * FROM yukseltme_talepleri
                ORDER BY olusturma DESC
                LIMIT ?
            """, (limit,))
        return [dict(row) for row in cur.fetchall()]


def yukseltme_onayla(talep_id, islem_yapan="admin"):
    """
    Yukseltme talebini onaylar ve kullanicinin planini gunceller.
    """
    with _baglanti() as conn:
        talep = conn.execute(
            "SELECT * FROM yukseltme_talepleri WHERE id = ?", (talep_id,)
        ).fetchone()

        if not talep:
            return {"durum": "HATA", "mesaj": "Talep bulunamadi"}

        talep = dict(talep)

        if talep["durum"] != "bekliyor":
            return {"durum": "HATA", "mesaj": f"Talep zaten {talep['durum']}"}

        # Plani guncelle
        simdi = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute("""
            UPDATE users SET plan = ?
            WHERE kullanici_adi = ?
        """, (talep["istenen_plan"], talep["kullanici_adi"]))

        # Talebi onaylandi olarak isaretle
        conn.execute("""
            UPDATE yukseltme_talepleri
            SET durum = 'onaylandi', islem_tarih = ?, islem_yapan = ?
            WHERE id = ?
        """, (simdi, islem_yapan, talep_id))

        conn.commit()

    return {
        "durum": "OK",
        "kullanici_adi": talep["kullanici_adi"],
        "yeni_plan": talep["istenen_plan"],
    }


def yukseltme_reddet(talep_id, islem_yapan="admin", sebep=""):
    """Yukseltme talebini reddeder."""
    simdi = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with _baglanti() as conn:
        talep = conn.execute(
            "SELECT * FROM yukseltme_talepleri WHERE id = ?", (talep_id,)
        ).fetchone()

        if not talep:
            return {"durum": "HATA", "mesaj": "Talep bulunamadi"}

        if talep["durum"] != "bekliyor":
            return {"durum": "HATA", "mesaj": f"Talep zaten {talep['durum']}"}

        conn.execute("""
            UPDATE yukseltme_talepleri
            SET durum = 'reddedildi', islem_tarih = ?, islem_yapan = ?,
                notlar = COALESCE(notlar, '') || ' | RED: ' || ?
            WHERE id = ?
        """, (simdi, islem_yapan, sebep, talep_id))
        conn.commit()

    return {"durum": "OK"}


def yukseltme_sayaci():
    """Durum bazli talep sayisi."""
    with _baglanti() as conn:
        cur = conn.execute("""
            SELECT durum, COUNT(*) as n
            FROM yukseltme_talepleri
            GROUP BY durum
        """)
        return {r["durum"]: r["n"] for r in cur.fetchall()}


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

