"""
landing_server.py - Veraxio Landing Page + Demo API
Calistir: py landing_server.py

Ozellikler:
- Statik dosyalari servis eder (landing.html, assets)
- POST /api/demo -> demo talebini DB'ye kaydeder
- Tarayiciyi otomatik acar
"""
import http.server
import socketserver
import os
import json
import webbrowser
import threading
import time
import sqlite3
import sys
from datetime import datetime
from urllib.parse import urlparse

PORT = 8502
DB_YOLU = os.path.join(os.path.dirname(os.path.abspath(__file__)), "denetimler.db")


def _tarayici_ac():
    """2 saniye sonra tarayiciyi acar."""
    time.sleep(2)
    webbrowser.open(f"http://localhost:{PORT}/landing.html")


def _db_demo_kaydet(veri):
    """Demo talebini DB'ye kaydeder."""
    try:
        conn = sqlite3.connect(DB_YOLU)
        conn.row_factory = sqlite3.Row

        # Rapor no
        rapor_no = "DEMO-" + datetime.now().strftime("%Y%m%d%H%M%S")

        # Karar alaninda ozet bilgi
        karar = (
            f"email={veri.get('email', '-')} "
            f"tel={veri.get('telefon', '-')}"
        )

        conn.execute("""
            INSERT INTO denetimler
            (rapor_no, tarih, modul, musteri, sektor, ai_tipi, denetci,
             genel_sonuc, karar, kanit_id, ceza_riski, json_veri, firma_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            rapor_no,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Demo Talebi",
            veri.get("ad", "-"),
            veri.get("sirket", "-"),
            "-",
            "landing",
            "DEMO_TALEBI",
            karar,
            rapor_no,
            "",
            json.dumps(veri, ensure_ascii=False),
            None,
        ))
        conn.commit()
        conn.close()
        return rapor_no
    except Exception as e:
        print(f"[Landing] DB kayit hatasi: {e}")
        return None


class Handler(http.server.SimpleHTTPRequestHandler):
    """Statik dosyalar + /api/demo POST handler."""

    def do_POST(self):
        """POST /api/demo - Demo talebini al ve kaydet."""
        parsed = urlparse(self.path)

        if parsed.path == "/api/demo":
            try:
                uzunluk = int(self.headers.get("Content-Length", 0))
                ham = self.rfile.read(uzunluk).decode("utf-8")
                veri = json.loads(ham)

                # Zorunlu alan kontrolu
                if not veri.get("ad") or not veri.get("email"):
                    self._yanit(400, {"durum": "HATA", "mesaj": "Ad ve email zorunlu"})
                    return

                rapor_no = _db_demo_kaydet(veri)
                if rapor_no:
                    print(f"[Landing] Yeni demo talebi: {veri.get('ad')} <{veri.get('email')}> (kayit: {rapor_no})")
                    self._yanit(200, {"durum": "OK", "kayit": rapor_no})
                else:
                    self._yanit(500, {"durum": "HATA", "mesaj": "Kayit yapilamadi"})
            except Exception as e:
                print(f"[Landing] POST hatasi: {e}")
                self._yanit(400, {"durum": "HATA", "mesaj": str(e)})
        else:
            self._yanit(404, {"durum": "HATA", "mesaj": "Endpoint yok"})

    def _yanit(self, kod, veri):
        """JSON yanit dondur."""
        self.send_response(kod)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(veri, ensure_ascii=False).encode("utf-8"))

    def log_message(self, format, *args):
        """Konsol log'unu sadeleştir (default cok gurultulu)."""
        # Sadece hatalari goster
        if args and len(args) > 1 and str(args[1]).startswith(("4", "5")):
            print(f"[Landing] {args[0]} {args[1]}")


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Tarayiciyi arka planda ac
    threading.Thread(target=_tarayici_ac, daemon=True).start()

    # Port dolu mu kontrol et
    try:
        socketserver.TCPServer.allow_reuse_address = True
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print("=" * 60)
            print("Veraxio - Landing Page + Demo API")
            print("=" * 60)
            print(f"URL: http://localhost:{PORT}/landing.html")
            print(f"API: http://localhost:{PORT}/api/demo")
            print()
            print("Durdurmak icin: Ctrl+C")
            print("=" * 60)
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\nSunucu durduruldu.")
    except OSError as e:
        print(f"[!] Port {PORT} mesgul: {e}")
        print(f"[i] Baska bir uygulama {PORT} portunu kullaniyor.")
        print(f"[i] Cozum: landing_server.py'de PORT degerini degistir.")


if __name__ == "__main__":
    main()