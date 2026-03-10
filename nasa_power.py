# -*- coding: utf-8 -*-
"""
NASA POWER API - Meteorolojik Veri Cekici
Kaynak: https://power.larc.nasa.gov/api/temporal/daily/point
"""

import urllib.request
import json

BASE_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
PARAMS   = "T2M_MAX,RH2M,WS10M_MAX,PRECTOTCORR"


def veri_cek(lat, lon, baslangic, bitis):
    """
    NASA POWER API'den gunluk meteoroloji verisi ceker.

    Parametreler:
        lat       : enlem (float, ornek: 39.0)
        lon       : boylam (float, ornek: 32.0)
        baslangic : YYYYMMDD formatinda string (ornek: '20230601')
        bitis     : YYYYMMDD formatinda string (ornek: '20230630')

    Dondurur:
        list of dict — her gun icin:
            {tarih, temp, rh, wind_ms, wind_kmh, precip}
    """
    url = (
        f"{BASE_URL}"
        f"?parameters={PARAMS}"
        f"&community=AG"
        f"&longitude={lon}"
        f"&latitude={lat}"
        f"&start={baslangic}"
        f"&end={bitis}"
        f"&format=JSON"
    )

    with urllib.request.urlopen(url, timeout=15) as r:
        data = json.loads(r.read().decode())

    prop = data["properties"]["parameter"]
    tarihler = sorted(prop["T2M_MAX"].keys())

    sonuclar = []
    for t in tarihler:
        wind_ms  = prop["WS10M_MAX"][t]
        wind_kmh = round(wind_ms * 3.6, 2)
        sonuclar.append({
            "tarih":    t,
            "temp":     prop["T2M_MAX"][t],
            "rh":       prop["RH2M"][t],
            "wind_ms":  wind_ms,
            "wind_kmh": wind_kmh,
            "precip":   prop["PRECTOTCORR"][t],
        })

    return sonuclar
