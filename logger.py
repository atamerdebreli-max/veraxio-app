"""
Merkezi log sistemi
- logs/app_YYYYMMDD.log  -> gunluk dosya
- logs/error.log         -> sadece hatalar (uzun sureli)
- Konsola da yazar
"""
import logging
import sys
from pathlib import Path
from datetime import datetime

KOK = Path(__file__).parent
LOG_KLASOR = KOK / "logs"
LOG_KLASOR.mkdir(exist_ok=True)

# Gunluk dosya adi
bugun = datetime.now().strftime("%Y%m%d")
LOG_DOSYA = LOG_KLASOR / f"app_{bugun}.log"
ERROR_DOSYA = LOG_KLASOR / "error.log"

# Root logger ayari (bir kez)
_root = logging.getLogger()
if not _root.handlers:
    _root.setLevel(logging.INFO)

    # Format
    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 1) Gunluk dosya (INFO+)
    fh = logging.FileHandler(LOG_DOSYA, encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(fmt)
    _root.addHandler(fh)

    # 2) Hata dosyasi (ERROR+, kalici)
    eh = logging.FileHandler(ERROR_DOSYA, encoding="utf-8")
    eh.setLevel(logging.ERROR)
    eh.setFormatter(fmt)
    _root.addHandler(eh)

    # 3) Konsol (INFO+)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    _root.addHandler(ch)


def log_al(ad):
    """Modul adi ile logger dondurur."""
    return logging.getLogger(ad)


def log_dosya_yolu():
    """Aktif log dosya yolunu dondurur."""
    return str(LOG_DOSYA)