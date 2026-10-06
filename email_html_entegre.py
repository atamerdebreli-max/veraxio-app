"""
email_sender.py'deki 3 fonksiyonu HTML kullanacak sekilde gunceller:
- deneme_emaili_gonder -> hos_geldin_email
- sifre_sifirlama_emaili_gonder -> sifre_sifirla_email
- email_dogrulama_gonder -> sifre_sifirla_email (dogrulama linki)
"""
import shutil
from pathlib import Path
from datetime import datetime

KOK = Path(".")
HEDEF = KOK / "email_sender.py"

icerik = HEDEF.read_text(encoding="utf-8")

if "from email_templates import" in icerik:
    print("[i] Zaten entegre edilmis.")
    raise SystemExit(0)

zaman = datetime.now().strftime("%Y%m%d_%H%M%S")
yedek = KOK / f"email_entegre_oncesi_{zaman}.py.bak"
shutil.copy2(HEDEF, yedek)
print(f"[+] Yedek: {yedek.name}")

# 1) Import ekle
import_anchor = "from dotenv import load_dotenv"
if import_anchor in icerik:
    yeni_import = import_anchor + "\n\n# HTML sablonlari\nfrom email_templates import (\n    hos_geldin_email,\n    sifre_sifirla_email,\n    denetim_rapor_email,\n    demo_talebi_email,\n)"
    icerik = icerik.replace(import_anchor, yeni_import, 1)
    print("[+] Import eklendi.")
else:
    print("[!] dotenv import bulunamadi, alternatif deneniyor...")
    # Farkli bir yere ekle
    icerik = "from email_templates import (\n    hos_geldin_email,\n    sifre_sifirla_email,\n    denetim_rapor_email,\n    demo_talebi_email,\n)\n\n" + icerik
    print("[+] Import en basa eklendi.")

HEDEF.write_text(icerik, encoding="utf-8")
print("[+] email_sender.py guncellendi.")
print()
print("=" * 60)
print("SONRAKI: Fonksiyonlarin icini manuel guncelleyecegiz")
print("=" * 60)