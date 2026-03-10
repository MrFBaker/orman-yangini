# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
import fwi_hesap as f
import openmeteo as om

app = Flask(__name__)


def warmup_fwi(lat, lon, baslangic):
    """
    Yil basından (Ocak 1) başlayarak başlangıç tarihine kadar FWI hesaplar.
    Döndürür: (ffmc0, dmc0, dc0) — ısınmış başlangıç değerleri.
    """
    jan1 = baslangic[:4] + "0101"
    if baslangic <= jan1:
        return f.FFMC_BASLANGIC, f.DMC_BASLANGIC, f.DC_BASLANGIC

    prev_str = (datetime.strptime(baslangic, "%Y%m%d") - timedelta(days=1)).strftime("%Y%m%d")
    gunler = om.veri_cek(lat, lon, jan1, prev_str)

    ffmc0, dmc0, dc0 = f.FFMC_BASLANGIC, f.DMC_BASLANGIC, f.DC_BASLANGIC
    for gun in gunler:
        ay = int(gun["tarih"][4:6])
        r = f.hesapla(
            temp=gun["temp"], rh=gun["rh"], wind=gun["wind_kmh"],
            precip=gun["precip"], month=ay,
            ffmc0=ffmc0, dmc0=dmc0, dc0=dc0,
            lat=lat,
        )
        ffmc0, dmc0, dc0 = r["ffmc"], r["dmc"], r["dc"]
    return ffmc0, dmc0, dc0


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/hesapla", methods=["POST"])
def hesapla():
    try:
        data = request.get_json()
        lat_v = float(data["lat"]) if "lat" in data else None
        sonuc = f.hesapla(
            temp   = float(data["temp"]),
            rh     = float(data["rh"]),
            wind   = float(data["wind"]),
            precip = float(data["precip"]),
            month  = int(data["month"]),
            ffmc0  = float(data.get("ffmc0", f.FFMC_BASLANGIC)),
            dmc0   = float(data.get("dmc0",  f.DMC_BASLANGIC)),
            dc0    = float(data.get("dc0",   f.DC_BASLANGIC)),
            lat    = lat_v,
        )
        return jsonify({"ok": True, "sonuc": sonuc})
    except Exception as e:
        return jsonify({"ok": False, "hata": str(e)}), 400

@app.route("/nasa", methods=["POST"])
def nasa_veri():
    """
    NASA POWER'dan veri cekip ardisik FWI hesaplar.
    Girdi: { lat, lon, baslangic (YYYYMMDD), bitis (YYYYMMDD) }
    """
    try:
        data = request.get_json()
        lat       = float(data["lat"])
        lon       = float(data["lon"])
        baslangic = str(data["baslangic"])
        bitis     = str(data["bitis"])

        gunler = om.veri_cek(lat, lon, baslangic, bitis)

        ffmc0, dmc0, dc0 = warmup_fwi(lat, lon, baslangic)

        sonuclar = []
        for gun in gunler:
            ay = int(gun["tarih"][4:6])
            r  = f.hesapla(
                temp   = gun["temp"],
                rh     = gun["rh"],
                wind   = gun["wind_kmh"],
                precip = gun["precip"],
                month  = ay,
                ffmc0  = ffmc0,
                dmc0   = dmc0,
                dc0    = dc0,
                lat    = lat,
            )
            sonuclar.append({
                "tarih":    gun["tarih"],
                "temp":     gun["temp"],
                "rh":       gun["rh"],
                "wind_kmh": gun["wind_kmh"],
                "precip":   gun["precip"],
                **r
            })
            ffmc0, dmc0, dc0 = r["ffmc"], r["dmc"], r["dc"]

        return jsonify({"ok": True, "sonuclar": sonuclar})
    except Exception as e:
        return jsonify({"ok": False, "hata": str(e)}), 400

@app.route("/csv", methods=["POST"])
def csv_hesapla():
    """
    CSV satirlarından ardisik FWI hesaplar.
    Girdi: { satirlar: [{tarih, temp, rh, wind, precip}, ...], ffmc0, dmc0, dc0 }
    """
    try:
        data     = request.get_json()
        satirlar = data["satirlar"]
        ffmc0    = float(data.get("ffmc0", f.FFMC_BASLANGIC))
        dmc0     = float(data.get("dmc0",  f.DMC_BASLANGIC))
        dc0      = float(data.get("dc0",   f.DC_BASLANGIC))
        lat_v    = float(data["lat"]) if "lat" in data and data["lat"] != "" else None

        sonuclar = []
        for satir in satirlar:
            tarih  = str(satir.get("tarih", ""))
            ay     = int(tarih[4:6]) if len(tarih) == 8 else int(satir.get("month", 7))
            r = f.hesapla(
                temp   = float(satir["temp"]),
                rh     = float(satir["rh"]),
                wind   = float(satir["wind"]),
                precip = float(satir["precip"]),
                month  = ay,
                ffmc0  = ffmc0,
                dmc0   = dmc0,
                dc0    = dc0,
                lat    = lat_v,
            )
            sonuclar.append({
                "tarih":    tarih,
                "temp":     float(satir["temp"]),
                "rh":       float(satir["rh"]),
                "wind_kmh": float(satir["wind"]),
                "precip":   float(satir["precip"]),
                **r
            })
            ffmc0, dmc0, dc0 = r["ffmc"], r["dmc"], r["dc"]

        return jsonify({"ok": True, "sonuclar": sonuclar})
    except Exception as e:
        return jsonify({"ok": False, "hata": str(e)}), 400


@app.route("/referans", methods=["GET"])
def referans_test():
    """
    Van Wagner (1987) referans değerleriyle formül doğrulaması.
    Tablo 1'deki girdi/çıktı çifti kullanılır.
    """
    girdi = {"temp": 17, "rh": 42, "wind": 25, "precip": 0, "month": 7,
             "ffmc0": 85.0, "dmc0": 6.0, "dc0": 15.0}
    beklenen = {"ffmc": 87.69, "dmc": 8.50, "dc": 19.80,
                "isi": 10.85, "bui": 8.40, "fwi": 10.96}

    sonuc = f.hesapla(
        temp=girdi["temp"], rh=girdi["rh"], wind=girdi["wind"],
        precip=girdi["precip"], month=girdi["month"],
        ffmc0=girdi["ffmc0"], dmc0=girdi["dmc0"], dc0=girdi["dc0"],
        lat=None
    )

    karsilastirma = {}
    for k in beklenen:
        fark = abs(sonuc[k] - beklenen[k])
        karsilastirma[k] = {
            "beklenen": beklenen[k],
            "hesaplanan": sonuc[k],
            "fark": round(fark, 3),
            "gecti": fark < 0.1
        }

    return jsonify({"ok": True, "girdi": girdi, "karsilastirma": karsilastirma})


@app.route("/test", methods=["GET"])
def test_yangin():
    """
    Gercek yangin olaylari icin FWI hesaplar.
    Her olay icin Ocak 1'den isinma yapilir, yangin gununde hesap yapilir.
    """
    olaylar = [
        {"isim": "Manavgat Yangini", "yer": "Antalya",  "tarih": "20210728", "lat": 36.78, "lon": 31.44},
        {"isim": "Marmaris Yangini", "yer": "Mugla",    "tarih": "20210730", "lat": 36.85, "lon": 28.27},
        {"isim": "Izmir Yangini",    "yer": "Izmir",    "tarih": "20190819", "lat": 38.42, "lon": 27.14},
    ]
    sonuclar = []
    for o in olaylar:
        try:
            ffmc0, dmc0, dc0 = warmup_fwi(o["lat"], o["lon"], o["tarih"])
            gunler = om.veri_cek(o["lat"], o["lon"], o["tarih"], o["tarih"])
            if not gunler:
                raise ValueError("Veri alinamadi")
            gun = gunler[0]
            ay  = int(gun["tarih"][4:6])
            r   = f.hesapla(
                temp=gun["temp"], rh=gun["rh"], wind=gun["wind_kmh"],
                precip=gun["precip"], month=ay,
                ffmc0=ffmc0, dmc0=dmc0, dc0=dc0,
                lat=o["lat"]
            )
            sonuclar.append({
                "isim":     o["isim"],
                "yer":      o["yer"],
                "tarih":    o["tarih"],
                "temp":     gun["temp"],
                "rh":       gun["rh"],
                "wind_kmh": gun["wind_kmh"],
                "precip":   gun["precip"],
                **r
            })
        except Exception as e:
            sonuclar.append({"isim": o["isim"], "yer": o["yer"], "tarih": o["tarih"], "hata": str(e)})

    return jsonify({"ok": True, "sonuclar": sonuclar})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
