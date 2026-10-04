"""
rate_limiter.py - Basit, bagimsiz rate limiter
IP bazli istek sayaci tutar.
"""
import time
from collections import defaultdict
from threading import Lock


class RateLimiter:
    """
    IP bazli rate limiter.

    Kullanim:
        limiter = RateLimiter()
        izin = limiter.izin_var_mi("192.168.1.1", "denetle", max_istek=30, sure=60)
    """

    def __init__(self):
        # {ip: {endpoint: [(timestamp, ...), ...]}}
        self._kayitlar = defaultdict(lambda: defaultdict(list))
        self._lock = Lock()

    def izin_var_mi(self, ip, endpoint="default", max_istek=30, sure=60):
        """
        IP'nin belirtilen endpoint'e istek atma izni var mi?

        Args:
            ip: Istemci IP adresi
            endpoint: Endpoint adi (orn: "denetle")
            max_istek: Sure icindeki max istek
            sure: Saniye cinsinden zaman penceresi

        Returns:
            dict: {"izin": bool, "kalan": int, "sifirlanma": int}
        """
        simdi = time.time()
        esik = simdi - sure

        with self._lock:
            # Eski kayitlari temizle
            self._kayitlar[ip][endpoint] = [
                t for t in self._kayitlar[ip][endpoint] if t > esik
            ]

            kayitlar = self._kayitlar[ip][endpoint]

            if len(kayitlar) >= max_istek:
                # Limit asildi
                en_eski = min(kayitlar)
                sifirlanma = int(en_eski + sure - simdi) + 1
                return {
                    "izin": False,
                    "kalan": 0,
                    "sifirlanma": max(1, sifirlanma),
                }

            # Yeni kayit ekle
            kayitlar.append(simdi)
            return {
                "izin": True,
                "kalan": max_istek - len(kayitlar),
                "sifirlanma": sure,
            }

    def sifirla(self, ip=None, endpoint=None):
        """Kayitlari sifirlar."""
        with self._lock:
            if ip and endpoint:
                self._kayitlar[ip][endpoint] = []
            elif ip:
                self._kayitlar[ip] = defaultdict(list)
            else:
                self._kayitlar = defaultdict(lambda: defaultdict(list))

    def durum(self, ip):
        """IP'nin mevcut durumunu dondurur."""
        with self._lock:
            return {
                endpoint: len(kayitlar)
                for endpoint, kayitlar in self._kayitlar[ip].items()
            }


# Global limiter
limiter = RateLimiter()