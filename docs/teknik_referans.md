# FWI Teknik Referans Dokumani

Bu belge, FWI hesaplama motorunun teknik detaylarini icerir.
Formullerin tamami Van Wagner (1987) Forestry Technical Report 35'e dayanir.

---

## 1. Meteorolojik Girdiler

| # | Degisken | Sembol | Birim | Gecerli Aralik | Olcum Zamani |
|---|----------|--------|-------|----------------|--------------|
| 1 | Sicaklik | temp | C | -40 ile +60 | 12:00 LST |
| 2 | Bagil Nem | rh | % | 0 ile 100 | 12:00 LST |
| 3 | Ruzgar Hizi | wind | km/h | >= 0 | 12:00 LST |
| 4 | 24 Saatlik Yagis | precip | mm | >= 0 | Onceki 24 saat toplami |
| 5 | Ay | month | tam sayi (1-12) | 1-12 | Hesaplama gunu |

> Tum olcumler ogle saatinde alinir. Van Wagner (1987) metodolojisi bunu gerektirir.

### Sicaklik Alt Sinirlari

| Degisken | Alt Sinir | Uygulanan Bilesen |
|----------|-----------|-------------------|
| temp | -1.1 C | FFMC ve DMC |
| temp | -2.8 C | DC |

### Yagis Esik Degerleri

| Bilesen | Yagis Esigi | Aciklama |
|---------|------------|----------|
| FFMC | > 0.5 mm | Bunun altinda yagis etkisi yok sayilir |
| DMC | > 1.5 mm | Bunun altinda yagis etkisi yok sayilir |
| DC | > 2.8 mm | Bunun altinda yagis etkisi yok sayilir |

---

## 2. Durum Degiskenleri

Sistem hafiza tasiyan bir yapidir. Her gun hesaplama yapmak icin onceki gunun degerleri gereklidir.

| Degisken | Baslangic Degeri | Aciklama |
|----------|-----------------|----------|
| ffmc0 | 85 | Onceki gunun FFMC degeri |
| dmc0 | 6 | Onceki gunun DMC degeri |
| dc0 | 15 | Onceki gunun DC degeri |

> Sezon basinda (ilkbahar) bu baslangic degerleri kullanilir.

---

## 3. Aylik Duzeltme Faktorleri

### Le — DMC Gun Uzunlugu Faktoru

| Enlem | Oca | Sub | Mar | Nis | May | Haz | Tem | Agu | Eyl | Eki | Kas | Ara |
|-------|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| >= 30N | 6.5 | 7.5 | 9.0 | 12.8 | 13.9 | 13.9 | 12.4 | 10.9 | 9.4 | 8.0 | 7.0 | 6.0 |
| 10N-30N | 7.9 | 8.4 | 8.9 | 9.5 | 9.9 | 10.2 | 10.1 | 9.7 | 9.1 | 8.6 | 8.1 | 7.8 |

> Turkiye enlemi ~36-42N → **>= 30N satiri** kullanilir.

### Lf — DC Gun Uzunlugu Faktoru

| Enlem | Oca | Sub | Mar | Nis | May | Haz | Tem | Agu | Eyl | Eki | Kas | Ara |
|-------|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| >= 20N | -1.6 | -1.6 | -1.6 | 0.9 | 3.8 | 5.8 | 6.4 | 5.0 | 2.4 | 0.4 | -1.6 | -1.6 |
| -20N-20N | 1.4 | 1.4 | 1.4 | 1.4 | 1.4 | 1.4 | 1.4 | 1.4 | 1.4 | 1.4 | 1.4 | 1.4 |

> Turkiye enlemi ~36-42N → **>= 20N satiri** kullanilir.

---

## 4. Formuller

### 4.1 FFMC — Fine Fuel Moisture Code

```
Adim 1: mo = 147.2 * (101 - ffmc0) / (59.5 + ffmc0)

Adim 2 (yagis > 0.5 mm):
  rf = precip - 0.5
  delta = 42.5 * rf * exp(-100/(251-mo)) * (1 - exp(-6.93/rf))
       + [mo > 150 ise]: 0.0015 * (mo-150)^2 * rf^0.5
  mr = mo + delta  (0-250 sinir)

Adim 3: Denge nem icerigi
  ed = 0.942*rh^0.679 + 11*exp((rh-100)/10) + 0.18*(21.1-temp)*(1-exp(-0.115*rh))
  ew = 0.618*rh^0.753 + 10*exp((rh-100)/10) + 0.18*(21.1-temp)*(1-exp(-0.115*rh))

Adim 4: Kuruma/islanma orani
  k0d = 0.424*(1-(rh/100)^1.7) + 0.0694*sqrt(wind)*(1-(rh/100)^8)
  kd  = k0d * 0.581 * exp(0.0365*temp)
  k0w = 0.424*(1-((100-rh)/100)^1.7) + 0.0694*sqrt(wind)*(1-((100-rh)/100)^8)
  kw  = k0w * 0.581 * exp(0.0365*temp)

Adim 5: Yeni nem icerigi
  mo > ed ise:  m = ed + (mo-ed) / 10^kd
  mo < ew ise:  m = ew - (ew-mo) / 10^kw
  aksi halde:   m = mo

Adim 6: FFMC = 59.5 * (250-m) / (147.2+m)  [0-101 sinir]
```

### 4.2 DMC — Duff Moisture Code

```
Adim 1: mo = 20 + 280 / exp(0.023 * dmc0)

Adim 2 (yagis > 1.5 mm):
  re = 0.92 * precip - 1.27
  b  = 100/(0.5+0.3*dmc0)       [dmc0 <= 33]
     = 14.0 - 1.3*log(dmc0)     [33 < dmc0 <= 65]
     = 6.2*log(dmc0) - 17.2     [dmc0 > 65]
  mr = mo + 1000*re / (48.77 + b*re)
  dmc_rain = 244.72 - 43.43*log(mr - 20)

Adim 3: K = 1.894 * (temp+1.1) * (100-rh) * Le * 0.0001

Adim 4: DMC = dmc_rain + K  (yagis varsa)
            = dmc0 + K      (yagis yoksa)
         DMC = max(DMC, 0)
```

### 4.3 DC — Drought Code

```
Adim 1: q0 = 800 / exp(dc0 / 400)

Adim 2 (yagis > 2.8 mm):
  rd = 0.83 * precip - 1.27
  qr = q0 + 3.937 * rd
  dc_rain = 400 * log(800 / qr)

Adim 3: V = 0.36 * (temp + 2.8) + Lf

Adim 4: DC = dc_rain + 0.5*V  (yagis varsa)
           = dc0 + 0.5*V      (yagis yoksa)
         DC = max(DC, 0)
```

### 4.4 ISI — Initial Spread Index

```
m  = 147.2 * (101 - FFMC) / (59.5 + FFMC)
fw = exp(0.05039 * wind)
ff = 91.9 * exp(-0.1386*m) * (1 + m^5.31 / 49300000)
ISI = 0.208 * fw * ff
```

### 4.5 BUI — Build Up Index

```
DMC <= 0.4*DC ise:
  BUI = 0.8 * DMC * DC / (DMC + 0.4*DC)
aksi halde:
  BUI = DMC - (1 - 0.8*DC/(DMC+0.4*DC)) * (0.92 + (0.0114*DMC)^1.7)
BUI = max(BUI, 0)
```

### 4.6 FWI — Fire Weather Index

```
fD = 0.626*BUI^0.809 + 2                         [BUI <= 80]
   = 1000 / (25 + 108.64*exp(-0.023*BUI))        [BUI > 80]
B  = 0.1 * ISI * fD
FWI = B                                           [B <= 1]
    = exp(2.72 * (0.434*log(B))^0.647)            [B > 1]
```

### 4.7 DSR — Daily Severity Rating

```
DSR = 0.0272 * FWI^1.77
```

---

## 5. Tehlike Siniflari

### Kanada Standart Esikleri

| Sinif | FWI Araligi |
|-------|------------|
| Dusuk | 0 - 5.0 |
| Orta | 5.0 - 10.0 |
| Yuksek | 10.0 - 20.0 |
| Cok Yuksek | 20.0 - 30.0 |
| Asiri | > 30.0 |

### EFFIS Akdeniz Esikleri (Turkiye icin onerilen)

| Sinif | FWI Araligi |
|-------|------------|
| Dusuk | 0 - 5.2 |
| Orta | 5.2 - 11.2 |
| Yuksek | 11.2 - 21.3 |
| Cok Yuksek | 21.3 - 38.0 |
| Asiri | > 38.0 |

---

## 6. Veri Formati

### Tek Gunluk (Scalar)
```python
# Girdi
{"temp": float, "rh": float, "wind": float, "precip": float,
 "month": int, "ffmc0": float, "dmc0": float, "dc0": float}

# Cikti
{"ffmc": float, "dmc": float, "dc": float, "isi": float,
 "bui": float, "fwi": float, "dsr": float, "sinif": str}
```

### Cok Gunluk (Zaman Serisi)
```
tarih, temp, rh, wind, precip, month
2025-06-01, 28.5, 35, 20, 0.0, 6
2025-06-02, 31.0, 28, 25, 0.0, 6
→ Her satira FFMC, DMC, DC, ISI, BUI, FWI, sinif eklenir
```

---

## 7. Onemli Notlar

1. Zaman adimi: Gunluk (katsayi 0.581). Saatlik mod da mumkun (katsayi 0.0579).
2. Turkiye enlemi 36-42N → Le icin >= 30N, Lf icin >= 20N tablosu kullanilir.
3. Sistem enleme gore dinamik tablo secimi yapar (fwi_hesap.py: enleme_gore_tablolar).
4. Warmup: Hesaplama baslangicindaki 1 Ocak'tan itibaren isitma yapilir.
