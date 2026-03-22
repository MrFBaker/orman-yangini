# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify, send_file
from datetime import datetime, timedelta
import sys, os, io
sys.path.insert(0, os.path.dirname(__file__))
import fwi_hesap as f
import openmeteo as om
import forecast as fc

app = Flask(__name__)


def warmup_fwi(lat, lon, baslangic):
    jan1 = baslangic[:4] + "0101"
    if baslangic <= jan1:
        return f.FFMC_BASLANGIC, f.DMC_BASLANGIC, f.DC_BASLANGIC
    prev_str = (datetime.strptime(baslangic, "%Y%m%d") - timedelta(days=1)).strftime("%Y%m%d")
    gunler = om.veri_cek(lat, lon, jan1, prev_str)
    ffmc0, dmc0, dc0 = f.FFMC_BASLANGIC, f.DMC_BASLANGIC, f.DC_BASLANGIC
    for gun in gunler:
        ay = int(gun["tarih"][4:6])
        r = f.hesapla(temp=gun["temp"], rh=gun["rh"], wind=gun["wind_kmh"],
                      precip=gun["precip"], month=ay, ffmc0=ffmc0, dmc0=dmc0, dc0=dc0, lat=lat)
        ffmc0, dmc0, dc0 = r["ffmc"], r["dmc"], r["dc"]
    return ffmc0, dmc0, dc0


@app.route("/")
def index():
    return render_template("index_v2.html")


@app.route("/hesapla", methods=["POST"])
def hesapla():
    try:
        data = request.get_json()
        lat_v = float(data["lat"]) if "lat" in data and data["lat"] != "" else None
        sonuc = f.hesapla(
            temp=float(data["temp"]), rh=float(data["rh"]),
            wind=float(data["wind"]), precip=float(data["precip"]),
            month=int(data["month"]),
            ffmc0=float(data.get("ffmc0", f.FFMC_BASLANGIC)),
            dmc0=float(data.get("dmc0", f.DMC_BASLANGIC)),
            dc0=float(data.get("dc0", f.DC_BASLANGIC)),
            lat=lat_v,
        )
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
        ffmc0, dmc0, dc0 = warmup_fwi(lat, lon, baslangic)
        sonuclar = []
        for gun in gunler:
            ay = int(gun["tarih"][4:6])
            r = f.hesapla(temp=gun["temp"], rh=gun["rh"], wind=gun["wind_kmh"],
                          precip=gun["precip"], month=ay, ffmc0=ffmc0, dmc0=dmc0, dc0=dc0, lat=lat)
            sonuclar.append({"tarih": gun["tarih"], "temp": gun["temp"], "rh": gun["rh"],
                             "wind_kmh": gun["wind_kmh"], "precip": gun["precip"], **r})
            ffmc0, dmc0, dc0 = r["ffmc"], r["dmc"], r["dc"]
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
        lat_v = float(data["lat"]) if "lat" in data and data["lat"] != "" else None
        sonuclar = []
        for satir in satirlar:
            tarih = str(satir.get("tarih", ""))
            ay = int(tarih[4:6]) if len(tarih) == 8 else int(satir.get("month", 7))
            r = f.hesapla(temp=float(satir["temp"]), rh=float(satir["rh"]),
                          wind=float(satir["wind"]), precip=float(satir["precip"]),
                          month=ay, ffmc0=ffmc0, dmc0=dmc0, dc0=dc0, lat=lat_v)
            sonuclar.append({"tarih": tarih, "temp": float(satir["temp"]), "rh": float(satir["rh"]),
                             "wind_kmh": float(satir["wind"]), "precip": float(satir["precip"]), **r})
            ffmc0, dmc0, dc0 = r["ffmc"], r["dmc"], r["dc"]
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


@app.route("/test", methods=["GET"])
def test_yangin():
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
            r   = f.hesapla(temp=gun["temp"], rh=gun["rh"], wind=gun["wind_kmh"],
                            precip=gun["precip"], month=ay,
                            ffmc0=ffmc0, dmc0=dmc0, dc0=dc0, lat=o["lat"])
            sonuclar.append({"isim": o["isim"], "yer": o["yer"], "tarih": o["tarih"],
                             "temp": gun["temp"], "rh": gun["rh"],
                             "wind_kmh": gun["wind_kmh"], "precip": gun["precip"], **r})
        except Exception as e:
            sonuclar.append({"isim": o["isim"], "yer": o["yer"], "tarih": o["tarih"], "hata": str(e)})
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
            [Paragraph("FWI", sBody), Paragraph(str(sonuc.get("fwi","-")), sBold), Paragraph("Yangin Hava Indeksi", sBody)],
            [Paragraph("DSR", sBody), Paragraph(str(sonuc.get("dsr","-")), sBody), Paragraph("Gunluk Siddet Orani", sBody)],
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
        header = [Paragraph(h, S("rTH", fontName=FB, fontSize=7.5, textColor=BLUE, leading=11))
                  for h in ["Tarih","T(C)","RH(%)","Ruzgar","Yagis","FFMC","DMC","DC","ISI","BUI","FWI","Sinif"]]
        rows = [header]
        sSatir = S("rTD", fontSize=7, textColor=DARK, leading=10)
        sSatirB = S("rTDB", fontName=FB, fontSize=7, textColor=DARK, leading=10)

        for r in satirlar:
            tarih = f"{r['tarih'][:4]}-{r['tarih'][4:6]}-{r['tarih'][6:8]}" if len(str(r.get('tarih',''))) == 8 else str(r.get('tarih',''))
            sinif = r.get("sinif", "")
            renk = sinif_renk.get(sinif, DARK)
            sSinif = S(f"rSn_{id(r)}", fontName=FB, fontSize=7, textColor=renk, leading=10)
            rows.append([
                Paragraph(tarih, sSatir),
                Paragraph(f"{r.get('temp',0):.1f}", sSatir),
                Paragraph(f"{r.get('rh',0):.0f}", sSatir),
                Paragraph(f"{r.get('wind_kmh',0):.1f}", sSatir),
                Paragraph(f"{r.get('precip',0):.1f}", sSatir),
                Paragraph(str(r.get("ffmc","")), sSatir),
                Paragraph(str(r.get("dmc","")), sSatir),
                Paragraph(str(r.get("dc","")), sSatir),
                Paragraph(str(r.get("isi","")), sSatir),
                Paragraph(str(r.get("bui","")), sSatir),
                Paragraph(str(r.get("fwi","")), sSatirB),
                Paragraph(sinif_tr.get(sinif, sinif), sSinif),
            ])

        cw = [2*cm, 1.2*cm, 1.2*cm, 1.2*cm, 1.2*cm, 1.3*cm, 1.3*cm, 1.3*cm, 1.2*cm, 1.2*cm, 1.2*cm, 1.8*cm]
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
    story.append(Paragraph("FWI Yangin Erken Uyari Sistemi  |  Van Wagner (1987)", sFooter))
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
        ffmc0, dmc0, dc0 = warmup_fwi(lat, lon,
                                        datetime.now().strftime("%Y%m%d"))
        gunler = fc.tahmin_cek(lat, lon)
        sonuclar = []
        for gun in gunler:
            ay = int(gun["tarih"][4:6])
            r = f.hesapla(temp=gun["temp"], rh=gun["rh"], wind=gun["wind_kmh"],
                          precip=gun["precip"], month=ay,
                          ffmc0=ffmc0, dmc0=dmc0, dc0=dc0, lat=lat)
            sonuclar.append({"tarih": gun["tarih"], "temp": gun["temp"],
                             "rh": gun["rh"], "wind_kmh": gun["wind_kmh"],
                             "precip": gun["precip"], **r})
            ffmc0, dmc0, dc0 = r["ffmc"], r["dmc"], r["dc"]
        return jsonify({"ok": True, "sonuclar": sonuclar})
    except Exception as e:
        return jsonify({"ok": False, "hata": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=False, port=5002)
