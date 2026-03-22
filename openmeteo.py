# -*- coding: utf-8 -*-
"""
Open-Meteo archive API - saatlik veri ceker, her gun icin 12:00 LST degerini alir.
FWI standardi: oglen olcumu (sicaklik, nem, ruzgar) + gunluk toplam yagis.
"""
import urllib.request
import json
import time

BASE = "https://archive-api.open-meteo.com/v1/archive"


def _fetch_with_retry(url, max_retries=3):
    """429 rate limit durumunda bekleyip tekrar dener."""
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(url, timeout=30) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < max_retries - 1:
                time.sleep(2 ** attempt + 1)
                continue
            raise


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
        f"&hourly=temperature_2m,relativehumidity_2m,windspeed_10m,precipitation,dewpoint_2m"
        f"&daily=temperature_2m_max"
        f"&windspeed_unit=kmh&timezone=auto"
    )

    data = _fetch_with_retry(url)

    hourly  = data["hourly"]
    times   = hourly["time"]
    temps   = hourly["temperature_2m"]
    rhs     = hourly["relativehumidity_2m"]
    winds   = hourly["windspeed_10m"]
    precips = hourly["precipitation"]
    dews    = hourly.get("dewpoint_2m", [None] * len(times))

    daily      = data.get("daily", {})
    daily_dates = daily.get("time", [])
    daily_tmax  = daily.get("temperature_2m_max", [])
    tmax_map = {}
    for j, d in enumerate(daily_dates):
        tmax_map[d.replace("-", "")] = daily_tmax[j] if j < len(daily_tmax) else None

    gunler = {}
    for i, t in enumerate(times):
        tarih = t[:10].replace("-", "")
        saat  = int(t[11:13])

        if tarih not in gunler:
            gunler[tarih] = {"precip_sum": 0.0}

        p = precips[i]
        if p is not None:
            gunler[tarih]["precip_sum"] += p

        if saat == 12:
            gunler[tarih]["temp"]      = temps[i] if temps[i] is not None else 20.0
            gunler[tarih]["rh"]        = rhs[i]   if rhs[i]   is not None else 50.0
            gunler[tarih]["wind_kmh"]  = winds[i]  if winds[i]  is not None else 0.0
            gunler[tarih]["dew_point"] = dews[i]   if dews[i]   is not None else 10.0

    sonuclar = []
    for tarih in sorted(gunler.keys()):
        g = gunler[tarih]
        if "temp" not in g:
            continue
        sonuclar.append({
            "tarih":     tarih,
            "temp":      round(g["temp"], 1),
            "rh":        round(g["rh"], 1),
            "wind_kmh":  round(g["wind_kmh"], 1),
            "precip":    round(g["precip_sum"], 1),
            "dew_point": round(g["dew_point"], 1),
            "temp_max":  round(tmax_map.get(tarih, g["temp"]), 1),
        })

    return sonuclar
