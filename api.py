"""
FastAPI REST API - AI Act Madde 50 denetim servisi
"""
import uuid
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from rate_limiter import limiter
from pydantic import BaseModel

import db
from core import (
    ai_bildirimi_var_mi, deepfake_kontrol, kamu_metni_kontrol,
)

app = FastAPI(
    title="AI Uyumluluk Denetim API",
    description="AB AI Act Madde 50 denetim servisi",
    version="1.0.0",
)

db.init_db()


class DenetimIstegi(BaseModel):
    musteri: str
    sektor: Optional[str] = ""
    ai_tipi: str = "Chatbot / AI Asistan"
    chatbot_mesaji: Optional[str] = ""
    denetci: Optional[str] = "API"


@app.get("/")
def root():
    """Saglik kontrolu."""
    return {
        "servis": "AI Uyumluluk Denetim API",
        "versiyon": "1.0.0",
        "kapsam": "AB AI Act Madde 50",
        "durum": "aktif",
    }


@app.post("/denetle")
def denetle(request: Request, istek: DenetimIstegi):
    """Tek denetim yapar."""
    # Rate limit kontrolu
    ip = request.client.host if request.client else "unknown"
    limit = limiter.izin_var_mi(ip, "denetle", max_istek=30, sure=60)
    if not limit["izin"]:
        raise HTTPException(
            status_code=429,
            detail=f"Cok fazla istek. {limit['sifirlanma']} saniye sonra tekrar deneyin.",
            headers={"Retry-After": str(limit["sifirlanma"])},
        )

    if not istek.musteri:
        raise HTTPException(status_code=400, detail="musteri zorunlu")

    rapor_no = "AIACT-API-" + datetime.now().strftime("%Y%m%d") + "-" + str(uuid.uuid4())[:6].upper()
    genel = "UYUMSUZ"
    karar = "BLOCK"
    kanit_id = str(uuid.uuid4())
    bulgular = []

    if istek.ai_tipi == "Chatbot / AI Asistan":
        if not istek.chatbot_mesaji:
            raise HTTPException(status_code=400, detail="chatbot_mesaji zorunlu")
        bildirim = ai_bildirimi_var_mi(istek.chatbot_mesaji)
        if bildirim:
            genel = "UYUMLU"
            karar = "ALLOW"
            bulgular.append("AI bildirimi VAR")
        else:
            bulgular.append("AI bildirimi YOK")

    elif istek.ai_tipi == "Deepfake Icerik":
        df = deepfake_kontrol(True, True, False, False)
        genel = df["durum"]
        karar = "BLOCK" if genel == "UYUMSUZ" else "ALLOW"
        bulgular = df["bulgular"]

    elif istek.ai_tipi == "Kamu Yarari Metni":
        km = kamu_metni_kontrol(True, True, False, False, False)
        genel = km["durum"]
        karar = "BLOCK" if genel == "UYUMSUZ" else "ALLOW"
        bulgular = km["bulgular"]

    db.kaydet(
        rapor_no=rapor_no,
        modul="API",
        musteri=istek.musteri,
        sektor=istek.sektor or "",
        ai_tipi=istek.ai_tipi,
        denetci=istek.denetci or "API",
        genel_sonuc=genel,
        karar=karar,
        kanit_id=kanit_id,
        ceza_riski="15 milyon Euro veya cironun %3u" if genel == "UYUMSUZ" else "",
        json_veri={"bulgular": bulgular},
    )

    return {
        "rapor_no": rapor_no,
        "musteri": istek.musteri,
        "ai_tipi": istek.ai_tipi,
        "genel_sonuc": genel,
        "karar": karar,
        "kanit_id": kanit_id,
        "bulgular": bulgular,
        "ceza_riski": "15 milyon Euro veya cironun %3u" if genel == "UYUMSUZ" else None,
        "tarih": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


@app.get("/gecmis")
def gecmis(request: Request, limit: int = 50, musteri: Optional[str] = None, sonuc: Optional[str] = None):
    """Gecmis denetimleri listeler."""
    kwargs = {"limit": limit}
    if musteri:
        kwargs["filtre_musteri"] = musteri
    if sonuc:
        kwargs["filtre_sonuc"] = sonuc
    kayitlar = db.listele(**kwargs)
    return {"toplam": len(kayitlar), "kayitlar": kayitlar}


@app.get("/gecmis/{rapor_no}")
def gecmis_detay(request: Request, rapor_no: str):
    """Belirli bir denetimi getirir."""
    kayitlar = db.listele()
    kayit = next((k for k in kayitlar if k["rapor_no"] == rapor_no), None)
    if not kayit:
        raise HTTPException(status_code=404, detail="Kayit bulunamadi")
    return kayit


@app.get("/istatistik")
def istatistik(request: Request):
    """Genel istatistik."""
    return db.istatistik()

# ============================================================
# WEBHOOK ENDPOINT
# ============================================================
class WebhookIstegi(BaseModel):
    api_key: str
    ai_tipi: str = "Chatbot / AI Asistan"
    url: Optional[str] = ""
    mesaj: Optional[str] = ""


@app.post("/webhook/denetle")
def webhook_denetle(request: Request, istek: WebhookIstegi):
    """
    Webhook ile otomatik denetim.
    """
    # Rate limit
    ip = request.client.host if request.client else "unknown"
    limit = limiter.izin_var_mi(ip, "webhook", max_istek=60, sure=60)
    if not limit["izin"]:
        raise HTTPException(
            status_code=429,
            detail=f"Cok fazla istek. {limit['sifirlanma']} saniye sonra tekrar deneyin.",
        )

    # API anahtari dogrula
    musteri_bilgi = db.api_anahtari_dogrula(istek.api_key)
    if not musteri_bilgi:
        raise HTTPException(status_code=401, detail="Gecersiz API anahtari")

    musteri = musteri_bilgi.get("musteri", "Bilinmeyen")
    ip_adresi = request.client.host if request.client else ""

    rapor_no = "AIACT-WEB-" + datetime.now().strftime("%Y%m%d") + "-" + str(uuid.uuid4())[:6].upper()

    genel = "UYUMSUZ"
    karar = "BLOCK"
    kanit_id = str(uuid.uuid4())
    bulgular = []

    # AI tipine gore denetim
    if istek.ai_tipi == "Chatbot / AI Asistan":
        if not istek.mesaj:
            raise HTTPException(status_code=400, detail="mesaj zorunlu")
        bildirim = ai_bildirimi_var_mi(istek.mesaj)
        if bildirim:
            genel = "UYUMLU"
            karar = "ALLOW"
            bulgular.append("AI bildirimi VAR")
        else:
            bulgular.append("AI bildirimi YOK")

    elif istek.ai_tipi == "Deepfake Icerik":
        df = deepfake_kontrol(True, True, False, False)
        genel = df["durum"]
        karar = "BLOCK" if genel == "UYUMSUZ" else "ALLOW"
        bulgular = df["bulgular"]

    elif istek.ai_tipi == "Kamu Yarari Metni":
        km = kamu_metni_kontrol(True, True, False, False, False)
        genel = km["durum"]
        karar = "BLOCK" if genel == "UYUMSUZ" else "ALLOW"
        bulgular = km["bulgular"]

    # Veritabanina kaydet
    db.kaydet(
        rapor_no=rapor_no,
        modul="Webhook",
        musteri=musteri,
        ai_tipi=istek.ai_tipi,
        denetci="Webhook",
        genel_sonuc=genel,
        karar=karar,
        kanit_id=kanit_id,
        ceza_riski="15 milyon Euro veya cironun %3u" if genel == "UYUMSUZ" else "",
        json_veri={"bulgular": bulgular, "url": istek.url},
    )

    # Webhook log kaydet
    db.webhook_log_ekle(
        anahtar=istek.api_key[:15] + "...",
        musteri=musteri,
        ai_tipi=istek.ai_tipi,
        durum=genel,
        ip_adresi=ip_adresi,
        json_veri={"rapor_no": rapor_no, "url": istek.url},
    )

    return {
        "durum": genel,
        "rapor_no": rapor_no,
        "musteri": musteri,
        "ai_tipi": istek.ai_tipi,
        "karar": karar,
        "kanit_id": kanit_id,
        "bulgular": bulgular,
        "ceza_riski": "15 milyon Euro veya cironun %3u" if genel == "UYUMSUZ" else None,
        "tarih": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


@app.get("/webhook/log")
def webhook_log(request: Request, limit: int = 50):
    """Webhook log kayitlarini listeler."""
    loglar = db.webhook_log_listele(limit=limit)
    return {"toplam": len(loglar), "loglar": loglar}
