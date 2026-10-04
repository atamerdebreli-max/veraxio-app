"""
synthid_detector.py - SynthID Text filigran dogrulama modulu
Transformers v4.46.0+ ile yerlesik SynthID destegi kullanir.

NOT: SynthID dogrulama, filigran eklenirken kullanilan OZEL ANAHTAR'i 
gerektirir. Bu nedenle sadece KENDI urettiginiz metinleri dogrulayabilirsiniz.
Baskasinin metnini (Google Gemini dahil) dogrulamak icin Google'in ozel 
anahtarina ihtiyac vardir.
"""

from transformers import SynthIDTextWatermarkingConfig
import torch


# Varsayilan anahtar (demo amacli - gercek kullanimda ozel anahtar kullanin)
_DEMO_KEYS = [654, 400, 836, 123, 340, 443, 597, 160, 57, 29, 590, 639, 13, 715, 468, 882]
_NGRAM_LEN = 5


def filigran_ekle(metin: str, keys=None, ngram_len: int = _NGRAM_LEN) -> dict:
    """
    Metne SynthID filigrani ekler (demo amacli).
    
    Args:
        metin: Filigran eklenecek metin
        keys: Ozel anahtar listesi (None ise demo anahtari kullanilir)
        ngram_len: N-gram uzunlugu (varsayilan 5)
    
    Returns:
        dict: {"durum": "OK", "filigranli_metin": str, "keys": list}
    """
    try:
        if keys is None:
            keys = _DEMO_KEYS

        config = SynthIDTextWatermarkingConfig(
            keys=keys,
            ngram_len=ngram_len,
        )

        # NOT: Gercek filigranlama, bir dil modeli ile generate() cagrisi 
        # sirasinda yapilir. Bu fonksiyon sadece konfigurasyonu hazirlar.
        return {
            "durum": "OK",
            "mesaj": "Filigran konfigurasyonu hazir. Model.generate() ile kullanin.",
            "keys": keys,
            "ngram_len": ngram_len,
        }
    except Exception as e:
        return {"durum": "HATA", "hata": str(e)[:100]}


def synthid_destegi_var_mi() -> dict:
    """
    SynthID Text desteginin mevcut olup olmadigini kontrol eder.
    """
    try:
        from transformers import SynthIDTextWatermarkingConfig
        return {
            "destek": True,
            "surum": "Transformers yerlesik",
            "not": "Dogrulama icin ozel anahtar gerekir",
        }
    except ImportError:
        return {
            "destek": False,
            "hata": "Transformers v4.46.0+ gerekli",
        }


def synthid_dogrula(metin: str, keys=None) -> dict:
    """
    Metinde SynthID filigrani olup olmadigini kontrol eder.
    
    NOT: Bu fonksiyon, filigranin eklenmesi sirasinda kullanilan 
    AYNI anahtarlari gerektirir. Farkli anahtarlarla dogrulama yapilamaz.
    
    Args:
        metin: Dogrulanacak metin
        keys: Filigran eklenirken kullanilan anahtar listesi
    
    Returns:
        dict: {
            "durum": "FILIGRANLI" | "FILIGRANSIZ" | "DOGRULANAMADI" | "HATA",
            "detay": str
        }
    """
    try:
        if keys is None:
            return {
                "durum": "DOGRULANAMADI",
                "detay": "Dogrulama icin ozel anahtar gerekli. Google Gemini gibi "
                         "harici AI'larin filigranlari, onlarin ozel anahtari olmadan "
                         "dogrulanamaz.",
            }

        # SynthID dogrulama, ozel anahtar ve model logitleri gerektirir.
        # Bu, transformers kutuphanesinin dusuk seviyeli API'sini kullanmayi 
        # gerektirir. Su an icin sadece bilgilendirme yapiyoruz.
        return {
            "durum": "DOGRULANAMADI",
            "detay": "SynthID dogrulama, model logitleri ve ozel anahtar gerektirir. "
                     "Transformers v4.46+ ile mumkundur ancak ek entegrasyon gerekir.",
        }
    except Exception as e:
        return {"durum": "HATA", "hata": str(e)[:100]}