"""
Genel yardimci fonksiyonlar
"""


def tr_to_ascii(text):
    """Turkce karakterleri ASCII'ye cevirir (PDF uyumlulugu icin)."""
    if text is None:
        return ""
    cevir = {
        "ş": "s", "Ş": "S",
        "ı": "i", "İ": "I",
        "ğ": "g", "Ğ": "G",
        "ü": "u", "Ü": "U",
        "ö": "o", "Ö": "O",
        "ç": "c", "Ç": "C",
    }
    for tr, a in cevir.items():
        text = str(text).replace(tr, a)
    return text