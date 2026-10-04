"""
ai_text_detector.py - AI metin tespit modulu
Model: Hello-SimpleAI/chatgpt-detector-roberta
Dogruluk: ~%95 (Ingilizce metinlerde)
Sinirlama: Turkce metinlerde dogruluk dusuk
"""

# LAZY_IMPORT_FIX - pipeline fonksiyon icine tasindi

# ============================================================
# RoBERTa - Genel AI Metin Tespiti
# ============================================================
_roberta_pipe = None


def _roberta_yukle():
    """Model ve pipeline'i ilk kullanimda yukler (lazy loading)."""
    global _roberta_pipe
    if _roberta_pipe is None:
        from transformers import pipeline
        _roberta_pipe = pipeline(
            "text-classification",
            model="Hello-SimpleAI/chatgpt-detector-roberta"
        )
    return _roberta_pipe


def _turkce_mi(metin: str) -> bool:
    """Metnin Turkce olup olmadigini kontrol eder."""
    turkce_karakterler = set("çğıöşüÇĞİÖŞÜ")
    return any(k in metin for k in turkce_karakterler)


def ai_metin_tespit_et(metin: str) -> dict:
    """
    Metni RoBERTa modeli ile analiz eder.

    Args:
        metin: Analiz edilecek metin (max 512 token)

    Returns:
        dict: {
            "durum": "AI" | "INSAN" | "HATA",
            "ai_olasilik": float,
            "insan_olasilik": float,
            "model": str,
            "uyari": str (opsiyonel, Turkce metinler icin)
        }
    """
    if not metin or not metin.strip():
        return {
            "durum": "HATA",
            "hata": "Bos metin",
            "model": "Hello-SimpleAI/chatgpt-detector-roberta",
        }

    try:
        pipe = _roberta_yukle()
        # Model max 512 token - fazlasini kes
        sonuc = pipe(metin[:512])[0]
        label = sonuc["label"]
        score = sonuc["score"]

        # Model LABEL_0 = Human, LABEL_1 = ChatGPT (veya benzeri)
        if "ChatGPT" in label or "AI" in label or "LABEL_1" in label:
            ai_olasilik = score
            insan_olasilik = 1 - score
            durum = "AI"
        else:
            insan_olasilik = score
            ai_olasilik = 1 - score
            durum = "INSAN"

        sonuc_dict = {
            "durum": durum,
            "ai_olasilik": round(ai_olasilik, 4),
            "insan_olasilik": round(insan_olasilik, 4),
            "model": "Hello-SimpleAI/chatgpt-detector-roberta",
        }

        # Turkce metin uyarisi
        if _turkce_mi(metin):
            sonuc_dict["uyari"] = (
                "Turkce metinlerde model dogrulugu dusuktur. "
                "Ingilizce metinlerde daha guvenilir sonuc alinir."
            )

        return sonuc_dict

    except Exception as e:
        return {
            "durum": "HATA",
            "hata": str(e)[:100],
            "model": "Hello-SimpleAI/chatgpt-detector-roberta",
        }