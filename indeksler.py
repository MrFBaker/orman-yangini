# -*- coding: utf-8 -*-
"""
Ek Yangın Tehlike İndeksleri Hesaplama Modülü

Bu modül, FWI (Van Wagner 1987) dışındaki dört yangın tehlike indeksini hesaplar:
  1. Angström İndeksi   — Angström (1942)
  2. Nesterov İndeksi   — Nesterov (1949)
  3. KBDI               — Keetch & Byram (1968)
  4. Carrega I87         — Carrega (1991)

Her fonksiyon bilimsel kaynağına sadık kalarak uygulanmıştır.
"""

import math

# ═══════════════════════════════════════════════════════════════
#  BAŞLANGIÇ DEĞERLERİ
# ═══════════════════════════════════════════════════════════════

KBDI_BASLANGIC = 0       # Doygun toprak (kış sonu / sezon başı)
NESTEROV_BASLANGIC = 0   # Kümülatif indeks sıfırdan başlar


# ═══════════════════════════════════════════════════════════════
#  1. ANGSTRÖM İNDEKSİ
# ═══════════════════════════════════════════════════════════════

def angstrom(temp, rh):
    """
    Angström Yangın Tehlike İndeksi.

    Kaynak: Angström, A. (1942). Väder och skogsbrand.
            Svenska Brandförsvarsföreningen, Stockholm.

    Formül:
        I = (RH / 20) + ((27 - T) / 10)

    DİKKAT: Düşük değer = yüksek tehlike (diğer indekslerin tersi).

    Parametreler:
        temp : Hava sıcaklığı (°C), öğlen 12:00 LST
        rh   : Bağıl nem (%), öğlen 12:00 LST

    Dönüş: float (tipik aralık: 0–8)
    """
    return round((rh / 20.0) + ((27.0 - temp) / 10.0), 2)


def angstrom_sinif(val):
    """
    Angström tehlike sınıfı.
    Düşük değer = yüksek tehlike.

    Eşikler (Angström 1942):
        > 4.0  : Düşük (yangın olası değil)
        2.5–4.0: Orta
        2.0–2.5: Yüksek
        < 2.0  : Aşırı (yangın koşulları uygun)
    """
    if val > 4.0:
        return "Dusuk"
    elif val > 2.5:
        return "Orta"
    elif val > 2.0:
        return "Yuksek"
    else:
        return "Asiri"


# ═══════════════════════════════════════════════════════════════
#  2. NESTEROV İNDEKSİ
# ═══════════════════════════════════════════════════════════════

def nesterov(temp, dew_point, precip, g0=0):
    """
    Nesterov Kümülatif Yangın Tehlike İndeksi.

    Kaynak: Nesterov, V.G. (1949). Gorimostʹ lesa i metody eë opredeleniia.
            Goslesbumizdat, Moskova.

    Formül:
        Günlük bileşen: d = T₁₃ × (T₁₃ − Td₁₃)
        Kümülatif:
          Eğer yağış < 3 mm → G = G₀ + d
          Eğer yağış ≥ 3 mm → G = 0 (reset)

        T₁₃  : Öğle sıcaklığı (°C)
        Td₁₃ : Öğle çiy noktası sıcaklığı (°C)
        (T₁₃ − Td₁₃) : Çiy noktası açığı — havadaki kuruluğu temsil eder

    Parametreler:
        temp      : Hava sıcaklığı (°C), öğlen 12:00 LST
        dew_point : Çiy noktası sıcaklığı (°C), öğlen 12:00 LST
        precip    : 24 saatlik toplam yağış (mm)
        g0        : Önceki günün kümülatif Nesterov değeri

    Dönüş: float (≥ 0, üst sınır yok)
    """
    if precip >= 3.0:
        return 0.0

    deficit = temp - dew_point
    if deficit < 0:
        deficit = 0.0

    d = temp * deficit
    g = g0 + d
    return round(max(g, 0.0), 1)


def nesterov_sinif(val):
    """
    Nesterov tehlike sınıfı.

    Eşikler (Shetinsky 1994, Rusya standartları):
        < 300      : Tehlike yok (I)
        300–1000   : Düşük (II)
        1000–4000  : Orta (III)
        4000–10000 : Yüksek (IV)
        > 10000    : Aşırı (V)
    """
    if val < 300:
        return "Tehlike Yok"
    elif val < 1000:
        return "Dusuk"
    elif val < 4000:
        return "Orta"
    elif val < 10000:
        return "Yuksek"
    else:
        return "Asiri"


# ═══════════════════════════════════════════════════════════════
#  3. KBDI (KEETCH-BYRAM DROUGHT INDEX)
# ═══════════════════════════════════════════════════════════════

def kbdi(temp_max, precip, kbdi0=0, yillik_yagis=600.0):
    """
    Keetch-Byram Kuraklık İndeksi.

    Kaynak: Keetch, J.J. & Byram, G.M. (1968). A Drought Index for
            Forest Fire Control. USDA Forest Service, Research Paper SE-38.

    KBDI topraktaki nem eksikliğini 0–800 arasında ölçer.
    0 = doygun toprak, 800 = maksimum kuraklık.

    Formül (metrik versiyon, Alexander 1990 uyarlaması):
        net_rain = max(0, P − 5.1)                          [mm]
        Q = KBDI₀ − net_rain                                [yağış etkisi]
        DF = (800 − Q) × (0.968 × exp(0.0486 × T_F) − 8.30) × 0.001
             / (1 + 10.88 × exp(−0.0441 × R_ann))          [kuraklık artışı]
        KBDI = Q + max(DF, 0)

        T_F      : Günlük maksimum sıcaklık (°F, C'den dönüştürülür)
        R_ann    : Yıllık ortalama yağış (inç, mm'den dönüştürülür)

    Parametreler:
        temp_max     : Günlük maksimum sıcaklık (°C)
        precip       : 24 saatlik toplam yağış (mm)
        kbdi0        : Önceki günün KBDI değeri (0–800)
        yillik_yagis : Yıllık ortalama yağış (mm), varsayılan 600 mm (Türkiye ort.)

    Dönüş: float (0–800)
    """
    # Birim dönüşümleri
    t_fahrenheit = temp_max * 9.0 / 5.0 + 32.0
    r_annual_inch = yillik_yagis / 25.4

    # Yağış etkisi: 0.20 inç = 5.08 mm eşik (Keetch & Byram 1968)
    net_rain = max(0.0, precip - 5.08)
    q = max(kbdi0 - net_rain, 0.0)

    # Kuraklık artış faktörü (Drought Factor)
    # Sıcaklık eşiği: T_max < 50°F (10°C) altında kurutma yok (Keetch & Byram 1968)
    if temp_max < 10.0:
        df = 0.0
    else:
        numerator = (800.0 - q) * (0.968 * math.exp(0.0486 * t_fahrenheit) - 8.30) * 0.001
        denominator = 1.0 + 10.88 * math.exp(-0.0441 * r_annual_inch)
        df = numerator / denominator if denominator != 0 else 0.0
        df = max(df, 0.0)

    result = q + df
    return round(min(max(result, 0.0), 800.0), 1)


def kbdi_sinif(val):
    """
    KBDI tehlike sınıfı.

    Eşikler (Keetch & Byram 1968):
        0–200   : Düşük (toprak doygun, yangın riski minimal)
        200–400 : Orta (üst toprak kurumaya başlıyor)
        400–600 : Yüksek (ciddi kuraklık)
        600–800 : Aşırı (maksimum yangın hassasiyeti)
    """
    if val < 200:
        return "Dusuk"
    elif val < 400:
        return "Orta"
    elif val < 600:
        return "Yuksek"
    else:
        return "Asiri"


# ═══════════════════════════════════════════════════════════════
#  4. CARREGA I87 İNDEKSİ
# ═══════════════════════════════════════════════════════════════

def carrega(temp, dew_point, rh, wind=0):
    """
    Carrega I87 Yangın Tehlike İndeksi.

    Kaynak: Carrega, P. (1991). A meteorological index of forest fire hazard
            in Mediterranean France. Int. J. Wildland Fire, 1(2), 79-86.

    Akdeniz iklim kuşağı için geliştirilmiş indeks. Türkiye'nin güney
    kıyı şeridi için özellikle uygun.

    Formül (basitleştirilmiş regresyon modeli):
        I87 = −4.51 + 0.236 × T + 0.095 × δ − 0.038 × RH

        T  : Öğle sıcaklığı (°C)
        δ  : Çiy noktası açığı = T − Td (°C)
        RH : Bağıl nem (%)

    Parametreler:
        temp      : Hava sıcaklığı (°C), öğlen 12:00 LST
        dew_point : Çiy noktası sıcaklığı (°C), öğlen 12:00 LST
        rh        : Bağıl nem (%), öğlen 12:00 LST
        wind      : Rüzgar hızı (km/h) — bu varyantta kullanılmaz, ileriye dönük

    Dönüş: float (tipik aralık: −5 ile +25)
    """
    delta = max(temp - dew_point, 0.0)
    i87 = -4.51 + 0.236 * temp + 0.095 * delta - 0.038 * rh
    return round(i87, 2)


def carrega_sinif(val):
    """
    Carrega I87 tehlike sınıfı.

    Eşikler (Carrega 1991, Akdeniz kalibrasyonu):
        < 5  : Düşük
        5–10 : Orta
        10–15: Yüksek
        > 15 : Aşırı
    """
    if val < 5:
        return "Dusuk"
    elif val < 10:
        return "Orta"
    elif val < 15:
        return "Yuksek"
    else:
        return "Asiri"


# ═══════════════════════════════════════════════════════════════
#  BİRLEŞİK HESAPLAMA FONKSİYONU
# ═══════════════════════════════════════════════════════════════

def hesapla_ek(temp, rh, wind, precip, temp_max, dew_point,
               kbdi0=0, nesterov0=0, yillik_yagis=600.0):
    """
    Dört ek indeksi tek seferde hesaplar.

    Parametreler:
        temp         : Öğle sıcaklığı (°C)
        rh           : Bağıl nem (%)
        wind         : Rüzgar hızı (km/h)
        precip       : 24 saatlik yağış (mm)
        temp_max     : Günlük maksimum sıcaklık (°C)
        dew_point    : Çiy noktası sıcaklığı (°C)
        kbdi0        : Önceki günün KBDI değeri
        nesterov0    : Önceki günün Nesterov değeri
        yillik_yagis : Yıllık ortalama yağış (mm)

    Dönüş: dict
    """
    ang = angstrom(temp, rh)
    nes = nesterov(temp, dew_point, precip, nesterov0)
    kb  = kbdi(temp_max, precip, kbdi0, yillik_yagis)
    car = carrega(temp, dew_point, rh, wind)

    return {
        "angstrom":       ang,
        "angstrom_sinif": angstrom_sinif(ang),
        "nesterov":       nes,
        "nesterov_sinif": nesterov_sinif(nes),
        "kbdi":           kb,
        "kbdi_sinif":     kbdi_sinif(kb),
        "carrega":        car,
        "carrega_sinif":  carrega_sinif(car),
    }
