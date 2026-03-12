# -*- coding: utf-8 -*-
"""
FWI (Fire Weather Index) Hesaplama Modülü
Kaynak: Van Wagner (1987) — Canadian Forest Fire Weather Index System
Referans kod: mesowx/CFFDRS, gagreene/cffdrs
"""

import math

# --- AYLIK FAKTÖR TABLOLARI (Van Wagner 1987 / gagreene cffdrs) ---

# Le: DMC gün uzunluğu faktörü
LE_30N  = [6.5, 7.5, 9.0, 12.8, 13.9, 13.9, 12.4, 10.9, 9.4, 8.0, 7.0, 6.0]   # lat >= 30
LE_10N  = [7.9, 8.4, 8.9, 9.5,  9.9,  10.2, 10.1, 9.7,  9.1, 8.6, 8.1, 7.8]   # 10 <= lat < 30
LE_EQ   = [9.0]*12                                                                  # -10 <= lat < 10
LE_10S  = [10.1,9.6, 9.1, 8.5,  8.1,  7.8,  7.9,  8.3,  8.9, 9.4, 9.9, 10.2]  # -30 <= lat < -10
LE_30S  = [11.5,10.5,9.2, 7.9,  6.8,  6.2,  6.5,  7.4,  8.7, 10.0,11.2,11.8]  # lat < -30

# Lf: DC gün uzunluğu faktörü
LF_20N  = [-1.6,-1.6,-1.6, 0.9,  3.8,  5.8,  6.4,  5.0,  2.4, 0.4,-1.6,-1.6]  # lat >= 20
LF_EQ   = [1.4]*12                                                                  # -20 <= lat < 20
LF_20S  = [6.4, 5.0, 2.4, 0.4, -1.6, -1.6, -1.6, -1.6, -1.6, 0.9, 3.8, 5.8]  # lat < -20

# Varsayılan: Türkiye (lat ~37-42°N)
LE = LE_30N
LF = LF_20N


def enleme_gore_tablolar(lat):
    """Enleme göre Le ve Lf tablolarını döndürür."""
    if lat >= 30:
        le = LE_30N
    elif lat >= 10:
        le = LE_10N
    elif lat >= -10:
        le = LE_EQ
    elif lat >= -30:
        le = LE_10S
    else:
        le = LE_30S

    if lat >= 20:
        lf = LF_20N
    elif lat >= -20:
        lf = LF_EQ
    else:
        lf = LF_20S

    return le, lf

# --- BAŞLANGIÇ DEĞERLERİ (sezon başı) ---
FFMC_BASLANGIC = 85.0
DMC_BASLANGIC  = 6.0
DC_BASLANGIC   = 15.0


def ffmc(temp, rh, wind, precip, ffmc0):
    """
    Fine Fuel Moisture Code (İnce Üst Tabaka Yanıcı Madde Nem Kodu — İYMNK)

    Parametreler:
        temp   : sıcaklık (°C), öğlen ölçümü
        rh     : bağıl nem (%), öğlen ölçümü
        wind   : rüzgar hızı (km/h), öğlen ölçümü
        precip : 24 saatlik yağış (mm)
        ffmc0  : önceki günün FFMC değeri

    Döndürür:
        float — güncel FFMC değeri (0–101)
    """
    # Sıcaklık alt sınırı
    if temp < -1.1:
        temp = -1.1

    # Adım 1: Önceki nem içeriğine dönüştür
    mo = 147.2 * (101.0 - ffmc0) / (59.5 + ffmc0)

    # Adım 2: Yağış düzeltmesi
    if precip > 0.5:
        rf = precip - 0.5
        delta = 42.5 * rf * math.exp(-100.0 / (251.0 - mo)) * (1.0 - math.exp(-6.93 / rf))
        if mo > 150.0:
            delta += 0.0015 * (mo - 150.0) ** 2 * math.sqrt(rf)
        mo = mo + delta
        if mo > 250.0:
            mo = 250.0

    # Adım 3: Denge nem içeriği
    ed = (0.942 * rh ** 0.679
          + 11.0 * math.exp((rh - 100.0) / 10.0)
          + 0.18 * (21.1 - temp) * (1.0 - math.exp(-0.115 * rh)))

    ew = (0.618 * rh ** 0.753
          + 10.0 * math.exp((rh - 100.0) / 10.0)
          + 0.18 * (21.1 - temp) * (1.0 - math.exp(-0.115 * rh)))

    # Adım 4: Kuruma / ıslanma oranı ve nem içeriği
    if mo < ed and mo < ew:
        k0w = (0.424 * (1.0 - ((100.0 - rh) / 100.0) ** 1.7)
               + 0.0694 * math.sqrt(wind) * (1.0 - ((100.0 - rh) / 100.0) ** 8.0))
        kw = k0w * 0.581 * math.exp(0.0365 * temp)
        m = ew - (ew - mo) / (10.0 ** kw)
    elif mo > ed:
        k0d = (0.424 * (1.0 - (rh / 100.0) ** 1.7)
               + 0.0694 * math.sqrt(wind) * (1.0 - (rh / 100.0) ** 8.0))
        kd = k0d * 0.581 * math.exp(0.0365 * temp)
        m = ed + (mo - ed) / (10.0 ** kd)
    else:
        m = mo

    # Adım 5: FFMC değerine dönüştür
    result = 59.5 * (250.0 - m) / (147.2 + m)
    return max(0.0, min(101.0, result))


def dmc(temp, rh, precip, dmc0, month, le_tablo=None):
    """
    Duff Moisture Code (Humus Nem Kodu)

    Parametreler:
        temp   : sıcaklık (°C), öğlen ölçümü
        rh     : bağıl nem (%), öğlen ölçümü
        precip : 24 saatlik yağış (mm)
        dmc0   : önceki günün DMC değeri
        month  : ay (1–12)

    Döndürür:
        float — güncel DMC değeri (≥ 0)
    """
    # Sıcaklık alt sınırı
    if temp < -1.1:
        temp = -1.1

    le = (le_tablo if le_tablo is not None else LE)[month - 1]

    # Adım 1: Önceki nem içeriği
    mo = 20.0 + 280.0 / math.exp(0.023 * dmc0)

    # Adım 2: Yağış düzeltmesi
    pr = dmc0
    if precip > 1.5:
        re = 0.92 * precip - 1.27
        if dmc0 > 65.0:
            b = 6.2 * math.log(dmc0) - 17.2
        elif dmc0 > 33.0:
            b = 14.0 - 1.3 * math.log(dmc0)
        else:
            b = 100.0 / (0.5 + 0.3 * dmc0)
        mr = mo + 1000.0 * re / (48.77 + b * re)
        mr = max(mr, 0.0)
        pr = 244.72 - 43.43 * math.log(mr - 20.0)
        pr = max(pr, 0.0)

    # Adım 3: Günlük kuruma oranı
    k = 1.894 * (temp + 1.1) * (100.0 - rh) * le * 0.0001

    result = pr + k
    return max(0.0, result)


def dc(temp, precip, dc0, month, lf_tablo=None):
    """
    Drought Code (Derin Organik Tabaka Nem Kodu — DONK)

    Parametreler:
        temp   : sıcaklık (°C), öğlen ölçümü
        precip : 24 saatlik yağış (mm)
        dc0    : önceki günün DC değeri
        month  : ay (1–12)

    Döndürür:
        float — güncel DC değeri (≥ 0)
    """
    # Sıcaklık alt sınırı
    if temp < -2.8:
        temp = -2.8

    lf = (lf_tablo if lf_tablo is not None else LF)[month - 1]

    # Adım 1: Önceki nem eşdeğeri
    q0 = 800.0 / math.exp(dc0 / 400.0)

    # Adım 2: Yağış düzeltmesi
    dr = dc0
    if precip > 2.8:
        rd = 0.83 * precip - 1.27
        qr = q0 + 3.937 * rd
        dr = 400.0 * math.log(800.0 / qr)
        dr = max(dr, 0.0)

    # Adım 3: Potansiyel evapotranspirasyon
    v = 0.36 * (temp + 2.8) + lf
    v = max(v, 0.0)

    result = dr + 0.5 * v
    return max(0.0, result)


def isi(ffmc_val, wind):
    """
    Initial Spread Index (İlk Yayılma İndeksi)

    Parametreler:
        ffmc_val : güncel FFMC değeri
        wind     : rüzgar hızı (km/h), öğlen ölçümü

    Döndürür:
        float — ISI değeri (≥ 0)
    """
    m  = 147.2 * (101.0 - ffmc_val) / (59.5 + ffmc_val)
    fw = math.exp(0.05039 * wind)
    ff = 91.9 * math.exp(-0.1386 * m) * (1.0 + m ** 5.31 / 49300000.0)
    result = 0.208 * fw * ff
    return max(0.0, result)


def bui(dmc_val, dc_val):
    """
    Build Up Index (Birikmiş Yanıcı Madde İndeksi)

    Parametreler:
        dmc_val : güncel DMC değeri
        dc_val  : güncel DC değeri

    Döndürür:
        float — BUI değeri (≥ 0)
    """
    if dmc_val == 0.0:
        return 0.0

    if dmc_val <= 0.4 * dc_val:
        result = 0.8 * dmc_val * dc_val / (dmc_val + 0.4 * dc_val)
    else:
        result = dmc_val - (1.0 - 0.8 * dc_val / (dmc_val + 0.4 * dc_val)) * (0.92 + (0.0114 * dmc_val) ** 1.7)

    return max(0.0, result)


def fwi(isi_val, bui_val):
    """
    Fire Weather Index (Yangın Hava İndeksi)

    Parametreler:
        isi_val : güncel ISI değeri
        bui_val : güncel BUI değeri

    Döndürür:
        float — FWI değeri (≥ 0)
    """
    if bui_val <= 80.0:
        fd = 0.626 * bui_val ** 0.809 + 2.0
    else:
        fd = 1000.0 / (25.0 + 108.64 * math.exp(-0.023 * bui_val))

    b = 0.1 * isi_val * fd

    if b <= 1.0:
        result = b
    else:
        result = math.exp(2.72 * (0.434 * math.log(b)) ** 0.647)

    return max(0.0, result)


def dsr(fwi_val):
    """
    Daily Severity Rating (Günlük Şiddet Değerlendirmesi)

    Parametreler:
        fwi_val : güncel FWI değeri

    Döndürür:
        float — DSR değeri (≥ 0)
    """
    return 0.0272 * fwi_val ** 1.77


def fwi_sinif(fwi_val):
    """
    FWI tehlike sınıfını döndürür.

    Parametreler:
        fwi_val : FWI değeri

    Döndürür:
        str — "Düşük" / "Orta" / "Yüksek" / "Çok Yüksek" / "Aşırı"
    """
    if fwi_val < 5.0:
        return "Dusuk"
    elif fwi_val < 10.0:
        return "Orta"
    elif fwi_val < 20.0:
        return "Yuksek"
    elif fwi_val < 30.0:
        return "Cok Yuksek"
    else:
        return "Asiri"


def hesapla(temp, rh, wind, precip, month,
            ffmc0=FFMC_BASLANGIC, dmc0=DMC_BASLANGIC, dc0=DC_BASLANGIC,
            lat=None):
    """
    Tüm FWI bileşenlerini hesaplar.

    Parametreler:
        temp   : sıcaklık (°C)
        rh     : bağıl nem (%)
        wind   : rüzgar hızı (km/h)
        precip : 24 saatlik yağış (mm)
        month  : ay (1–12)
        ffmc0  : önceki gün FFMC (varsayılan: 85)
        dmc0   : önceki gün DMC  (varsayılan: 6)
        dc0    : önceki gün DC   (varsayılan: 15)

    Döndürür:
        dict — tüm indeks değerleri ve tehlike sınıfı
    """
    le_t, lf_t = enleme_gore_tablolar(lat) if lat is not None else (None, None)
    ffmc_val = ffmc(temp, rh, wind, precip, ffmc0)
    dmc_val  = dmc(temp, rh, precip, dmc0, month, le_tablo=le_t)
    dc_val   = dc(temp, precip, dc0, month, lf_tablo=lf_t)
    isi_val  = isi(ffmc_val, wind)
    bui_val  = bui(dmc_val, dc_val)
    fwi_val  = fwi(isi_val, bui_val)
    dsr_val  = dsr(fwi_val)
    sinif    = fwi_sinif(fwi_val)

    return {
        "ffmc":  round(ffmc_val, 2),
        "dmc":   round(dmc_val, 2),
        "dc":    round(dc_val, 2),
        "isi":   round(isi_val, 2),
        "bui":   round(bui_val, 2),
        "fwi":   round(fwi_val, 2),
        "dsr":   round(dsr_val, 2),
        "sinif": sinif
    }


# --- TEST (doğrulama) ---
if __name__ == "__main__":
    # Van Wagner (1987) referans değerleri
    # Girdi: temp=17°C, rh=42%, wind=25 km/h, precip=0 mm, month=7
    # Başlangıç: ffmc0=85, dmc0=6, dc0=15
    sonuc = hesapla(
        temp=17, rh=42, wind=25, precip=0,
        month=7,
        ffmc0=85, dmc0=6, dc0=15
    )

    print("=== FWI Hesaplama Sonuclari ===")
    for k, v in sonuc.items():
        print(f"  {k.upper():6s}: {v}")
