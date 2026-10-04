"""
chatbot_scraper.py - Chatbot URL'sinden otomatik mesaj cekme
Web scraping ile chatbot widget'ini bulur ve ilk mesaji cikarir.
"""

import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse


# Chatbot widget'larinda gorulen tipik sinyaller
CHATBOT_SINYALLERI = [
    "chatbot", "chat-widget", "chatbot-widget", "intercom", "drift",
    "crisp", "tawk", "livechat", "zendesk", "freshchat", "hubspot-messages",
    "tidio", "olark", "purechat", "smartsupp", "userlike", "chaport",
]


def _chatbot_scriptleri_bul(soup):
    """Sayfadaki chatbot scriptlerini bulur."""
    bulunanlar = []
    for script in soup.find_all("script", src=True):
        src = script.get("src", "").lower()
        for sinyal in CHATBOT_SINYALLERI:
            if sinyal in src:
                bulunanlar.append(sinyal)
                break
    return list(set(bulunanlar))


def _metin_temizle(metin):
    """Metni temizler."""
    if not metin:
        return ""
    metin = re.sub(r'\s+', ' ', metin)
    return metin.strip()


def _chatbot_mesaji_cikar(soup):
    """Sayfadan chatbot ilk mesajini cikarmaya calisir."""
    chatbot_secicileri = [
        '[class*="chatbot"]', '[id*="chatbot"]',
        '[class*="chat-widget"]', '[id*="chat-widget"]',
        '[class*="message"]', '[class*="greeting"]',
        '[class*="welcome"]', '[class*="intro"]',
    ]

    adaylar = []
    for secici in chatbot_secicileri:
        try:
            for elem in soup.select(secici):
                metin = _metin_temizle(elem.get_text())
                if 10 < len(metin) < 500:
                    adaylar.append(metin)
        except Exception:
            continue

    if adaylar:
        adaylar.sort(key=len)
        return adaylar[0]

    return ""


def chatbot_url_denetle(url, timeout=10):
    """
    Verilen URL'deki chatbot'u bulur ve ilk mesaji cikarir.

    Returns:
        dict: {
            "durum": "OK" | "HATA" | "CHATBOT_YOK",
            "url": str,
            "chatbot_mesaji": str,
            "chatbot_bulundu": bool,
            "widget_tipleri": list,
            "sayfa_basligi": str,
            "hata": str (opsiyonel)
        }
    """
    sonuc = {
        "durum": "HATA",
        "url": url,
        "chatbot_mesaji": "",
        "chatbot_bulundu": False,
        "widget_tipleri": [],
        "sayfa_basligi": "",
    }

    if not url or not url.startswith(("http://", "https://")):
        sonuc["hata"] = "Gecersiz URL. http:// veya https:// ile baslamali."
        return sonuc

    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        baslik = soup.find("title")
        if baslik:
            sonuc["sayfa_basligi"] = _metin_temizle(baslik.get_text())

        widget_tipleri = _chatbot_scriptleri_bul(soup)
        sonuc["widget_tipleri"] = widget_tipleri
        sonuc["chatbot_bulundu"] = len(widget_tipleri) > 0

        mesaj = _chatbot_mesaji_cikar(soup)
        if mesaj:
            sonuc["chatbot_mesaji"] = mesaj
            sonuc["durum"] = "OK"
        elif sonuc["chatbot_bulundu"]:
            sonuc["durum"] = "OK"
            sonuc["chatbot_mesaji"] = "(Chatbot bulundu ama mesaj otomatik cikarilamadi. Manuel girin.)"
        else:
            sonuc["durum"] = "CHATBOT_YOK"
            sonuc["hata"] = "Sayfada chatbot widget'i bulunamadi."

        return sonuc

    except requests.exceptions.Timeout:
        sonuc["hata"] = "Zaman asimi. Site yanit vermedi."
        return sonuc
    except requests.exceptions.RequestException as e:
        sonuc["hata"] = f"Baglanti hatasi: {str(e)[:80]}"
        return sonuc
    except Exception as e:
        sonuc["hata"] = f"Beklenmeyen hata: {str(e)[:80]}"
        return sonuc


def chatbot_url_gecerli_mi(url):
    """URL formatini kontrol eder."""
    if not url:
        return False
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False