# -*- coding: utf-8 -*-
try:
    import sentry_sdk
    sentry_sdk.init(
        dsn="https://3c46d86740823152fba5c5738ffa1987@o4511089160683520.ingest.de.sentry.io/4511089167433808",
        send_default_pii=True,
    )
except ImportError:
    pass  # Sentry opsiyonel — local dev'de gerekmez

from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for
from datetime import datetime, timedelta
import sys, os, io
sys.path.insert(0, os.path.dirname(__file__))
import fwi_hesap as f
import openmeteo as om
import forecast as fc
import indeksler as idx
try:
    import istasyon as ist
except ImportError:
    ist = None

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "fire-ews-secret-2026")

# Kullanıcı bilgileri
USERS = {
    "admin": "fire2026",
    "reyhan21": "123456",
}


@app.before_request
def login_required():
    """Her istekte session kontrolü — giriş yapılmamışsa login sayfasına yönlendir."""
    allowed = ["/login", "/static"]
    if any(request.path.startswith(p) for p in allowed):
        return
    if not session.get("logged_in"):
        if request.path == "/" or request.headers.get("Accept", "").startswith("text/html"):
            return redirect(url_for("login_page"))
        return jsonify({"ok": False, "hata": "Giriş yapılmamış"}), 401


@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        data = request.get_json() if request.is_json else request.form
        user = data.get("username", "")
        pw = data.get("password", "")
        if user in USERS and USERS[user] == pw:
            session["logged_in"] = True
            session.permanent = True
            if request.is_json:
                return jsonify({"ok": True})
            return redirect(url_for("index"))
        if request.is_json:
            return jsonify({"ok": False, "hata": "Hatalı kullanıcı adı veya şifre"}), 401
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_page"))


def warmup(lat, lon, baslangic):
    """1 Ocak'tan başlangıç tarihine kadar tüm indeks state'lerini biriktir."""
    jan1 = baslangic[:4] + "0101"
    state = {
        "ffmc0": f.FFMC_BASLANGIC, "dmc0": f.DMC_BASLANGIC, "dc0": f.DC_BASLANGIC,
        "kbdi0": idx.KBDI_BASLANGIC, "nesterov0": idx.NESTEROV_BASLANGIC,
    }
    if baslangic <= jan1:
        return state
    prev_str = (datetime.strptime(baslangic, "%Y%m%d") - timedelta(days=1)).strftime("%Y%m%d")
    gunler = om.veri_cek(lat, lon, jan1, prev_str)
    for gun in gunler:
        ay = int(gun["tarih"][4:6])
        r = f.hesapla(temp=gun["temp"], rh=gun["rh"], wind=gun["wind_kmh"],
                      precip=gun["precip"], month=ay,
                      ffmc0=state["ffmc0"], dmc0=state["dmc0"], dc0=state["dc0"], lat=lat)
        state["ffmc0"], state["dmc0"], state["dc0"] = r["ffmc"], r["dmc"], r["dc"]
        ek = idx.hesapla_ek(temp=gun["temp"], rh=gun["rh"], wind=gun["wind_kmh"],
                            precip=gun["precip"], temp_max=gun.get("temp_max", gun["temp"]),
                            dew_point=gun.get("dew_point", 10.0),
                            kbdi0=state["kbdi0"], nesterov0=state["nesterov0"])
        state["kbdi0"] = ek["kbdi"]
        state["nesterov0"] = ek["nesterov"]
    return state


@app.route("/")
def index():
    return render_template("index_v2.html")


@app.route("/hesapla", methods=["POST"])
def hesapla():
    try:
        data = request.get_json()
        lat_v = float(data["lat"]) if "lat" in data and data["lat"] != "" else None
        temp = float(data["temp"])
        rh = float(data["rh"])
        wind = float(data["wind"])
        precip = float(data["precip"])
        sonuc = f.hesapla(
            temp=temp, rh=rh, wind=wind, precip=precip,
            month=int(data["month"]),
            ffmc0=float(data.get("ffmc0", f.FFMC_BASLANGIC)),
            dmc0=float(data.get("dmc0", f.DMC_BASLANGIC)),
            dc0=float(data.get("dc0", f.DC_BASLANGIC)),
            lat=lat_v,
        )
        ek = idx.hesapla_ek(temp=temp, rh=rh, wind=wind, precip=precip,
                            temp_max=float(data.get("temp_max", temp)),
                            dew_point=float(data.get("dew_point", 10.0)))
        sonuc.update(ek)
        return jsonify({"ok": True, "sonuc": sonuc})
    except Exception as e:
        return jsonify({"ok": False, "hata": str(e)}), 400


@app.route("/nasa", methods=["POST"])
def nasa_veri():
    try:
        data = request.get_json()
        lat = float(data["lat"])
        lon = float(data["lon"])
        baslangic = str(data["baslangic"])
        bitis = str(data["bitis"])
        gunler = om.veri_cek(lat, lon, baslangic, bitis)
        s = warmup(lat, lon, baslangic)
        sonuclar = []
        for gun in gunler:
            ay = int(gun["tarih"][4:6])
            r = f.hesapla(temp=gun["temp"], rh=gun["rh"], wind=gun["wind_kmh"],
                          precip=gun["precip"], month=ay,
                          ffmc0=s["ffmc0"], dmc0=s["dmc0"], dc0=s["dc0"], lat=lat)
            ek = idx.hesapla_ek(temp=gun["temp"], rh=gun["rh"], wind=gun["wind_kmh"],
                                precip=gun["precip"], temp_max=gun.get("temp_max", gun["temp"]),
                                dew_point=gun.get("dew_point", 10.0),
                                kbdi0=s["kbdi0"], nesterov0=s["nesterov0"])
            satir = {"tarih": gun["tarih"], "temp": gun["temp"], "rh": gun["rh"],
                     "wind_kmh": gun["wind_kmh"], "precip": gun["precip"], **r, **ek}
            sonuclar.append(satir)
            s["ffmc0"], s["dmc0"], s["dc0"] = r["ffmc"], r["dmc"], r["dc"]
            s["kbdi0"], s["nesterov0"] = ek["kbdi"], ek["nesterov"]
        return jsonify({"ok": True, "sonuclar": sonuclar})
    except Exception as e:
        return jsonify({"ok": False, "hata": str(e)}), 400


@app.route("/csv", methods=["POST"])
def csv_hesapla():
    try:
        data = request.get_json()
        satirlar = data["satirlar"]
        ffmc0 = float(data.get("ffmc0", f.FFMC_BASLANGIC))
        dmc0 = float(data.get("dmc0", f.DMC_BASLANGIC))
        dc0 = float(data.get("dc0", f.DC_BASLANGIC))
        kbdi0 = float(data.get("kbdi0", idx.KBDI_BASLANGIC))
        nesterov0 = float(data.get("nesterov0", idx.NESTEROV_BASLANGIC))
        lat_v = float(data["lat"]) if "lat" in data and data["lat"] != "" else None
        sonuclar = []
        for satir in satirlar:
            tarih = str(satir.get("tarih", ""))
            ay = int(tarih[4:6]) if len(tarih) == 8 else int(satir.get("month", 7))
            temp = float(satir["temp"])
            rh = float(satir["rh"])
            wind = float(satir["wind"])
            precip = float(satir["precip"])
            dew_point = float(satir.get("dew_point", 10.0))
            temp_max = float(satir.get("temp_max", temp))
            r = f.hesapla(temp=temp, rh=rh, wind=wind, precip=precip,
                          month=ay, ffmc0=ffmc0, dmc0=dmc0, dc0=dc0, lat=lat_v)
            ek = idx.hesapla_ek(temp=temp, rh=rh, wind=wind, precip=precip,
                                temp_max=temp_max, dew_point=dew_point,
                                kbdi0=kbdi0, nesterov0=nesterov0)
            sonuclar.append({"tarih": tarih, "temp": temp, "rh": rh,
                             "wind_kmh": wind, "precip": precip, **r, **ek})
            ffmc0, dmc0, dc0 = r["ffmc"], r["dmc"], r["dc"]
            kbdi0, nesterov0 = ek["kbdi"], ek["nesterov"]
        return jsonify({"ok": True, "sonuclar": sonuclar})
    except Exception as e:
        return jsonify({"ok": False, "hata": str(e)}), 400


@app.route("/referans", methods=["GET"])
def referans_test():
    import math as _m
    T, H, W, r, ay = 17, 42, 25, 0, 7
    FFMC0, DMC0, DC0 = 85.0, 6.0, 15.0

    mo   = 147.2 * (101.0 - FFMC0) / (59.5 + FFMC0)
    ed   = (0.942 * H**0.679 + 11.0 * _m.exp((H-100)/10)
            + 0.18*(21.1-T)*(1-_m.exp(-0.115*H)))
    ew   = (0.618 * H**0.753 + 10.0 * _m.exp((H-100)/10)
            + 0.18*(21.1-T)*(1-_m.exp(-0.115*H)))
    k0d  = (0.424*(1-(H/100)**1.7) + 0.0694*_m.sqrt(W)*(1-(H/100)**8))
    kd   = k0d * 0.581 * _m.exp(0.0365*T)
    m    = ed + (mo - ed) / (10.0**kd)
    ffmc_val = 59.5*(250-m)/(147.2+m)

    Le   = f.LE_30N[ay-1]
    K    = 1.894*(T+1.1)*(100-H)*Le*0.0001
    dmc_val = DMC0 + K

    Lf   = f.LF_20N[ay-1]
    V    = 0.36*(T+2.8) + Lf
    dc_val = DC0 + 0.5*V

    m_isi = 147.2*(101-ffmc_val)/(59.5+ffmc_val)
    fw   = _m.exp(0.05039*W)
    ff   = 91.9*_m.exp(-0.1386*m_isi)*(1+m_isi**5.31/49300000)
    isi_val = 0.208*fw*ff

    if dmc_val <= 0.4*dc_val:
        bui_yol = "dmc <= 0.4*dc"
        bui_val = 0.8*dmc_val*dc_val/(dmc_val+0.4*dc_val)
    else:
        bui_yol = "dmc > 0.4*dc"
        P = 1 - 0.8*dc_val/(dmc_val+0.4*dc_val)
        bui_val = dmc_val - P*(0.92+(0.0114*dmc_val)**1.7)

    fd   = 0.626*bui_val**0.809 + 2.0
    B    = 0.1*isi_val*fd
    fwi_val = _m.exp(2.72*(0.434*_m.log(B))**0.647) if B > 1 else B

    adimlar = {
        "ffmc": {"mo": round(mo,4), "ed": round(ed,4), "ew": round(ew,4),
                 "k0d": round(k0d,4), "kd": round(kd,4), "m": round(m,4), "sonuc": round(ffmc_val,2)},
        "dmc": {"Le": Le, "K": round(K,4), "sonuc": round(dmc_val,2)},
        "dc": {"Lf": Lf, "V": round(V,4),
               "DC_0+0.5V": f"15 + 0.5x{round(V,4)} = {round(dc_val,4)}", "sonuc": round(dc_val,2)},
        "isi": {"m": round(m_isi,4), "fw": round(fw,4), "ff": round(ff,4), "sonuc": round(isi_val,2)},
        "bui": {"kural": bui_yol, "sonuc": round(bui_val,2)},
        "fwi": {"fd": round(fd,4), "B": round(B,4), "sonuc": round(fwi_val,2)},
    }

    beklenen = {"ffmc": 87.69, "dmc": 8.47, "dc": 21.76, "isi": 10.85, "bui": 8.59, "fwi": 10.14}
    karsilastirma = {}
    for k in beklenen:
        hesaplanan = adimlar[k]["sonuc"]
        fark = abs(hesaplanan - beklenen[k])
        karsilastirma[k] = {"beklenen": beklenen[k], "hesaplanan": hesaplanan,
                            "fark": round(fark,3), "gecti": fark < 0.1}

    return jsonify({"ok": True,
                    "girdi": {"T": T, "H": H, "W": W, "r": r, "ay": ay,
                              "FFMC0": FFMC0, "DMC0": DMC0, "DC0": DC0},
                    "adimlar": adimlar, "karsilastirma": karsilastirma})


# ═══ İSTASYON VERİSİ API ═══
# istasyon modülü yoksa endpoint'ler 503 döner

def _ist_gerekli():
    if ist is None:
        return jsonify({"ok": False, "hata": "İstasyon modülü yüklenmedi"}), 503
    return None

@app.route("/api/station", methods=["POST"])
def station_push():
    """İstasyondan gelen ölçümü kaydet ve indeks hesapla."""
    err = _ist_gerekli()
    if err: return err
    d = request.get_json(force=True)
    station_id = d.get("station_id")
    timestamp  = d.get("timestamp")
    temp       = d.get("temp")
    rh         = d.get("rh")
    wind       = d.get("wind")
    precip     = d.get("precip", 0)

    if not all([station_id, timestamp, temp is not None, rh is not None]):
        return jsonify({"ok": False, "hata": "Eksik alan: station_id, timestamp, temp, rh zorunlu"}), 400

    dew_point = d.get("dew_point")
    temp_max  = d.get("temp_max", temp)

    ist.veri_ekle(station_id, timestamp, temp, rh, wind or 0, precip,
                  dew_point=dew_point, temp_max=temp_max)

    try:
        ek = idx.hesapla_ek(
            temp=float(temp), rh=float(rh), wind=float(wind or 0),
            precip=float(precip), temp_max=float(temp_max or temp),
            dew_point=float(dew_point) if dew_point else 10.0)
        ay = int(timestamp[5:7]) if len(timestamp) >= 7 else 6
        fwi_r = f.hesapla(temp=float(temp), rh=float(rh),
                          wind=float(wind or 0), precip=float(precip),
                          month=ay, ffmc0=85.0, dmc0=6.0, dc0=15.0, lat=39.0)
        indeksler = {**fwi_r, **ek}
    except Exception as e:
        indeksler = {"hata": str(e)}

    return jsonify({"ok": True, "indeksler": indeksler})


@app.route("/api/station/list", methods=["GET"])
def station_list():
    """Kayıtlı istasyonları listele."""
    err = _ist_gerekli()
    if err: return err
    return jsonify({"ok": True, "istasyonlar": ist.istasyon_listele()})


@app.route("/api/station/data", methods=["POST"])
def station_data():
    """İstasyon verisini sorgula ve indeks hesapla."""
    err = _ist_gerekli()
    if err: return err
    d = request.get_json(force=True)
    station_id = d.get("station_id")
    limit      = d.get("limit", 100)

    if not station_id:
        return jsonify({"ok": False, "hata": "station_id zorunlu"}), 400

    okumalar = ist.son_okumalar(station_id, limit=limit)
    if not okumalar:
        return jsonify({"ok": False, "hata": "Bu istasyonda veri bulunamadı"})

    gunluk = ist.gunluk_ozet(okumalar)

    sonuclar = []
    ffmc0, dmc0, dc0, kbdi0, nesterov0 = 85.0, 6.0, 15.0, 0.0, 0.0
    for gun in gunluk:
        try:
            ay = int(gun["tarih"][4:6])
            r = f.hesapla(temp=gun["temp"], rh=gun["rh"],
                          wind=gun["wind_kmh"] or 0, precip=gun["precip"],
                          month=ay, ffmc0=ffmc0, dmc0=dmc0, dc0=dc0, lat=39.0)
            ek = idx.hesapla_ek(
                temp=gun["temp"], rh=gun["rh"],
                wind=gun["wind_kmh"] or 0, precip=gun["precip"],
                temp_max=gun["temp_max"] or gun["temp"],
                dew_point=gun["dew_point"] or 10.0,
                kbdi0=kbdi0, nesterov0=nesterov0)

            ffmc0, dmc0, dc0 = r["ffmc"], r["dmc"], r["dc"]
            kbdi0 = ek["kbdi"]
            nesterov0 = ek["nesterov"]

            sonuclar.append({
                "tarih": gun["tarih"],
                "temp": gun["temp"], "rh": gun["rh"],
                "wind_kmh": gun["wind_kmh"] or 0, "precip": gun["precip"],
                **r, **ek
            })
        except Exception as e:
            sonuclar.append({"tarih": gun["tarih"], "hata": str(e)})

    stats = ist.istatistik(station_id)
    return jsonify({"ok": True, "sonuclar": sonuclar, "istatistik": stats,
                    "ham_okuma_sayisi": len(okumalar)})


@app.route("/api/station/register", methods=["POST"])
def station_register():
    """Yeni istasyon kaydı."""
    err = _ist_gerekli()
    if err: return err
    d = request.get_json(force=True)
    station_id = d.get("station_id")
    isim       = d.get("isim", station_id)
    lat        = d.get("lat", 0)
    lon        = d.get("lon", 0)
    alt        = d.get("alt", 0)
    api_key    = d.get("api_key")

    if not station_id:
        return jsonify({"ok": False, "hata": "station_id zorunlu"}), 400

    ist.istasyon_kaydet(station_id, isim, lat, lon, alt, api_key)
    return jsonify({"ok": True, "mesaj": f"İstasyon '{station_id}' kaydedildi"})


@app.route("/test", methods=["GET"])
def test_yangin():
    olaylar = [
        {"isim_key": "event_1_name",  "isim": "Manavgat Yangını",        "yer": "Antalya",   "tarih": "20210728", "lat": 36.78, "lon": 31.44},
        {"isim_key": "event_2_name",  "isim": "Marmaris Yangını",        "yer": "Muğla",     "tarih": "20210730", "lat": 36.85, "lon": 28.27},
        {"isim_key": "event_3_name",  "isim": "İzmir Yangını",           "yer": "İzmir",     "tarih": "20190819", "lat": 38.42, "lon": 27.14},
        {"isim_key": "event_4_name",  "isim": "Bodrum Yangını",          "yer": "Muğla",     "tarih": "20210729", "lat": 37.04, "lon": 27.43},
        {"isim_key": "event_5_name",  "isim": "Köyceğiz Yangını",        "yer": "Muğla",     "tarih": "20210801", "lat": 36.97, "lon": 28.68},
        {"isim_key": "event_6_name",  "isim": "Aydıncık Yangını",        "yer": "Mersin",    "tarih": "20210728", "lat": 36.15, "lon": 33.32},
        {"isim_key": "event_7_name",  "isim": "Akseki Yangını",          "yer": "Antalya",   "tarih": "20210728", "lat": 37.05, "lon": 31.79},
        {"isim_key": "event_8_name",  "isim": "Milas Yangını",           "yer": "Muğla",     "tarih": "20210802", "lat": 37.28, "lon": 27.78},
        {"isim_key": "event_9_name",  "isim": "Aladağ Yangını",          "yer": "Adana",     "tarih": "20210728", "lat": 37.55, "lon": 35.40},
        {"isim_key": "event_10_name", "isim": "Osmaniye Yangını",        "yer": "Osmaniye",  "tarih": "20210728", "lat": 37.07, "lon": 36.25},
    ]
    sonuclar = []
    for o in olaylar:
        try:
            st = warmup(o["lat"], o["lon"], o["tarih"])
            gunler = om.veri_cek(o["lat"], o["lon"], o["tarih"], o["tarih"])
            if not gunler:
                raise ValueError("Veri alinamadi")
            gun = gunler[0]
            ay  = int(gun["tarih"][4:6])
            r   = f.hesapla(temp=gun["temp"], rh=gun["rh"], wind=gun["wind_kmh"],
                            precip=gun["precip"], month=ay,
                            ffmc0=st["ffmc0"], dmc0=st["dmc0"], dc0=st["dc0"], lat=o["lat"])
            ek  = idx.hesapla_ek(temp=gun["temp"], rh=gun["rh"], wind=gun["wind_kmh"],
                                precip=gun["precip"], temp_max=gun.get("temp_max", gun["temp"]),
                                dew_point=gun.get("dew_point", 10.0),
                                kbdi0=st["kbdi0"], nesterov0=st["nesterov0"])
            sonuclar.append({"isim_key": o["isim_key"], "isim": o["isim"], "yer": o["yer"], "tarih": o["tarih"],
                             "temp": gun["temp"], "rh": gun["rh"],
                             "wind_kmh": gun["wind_kmh"], "precip": gun["precip"], **r, **ek})
        except Exception as e:
            sonuclar.append({"isim_key": o["isim_key"], "isim": o["isim"], "yer": o["yer"], "tarih": o["tarih"], "hata": str(e)})
    return jsonify({"ok": True, "sonuclar": sonuclar})


@app.route("/rapor-pdf", methods=["POST"])
def rapor_pdf():
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    )
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    font_candidates = [
        (r"C:\Windows\Fonts\arial.ttf", "Arial", r"C:\Windows\Fonts\arialbd.ttf", "Arial-Bold"),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "DejaVu",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "DejaVu-Bold"),
    ]
    FR, FB = "Helvetica", "Helvetica-Bold"
    for reg_path, reg_name, bold_path, bold_name in font_candidates:
        if os.path.exists(reg_path):
            try:
                pdfmetrics.registerFont(TTFont(reg_name, reg_path))
                if os.path.exists(bold_path):
                    pdfmetrics.registerFont(TTFont(bold_name, bold_path))
                else:
                    bold_name = reg_name
                FR, FB = reg_name, bold_name
                break
            except Exception:
                pass

    BLACK  = colors.HexColor("#1a1a1a")
    DARK   = colors.HexColor("#2c2c2c")
    MEDIUM = colors.HexColor("#555555")
    MUTED  = colors.HexColor("#888888")
    ACCENT = colors.HexColor("#b85000")
    BLUE   = colors.HexColor("#1a5a8a")
    GREEN  = colors.HexColor("#1a6b2a")
    RED    = colors.HexColor("#a01010")
    BGCARD = colors.HexColor("#f4f6f8")
    BGHEAD = colors.HexColor("#e8edf2")
    BORDER = colors.HexColor("#ccd4dd")

    def S(name, **kw):
        base = dict(fontName=FR, fontSize=10, leading=15,
                    textColor=BLACK, spaceAfter=0, spaceBefore=0)
        base.update(kw)
        return ParagraphStyle(name, **base)

    sTitle  = S("rTitle",  fontName=FB, fontSize=16, textColor=ACCENT, leading=22, spaceAfter=4)
    sSub    = S("rSub",    fontSize=9, textColor=MEDIUM, leading=13)
    sH1     = S("rH1",     fontName=FB, fontSize=11, textColor=ACCENT, leading=16, spaceBefore=14, spaceAfter=6)
    sBody   = S("rBody",   fontSize=9.5, textColor=DARK, leading=15, spaceAfter=4)
    sBold   = S("rBold",   fontName=FB, fontSize=9.5, textColor=BLACK, leading=15)
    sFooter = S("rFooter", fontSize=7.5, textColor=MUTED, leading=12, alignment=1)

    def HR():
        return HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceAfter=8, spaceBefore=2)

    data = request.get_json()
    tip = data.get("tip", "manuel")

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
        leftMargin=2.2*cm, rightMargin=2.2*cm,
        topMargin=2*cm, bottomMargin=1.8*cm,
        title="FWI Hesaplama Raporu")

    story = []
    now = datetime.now().strftime("%d.%m.%Y %H:%M")

    story.append(Paragraph("FWI Hesaplama Raporu", sTitle))
    story.append(Paragraph(f"Olusturma tarihi: {now}", sSub))
    story.append(Spacer(1, 6))
    story.append(HR())

    sinif_tr = {"Dusuk": "Dusuk", "Orta": "Orta", "Yuksek": "Yuksek",
                "Cok Yuksek": "Cok Yuksek", "Asiri": "Asiri"}
    sinif_renk = {"Dusuk": GREEN, "Orta": colors.HexColor("#8a7a00"),
                  "Yuksek": colors.HexColor("#b86800"), "Cok Yuksek": RED,
                  "Asiri": colors.HexColor("#880088")}

    if tip == "manuel":
        girdi = data.get("girdi", {})
        sonuc = data.get("sonuc", {})

        story.append(Paragraph("Girdi Degerleri", sH1))
        girdi_rows = [
            [Paragraph("Parametre", sBold), Paragraph("Deger", sBold)],
            [Paragraph("Sicaklik", sBody), Paragraph(f"{girdi.get('temp', '-')} C", sBody)],
            [Paragraph("Bagil Nem", sBody), Paragraph(f"%{girdi.get('rh', '-')}", sBody)],
            [Paragraph("Ruzgar Hizi", sBody), Paragraph(f"{girdi.get('wind', '-')} km/h", sBody)],
            [Paragraph("Yagis", sBody), Paragraph(f"{girdi.get('precip', '-')} mm", sBody)],
            [Paragraph("Ay", sBody), Paragraph(f"{girdi.get('month', '-')}", sBody)],
        ]
        if girdi.get("lat"):
            girdi_rows.append([Paragraph("Enlem", sBody), Paragraph(f"{girdi['lat']}", sBody)])

        t = Table(girdi_rows, colWidths=[6*cm, 10*cm], hAlign="LEFT")
        t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), BGHEAD),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, BGCARD]),
            ("BOX", (0,0), (-1,-1), 0.5, BORDER),
            ("LINEBELOW", (0,0), (-1,-2), 0.3, BORDER),
            ("TOPPADDING", (0,0), (-1,-1), 6),
            ("BOTTOMPADDING", (0,0), (-1,-1), 6),
            ("LEFTPADDING", (0,0), (-1,-1), 10),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ]))
        story.append(t)
        story.append(Spacer(1, 10))

        sinif = sonuc.get("sinif", "Orta")
        fwi_val = sonuc.get("fwi", 0)
        renk = sinif_renk.get(sinif, DARK)

        story.append(Paragraph("Sonuc", sH1))
        story.append(Paragraph(
            f"Tehlike Sinifi: <b>{sinif_tr.get(sinif, sinif)}</b>  |  FWI = <b>{fwi_val}</b>",
            S("rSonuc", fontName=FR, fontSize=12, textColor=renk, leading=18)))
        story.append(Spacer(1, 8))

        indeks_rows = [
            [Paragraph("Indeks", sBold), Paragraph("Deger", sBold), Paragraph("Aciklama", sBold)],
            [Paragraph("FFMC", sBody), Paragraph(str(sonuc.get("ffmc","-")), sBody), Paragraph("Ince Ust Tabaka Yanici Madde Nem Kodu", sBody)],
            [Paragraph("DMC", sBody), Paragraph(str(sonuc.get("dmc","-")), sBody), Paragraph("Dokuntu Nem Kodu", sBody)],
            [Paragraph("DC", sBody), Paragraph(str(sonuc.get("dc","-")), sBody), Paragraph("Derin Organik Tabaka Nem Kodu", sBody)],
            [Paragraph("ISI", sBody), Paragraph(str(sonuc.get("isi","-")), sBody), Paragraph("Baslangic Yayilma Indeksi", sBody)],
            [Paragraph("BUI", sBody), Paragraph(str(sonuc.get("bui","-")), sBody), Paragraph("Birikmis Yanici Madde Indeksi", sBody)],
            [Paragraph("FWI", sBody), Paragraph(str(sonuc.get("fwi","-")), sBold), Paragraph("Yangin Hava Indeksi — Van Wagner (1987)", sBody)],
            [Paragraph("DSR", sBody), Paragraph(str(sonuc.get("dsr","-")), sBody), Paragraph("Gunluk Siddet Orani", sBody)],
            [Paragraph("Angstrom", sBody), Paragraph(str(sonuc.get("angstrom","-")), sBody), Paragraph("Anlik Yangin Tehlike — Angstrom (1942)", sBody)],
            [Paragraph("Nesterov", sBody), Paragraph(str(sonuc.get("nesterov","-")), sBody), Paragraph("Kumulatif Kuraklik — Nesterov (1949)", sBody)],
            [Paragraph("KBDI", sBody), Paragraph(str(sonuc.get("kbdi","-")), sBody), Paragraph("Toprak Nem Eksikligi — Keetch-Byram (1968)", sBody)],
            [Paragraph("Carrega", sBody), Paragraph(str(sonuc.get("carrega","-")), sBody), Paragraph("Akdeniz Yangin Indeksi — Carrega I87 (1991)", sBody)],
        ]
        t2 = Table(indeks_rows, colWidths=[3*cm, 3*cm, 10*cm], hAlign="LEFT")
        t2.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), BGHEAD),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, BGCARD]),
            ("BOX", (0,0), (-1,-1), 0.5, BORDER),
            ("LINEBELOW", (0,0), (-1,-2), 0.3, BORDER),
            ("TOPPADDING", (0,0), (-1,-1), 6),
            ("BOTTOMPADDING", (0,0), (-1,-1), 6),
            ("LEFTPADDING", (0,0), (-1,-1), 10),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ]))
        story.append(t2)

    elif tip == "coklu":
        satirlar = data.get("satirlar", [])
        meta = data.get("meta", {})

        if meta:
            story.append(Paragraph("Sorgu Bilgileri", sH1))
            meta_text = []
            if meta.get("lat"): meta_text.append(f"Konum: {meta['lat']}, {meta['lon']}")
            if meta.get("baslangic"): meta_text.append(f"Donem: {meta['baslangic']} - {meta['bitis']}")
            meta_text.append(f"Toplam gun: {len(satirlar)}")
            story.append(Paragraph("  |  ".join(meta_text), sBody))
            story.append(Spacer(1, 8))

        if satirlar:
            fwi_list = [r["fwi"] for r in satirlar]
            max_fwi = max(fwi_list)
            max_gun = next((r for r in satirlar if r["fwi"] == max_fwi), None)
            ort_fwi = sum(fwi_list) / len(fwi_list)
            asiri = sum(1 for v in fwi_list if v >= 30)
            cok_yuksek = sum(1 for v in fwi_list if v >= 20)

            story.append(Paragraph("Istatistikler", sH1))
            stat_rows = [
                [Paragraph("Metrik", sBold), Paragraph("Deger", sBold)],
                [Paragraph("En Yuksek FWI", sBody),
                 Paragraph(f"{max_fwi} ({max_gun['tarih'][:4]}-{max_gun['tarih'][4:6]}-{max_gun['tarih'][6:8]})" if max_gun else str(max_fwi), sBody)],
                [Paragraph("Ortalama FWI", sBody), Paragraph(f"{ort_fwi:.1f}", sBody)],
                [Paragraph("Asiri Gun (FWI >= 30)", sBody), Paragraph(str(asiri), sBody)],
                [Paragraph("Cok Yuksek+ Gun (FWI >= 20)", sBody), Paragraph(str(cok_yuksek), sBody)],
            ]
            ts = Table(stat_rows, colWidths=[8*cm, 8*cm], hAlign="LEFT")
            ts.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,0), BGHEAD),
                ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, BGCARD]),
                ("BOX", (0,0), (-1,-1), 0.5, BORDER),
                ("LINEBELOW", (0,0), (-1,-2), 0.3, BORDER),
                ("TOPPADDING", (0,0), (-1,-1), 6),
                ("BOTTOMPADDING", (0,0), (-1,-1), 6),
                ("LEFTPADDING", (0,0), (-1,-1), 10),
                ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ]))
            story.append(ts)
            story.append(Spacer(1, 12))

        story.append(Paragraph("Gunluk Sonuclar", sH1))
        header = [Paragraph(h, S("rTH", fontName=FB, fontSize=7, textColor=BLUE, leading=10))
                  for h in ["Tarih","T","RH","W","P","FWI","Sinif","Ang.","Nes.","KBDI","Car."]]
        rows = [header]
        sSatir = S("rTD", fontSize=6.5, textColor=DARK, leading=9)
        sSatirB = S("rTDB", fontName=FB, fontSize=6.5, textColor=DARK, leading=9)

        for r in satirlar:
            tarih = f"{r['tarih'][:4]}-{r['tarih'][4:6]}-{r['tarih'][6:8]}" if len(str(r.get('tarih',''))) == 8 else str(r.get('tarih',''))
            sinif = r.get("sinif", "")
            renk = sinif_renk.get(sinif, DARK)
            sSinif = S(f"rSn_{id(r)}", fontName=FB, fontSize=6.5, textColor=renk, leading=9)
            nes_val = r.get("nesterov", "")
            if isinstance(nes_val, (int, float)) and abs(nes_val) >= 1000:
                nes_val = f"{nes_val/1000:.1f}K"
            rows.append([
                Paragraph(tarih, sSatir),
                Paragraph(f"{r.get('temp',0):.1f}", sSatir),
                Paragraph(f"{r.get('rh',0):.0f}", sSatir),
                Paragraph(f"{r.get('wind_kmh',0):.1f}", sSatir),
                Paragraph(f"{r.get('precip',0):.1f}", sSatir),
                Paragraph(str(r.get("fwi","")), sSatirB),
                Paragraph(sinif_tr.get(sinif, sinif), sSinif),
                Paragraph(str(r.get("angstrom","")), sSatir),
                Paragraph(str(nes_val), sSatir),
                Paragraph(str(r.get("kbdi","")), sSatir),
                Paragraph(str(r.get("carrega","")), sSatir),
            ])

        cw = [2*cm, 1*cm, 1*cm, 1*cm, 1*cm, 1.2*cm, 1.6*cm, 1.1*cm, 1.3*cm, 1.2*cm, 1.1*cm]
        tbl = Table(rows, colWidths=cw, hAlign="LEFT", repeatRows=1)
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), BGHEAD),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, BGCARD]),
            ("BOX", (0,0), (-1,-1), 0.5, BORDER),
            ("LINEBELOW", (0,0), (-1,-1), 0.2, BORDER),
            ("TOPPADDING", (0,0), (-1,-1), 4),
            ("BOTTOMPADDING", (0,0), (-1,-1), 4),
            ("LEFTPADDING", (0,0), (-1,-1), 4),
            ("RIGHTPADDING", (0,0), (-1,-1), 4),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ]))
        story.append(tbl)

    story.append(Spacer(1, 20))
    story.append(HR())
    story.append(Paragraph("Fire-EWS  |  FWI + Angstrom + Nesterov + KBDI + Carrega I87", sFooter))
    story.append(Paragraph(f"Rapor olusturma: {now}", sFooter))

    doc.build(story)
    buf.seek(0)
    return send_file(buf, mimetype="application/pdf",
                     as_attachment=True, download_name="fwi_rapor.pdf")


@app.route("/tahmin", methods=["POST"])
def tahmin():
    try:
        data = request.get_json()
        lat = float(data["lat"])
        lon = float(data["lon"])
        s = warmup(lat, lon, datetime.now().strftime("%Y%m%d"))
        gunler = fc.tahmin_cek(lat, lon)
        sonuclar = []
        for gun in gunler:
            ay = int(gun["tarih"][4:6])
            r = f.hesapla(temp=gun["temp"], rh=gun["rh"], wind=gun["wind_kmh"],
                          precip=gun["precip"], month=ay,
                          ffmc0=s["ffmc0"], dmc0=s["dmc0"], dc0=s["dc0"], lat=lat)
            ek = idx.hesapla_ek(temp=gun["temp"], rh=gun["rh"], wind=gun["wind_kmh"],
                                precip=gun["precip"], temp_max=gun.get("temp_max", gun["temp"]),
                                dew_point=gun.get("dew_point", 10.0),
                                kbdi0=s["kbdi0"], nesterov0=s["nesterov0"])
            sonuclar.append({"tarih": gun["tarih"], "temp": gun["temp"],
                             "rh": gun["rh"], "wind_kmh": gun["wind_kmh"],
                             "precip": gun["precip"], **r, **ek})
            s["ffmc0"], s["dmc0"], s["dc0"] = r["ffmc"], r["dmc"], r["dc"]
            s["kbdi0"], s["nesterov0"] = ek["kbdi"], ek["nesterov"]
        return jsonify({"ok": True, "sonuclar": sonuclar})
    except Exception as e:
        return jsonify({"ok": False, "hata": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=False, port=5002)
