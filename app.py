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
    Ara adımlar da döndürülür — kullanıcı her sayıyı elle doğrulayabilir.
    """
    import math as _m
    T, H, W, r, ay = 17, 42, 25, 0, 7
    FFMC0, DMC0, DC0 = 85.0, 6.0, 15.0

    # ── FFMC ara adımlar ──────────────────────────────────────────
    mo   = 147.2 * (101.0 - FFMC0) / (59.5 + FFMC0)
    ed   = (0.942 * H**0.679 + 11.0 * _m.exp((H-100)/10)
            + 0.18*(21.1-T)*(1-_m.exp(-0.115*H)))
    ew   = (0.618 * H**0.753 + 10.0 * _m.exp((H-100)/10)
            + 0.18*(21.1-T)*(1-_m.exp(-0.115*H)))
    k0d  = (0.424*(1-(H/100)**1.7) + 0.0694*_m.sqrt(W)*(1-(H/100)**8))
    kd   = k0d * 0.581 * _m.exp(0.0365*T)
    m    = ed + (mo - ed) / (10.0**kd)
    ffmc_val = 59.5*(250-m)/(147.2+m)

    # ── DMC ara adımlar ───────────────────────────────────────────
    Le   = f.LE_30N[ay-1]          # Temmuz ≥30°N = 12.4
    K    = 1.894*(T+1.1)*(100-H)*Le*0.0001
    dmc_val = DMC0 + K

    # ── DC ara adımlar ────────────────────────────────────────────
    Lf   = f.LF_20N[ay-1]          # Temmuz ≥20°N = 6.4
    V    = 0.36*(T+2.8) + Lf
    dc_val = DC0 + 0.5*V

    # ── ISI ara adımlar ───────────────────────────────────────────
    m_isi = 147.2*(101-ffmc_val)/(59.5+ffmc_val)
    fw   = _m.exp(0.05039*W)
    ff   = 91.9*_m.exp(-0.1386*m_isi)*(1+m_isi**5.31/49300000)
    isi_val = 0.208*fw*ff

    # ── BUI ara adımlar ───────────────────────────────────────────
    if dmc_val <= 0.4*dc_val:
        bui_yol = "dmc <= 0.4*dc"
        bui_val = 0.8*dmc_val*dc_val/(dmc_val+0.4*dc_val)
    else:
        bui_yol = "dmc > 0.4*dc"
        P = 1 - 0.8*dc_val/(dmc_val+0.4*dc_val)
        bui_val = dmc_val - P*(0.92+(0.0114*dmc_val)**1.7)

    # ── FWI ara adımlar ───────────────────────────────────────────
    fd   = 0.626*bui_val**0.809 + 2.0
    B    = 0.1*isi_val*fd
    fwi_val = _m.exp(2.72*(0.434*_m.log(B))**0.647) if B > 1 else B

    adimlar = {
        "ffmc": {
            "mo":   round(mo, 4),
            "ed":   round(ed, 4),
            "ew":   round(ew, 4),
            "k0d":  round(k0d, 4),
            "kd":   round(kd, 4),
            "m":    round(m, 4),
            "sonuc": round(ffmc_val, 2)
        },
        "dmc": {
            "Le":   Le,
            "K":    round(K, 4),
            "sonuc": round(dmc_val, 2)
        },
        "dc": {
            "Lf":   Lf,
            "V":    round(V, 4),
            "DC_0+0.5V": f"15 + 0.5×{round(V,4)} = {round(dc_val,4)}",
            "sonuc": round(dc_val, 2)
        },
        "isi": {
            "m":    round(m_isi, 4),
            "fw":   round(fw, 4),
            "ff":   round(ff, 4),
            "sonuc": round(isi_val, 2)
        },
        "bui": {
            "kural": bui_yol,
            "sonuc": round(bui_val, 2)
        },
        "fwi": {
            "fd":   round(fd, 4),
            "B":    round(B, 4),
            "sonuc": round(fwi_val, 2)
        }
    }

    beklenen = {"ffmc": 87.69, "dmc": 8.47, "dc": 21.76,
                "isi": 10.85, "bui": 8.59, "fwi": 10.14}

    karsilastirma = {}
    for k in beklenen:
        hesaplanan = adimlar[k]["sonuc"]
        fark = abs(hesaplanan - beklenen[k])
        karsilastirma[k] = {
            "beklenen":   beklenen[k],
            "hesaplanan": hesaplanan,
            "fark":       round(fark, 3),
            "gecti":      fark < 0.1
        }

    return jsonify({
        "ok": True,
        "girdi": {"T": T, "H": H, "W": W, "r": r, "ay": ay,
                  "FFMC0": FFMC0, "DMC0": DMC0, "DC0": DC0},
        "adimlar": adimlar,
        "karsilastirma": karsilastirma
    })


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
