# -*- coding: utf-8 -*-
"""
Open-Meteo archive API - saatlik veri ceker, her gun icin 12:00 LST degerini alir.
FWI standardi: oglen olcumu (sicaklik, nem, ruzgar) + gunluk toplam yagis.
"""
import urllib.request
import json

BASE = "https://archive-api.open-meteo.com/v1/archive"


def veri_cek(lat, lon, baslangic, bitis):
    """
    baslangic, bitis: YYYYMMDD string
    Donus: [{"tarih": "YYYYMMDD", "temp": float, "rh": float,
             "wind_kmh": float, "precip": float}, ...]
    """
    def fmt(d):
        return f"{d[:4]}-{d[4:6]}-{d[6:8]}"

    url = (
        f"{BASE}?latitude={lat}&longitude={lon}"
        f"&start_date={fmt(baslangic)}&end_date={fmt(bitis)}"
        f"&hourly=temperature_2m,relativehumidity_2m,windspeed_10m,precipitation"
        f"&windspeed_unit=kmh&timezone=auto"
    )

    with urllib.request.urlopen(url, timeout=30) as resp:
        data = json.loads(resp.read())

    hourly  = data["hourly"]
    times   = hourly["time"]           # "2023-06-01T12:00"
    temps   = hourly["temperature_2m"]
    rhs     = hourly["relativehumidity_2m"]
    winds   = hourly["windspeed_10m"]
    precips = hourly["precipitation"]

    gunler = {}
    for i, t in enumerate(times):
        tarih = t[:10].replace("-", "")   # YYYYMMDD
        saat  = int(t[11:13])

        if tarih not in gunler:
            gunler[tarih] = {"precip_sum": 0.0}

        # Gunluk toplam yagis
        p = precips[i]
        if p is not None:
            gunler[tarih]["precip_sum"] += p

        # Oglen anlık degerleri
        if saat == 12:
            gunler[tarih]["temp"]     = temps[i] if temps[i] is not None else 20.0
            gunler[tarih]["rh"]       = rhs[i]   if rhs[i]   is not None else 50.0
            gunler[tarih]["wind_kmh"] = winds[i]  if winds[i]  is not None else 0.0

    sonuclar = []
    for tarih in sorted(gunler.keys()):
        g = gunler[tarih]
        if "temp" not in g:
            continue
        sonuclar.append({
            "tarih":    tarih,
            "temp":     round(g["temp"], 1),
            "rh":       round(g["rh"], 1),
            "wind_kmh": round(g["wind_kmh"], 1),
            "precip":   round(g["precip_sum"], 1),
        })

    return sonuclar
