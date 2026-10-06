"""
users tablosuna email_dogrulandi sutunu ekler.
Mevcut kullanicilari dogrulanmis olarak isaretler (admin, testuser2 vs).
Yeni kayitlar dogrulanmamis olur.
"""
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime

DB = Path("denetimler.db")

# Yedek
zaman = datetime.now().strftime("%Y%m%d_%H%M%S")
yedek = Path(f"denetimler_migemail_oncesi_{zaman}.db")
shutil.copy2(DB, yedek)
print(f"[+] Yedek: {yedek.name}")

conn = sqlite3.connect(str(DB))

# Mevcut sutunlar
mevcut = [r[1] for r in conn.execute("PRAGMA table_info(users)").fetchall()]

# email_dogrulandi ekle
if "email_dogrulandi" not in mevcut:
    conn.execute("ALTER TABLE users ADD COLUMN email_dogrulandi INTEGER DEFAULT 0")
    print("[+] email_dogrulandi sutunu eklendi.")
else:
    print("[i] email_dogrulandi zaten var.")

conn.commit()

# Mevcut kullanicilari dogrulanmis yap
conn.execute("UPDATE users SET email_dogrulandi = 1 WHERE email_dogrulandi = 0 OR email_dogrulandi IS NULL")
conn.commit()

# Dogrula
print()
print("[i] Kullanicilar:")
for r in conn.execute("SELECT kullanici_adi, email_dogrulandi FROM users").fetchall():
    print(f"  {r[0]}: email_dogrulandi = {r[1]}")

conn.close()
print()
print("=" * 60)
print("TAMAM! Simdi dogrulama zorunlulugunu ekleyelim.")
print("=" * 60)