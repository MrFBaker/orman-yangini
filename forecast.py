# -*- coding: utf-8 -*-
"""
Open-Meteo Forecast API - 7 günlük hava tahmini verisini çeker.
Saatlik veri alınır, her gün için 12:00 LST değerleri + günlük yağış toplamı kullanılır.
"""
import urllib.request
import json

BASE = "https://api.open-meteo.com/v1/forecast"


def tahmin_cek(lat, lon):
    """
    Open-Meteo Forecast API'den 7 günlük saatlik tahmin verisini çeker.
    Her gün için öğlen 12:00 LST sıcaklık, nem, rüzgar + günlük toplam yağış döndürür.

    Parametreler:
        lat : enlem (float)
        lon : boylam (float)

    Dönüş: [{
        "tarih": "YYYYMMDD",
        "temp": float,
        "rh": float,
        "wind_kmh": float,
        "precip": float
    }, ...]
    """
    url = (
        f"{BASE}?latitude={lat}&longitude={lon}"
        f"&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation"
        f"&wind_speed_unit=kmh&timezone=auto&forecast_days=7"
    )

    with urllib.request.urlopen(url, timeout=30) as resp:
        data = json.loads(resp.read())

    hourly = data["hourly"]
    times = hourly["time"]
    temps = hourly["temperature_2m"]
    rhs = hourly["relative_humidity_2m"]
    winds = hourly["wind_speed_10m"]
    precips = hourly["precipitation"]

    gunler = {}
    for i, t in enumerate(times):
        tarih = t[:10].replace("-", "")
        saat = int(t[11:13])

        if tarih not in gunler:
            gunler[tarih] = {"precip_sum": 0.0}

        p = precips[i]
        if p is not None:
            gunler[tarih]["precip_sum"] += p

        if saat == 12:
            gunler[tarih]["temp"] = temps[i] if temps[i] is not None else 20.0
            gunler[tarih]["rh"] = rhs[i] if rhs[i] is not None else 50.0
            gunler[tarih]["wind_kmh"] = winds[i] if winds[i] is not None else 0.0

    sonuclar = []
    for tarih in sorted(gunler.keys()):
        g = gunler[tarih]
        if "temp" not in g:
            continue
        sonuclar.append({
            "tarih": tarih,
            "temp": round(g["temp"], 1),
            "rh": round(g["rh"], 1),
            "wind_kmh": round(g["wind_kmh"], 1),
            "precip": round(g["precip_sum"], 1),
        })

    return sonuclar
