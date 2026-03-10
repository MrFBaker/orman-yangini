# Faz 1 — Kaynak & Kod Analizi Sonuçları

**Kaynaklar:** mesowx/CFFDRS, gagreene/cffdrs (Van Wagner 1987 formüllerine dayalı)

---

## 1. Meteorolojik Girdiler

| Değişken | Birim | Açıklama | Ölçüm Zamanı |
|----------|-------|----------|---------------|
| `temp` | °C | Sıcaklık | Öğlen (12:00 LST) |
| `rh` | % | Bağıl Nem | Öğlen (12:00 LST) |
| `wind` | km/h | Rüzgar Hızı (10m yükseklik) | Öğlen (12:00 LST) |
| `precip` | mm | 24 saatlik toplam yağış | Öğlen (12:00 LST) |
| `month` | 1–12 | Ay (mevsimsel düzeltme için) | — |

> **Önemli:** Tüm ölçümler öğlen saatinde alınır. Bu standart FWI prosedürüdür.

---

## 2. Durum Değişkenleri (Önceki Günden Taşınan)

| Değişken | Başlangıç Değeri | Açıklama |
|----------|-----------------|----------|
| `ffmc0` | **85** | Önceki günün FFMC değeri |
| `dmc0` | **6** | Önceki günün DMC değeri |
| `dc0` | **15** | Önceki günün DC değeri |

> Sezon başında (ilkbahar) bu başlangıç değerleri kullanılır (Van Wagner 1987).

---

## 3. Sistem Yapısı ve Hesaplama Sırası

```
Girdiler: temp, rh, wind, precip, month
          + önceki gün: ffmc0, dmc0, dc0
                 ↓
    ┌──────────────────────────┐
    │  FFMC (temp,rh,wind,precip,ffmc0)  │
    │  DMC  (temp,rh,precip,dmc0,month) │
    │  DC   (temp,precip,dc0,month)      │
    └──────────────────────────┘
                 ↓
    ┌──────────────────────────┐
    │  ISI = f(ffmc, wind)               │
    │  BUI = f(dmc, dc)                  │
    └──────────────────────────┘
                 ↓
    ┌──────────────────────────┐
    │  FWI = f(isi, bui)                 │
    │  DSR = f(fwi)          [opsiyonel] │
    └──────────────────────────┘
```

---

## 4. Formüller (Bileşen Bazında)

### 4.1 FFMC — Fine Fuel Moisture Code

**Adım 1 — Önceki nem içeriğine dönüştür:**
```
mo = 147.2 × (101 − ffmc0) / (59.5 + ffmc0)
```

**Adım 2 — Yağış düzeltmesi (eğer precip > 0.5 mm):**
```
rf = precip − 0.5
delta_mrf = 42.5 × rf × exp(−100/(251−mo)) × (1 − exp(−6.93/rf))
  + [eğer mo > 150]: 0.0015 × (mo−150)² × rf^0.5
mr = mo + delta_mrf   (0–250 arasında sınırlanır)
mo = mr  (yağış varsa)
```

**Adım 3 — Denge nem içeriği:**
```
ed = 0.942×rh^0.679 + 11×exp((rh−100)/10) + 0.18×(21.1−temp)×(1−exp(−0.115×rh))
ew = 0.618×rh^0.753 + 10×exp((rh−100)/10) + 0.18×(21.1−temp)×(1−exp(−0.115×rh))
```

**Adım 4 — Kuruma/ıslanma oranı (günlük):**
```
k0w = 0.424×(1−((100−rh)/100)^1.7) + 0.0694×√wind×(1−((100−rh)/100)^8)
kw  = k0w × 0.581 × exp(0.0365×temp)

k0d = 0.424×(1−(rh/100)^1.7) + 0.0694×√wind×(1−(rh/100)^8)
kd  = k0d × 0.581 × exp(0.0365×temp)
```

**Adım 5 — Yeni nem içeriği:**
```
eğer mo < ed ve mo < ew:  m = ew − (ew−mo) / 10^kw
eğer mo > ed:             m = ed + (mo−ed) / 10^kd
aksi hâlde:               m = mo
m = clip(m, 0, 250)
```

**Adım 6 — FFMC değerine dönüştür:**
```
FFMC = 59.5 × (250−m) / (147.2+m)    [0–101 arasında sınırlanır]
```

---

### 4.2 DMC — Duff Moisture Code

**Adım 1 — Önceki nem içeriği:**
```
mo = 20 + 280 / exp(0.023 × dmc0)
```

**Adım 2 — Yağış düzeltmesi (eğer precip > 1.5 mm):**
```
re = 0.92 × precip − 1.27

b = 100 / (0.5 + 0.3×dmc0)          [dmc0 ≤ 33 ise]
  = 14.0 − 1.3×log(dmc0)            [33 < dmc0 ≤ 65 ise]
  = 6.2×log(dmc0) − 17.2            [dmc0 > 65 ise]

mr = mo + 1000×re / (48.77 + b×re)
dmc_rain = 244.72 − 43.43×log(mr − 20)
```

**Adım 3 — Günlük kuruma oranı:**
```
Le = aylık gün uzunluğu faktörü (Ocak–Aralık):
     [6.5, 7.5, 9.0, 12.8, 13.9, 13.9, 12.4, 10.9, 9.4, 8.0, 7.0, 6.0]
     (enlem ≥ 30°N için; Türkiye bu kategoriye girer)

k = 1.894 × (temp + 1.1) × (100 − rh) × Le × 0.0001
```

**Adım 4 — Sonuç:**
```
DMC = dmc_rain + k    (yağış varsa)
    = dmc0 + k        (yağış yoksa)
DMC = max(DMC, 0)
```

---

### 4.3 DC — Drought Code

**Adım 1 — Önceki nem eşdeğeri:**
```
q0 = 800 / exp(dc0 / 400)
```

**Adım 2 — Yağış düzeltmesi (eğer precip > 2.8 mm):**
```
rd = 0.83 × precip − 1.27
qr = q0 + 3.937 × rd
dc_rain = 400 × log(800 / qr)
```

**Adım 3 — Potansiyel evapotranspirasyon:**
```
Lf = aylık gün uzunluğu faktörü (Ocak–Aralık):
     [−1.6, −1.6, −1.6, 0.9, 3.8, 5.8, 6.4, 5.0, 2.4, 0.4, −1.6, −1.6]
     (enlem ≥ 20°N için; Türkiye bu kategoriye girer)

v = 0.36 × (temp + 2.8) + Lf
```

**Adım 4 — Sonuç:**
```
DC = dc_rain + 0.5×v    (yağış varsa)
   = dc0 + 0.5×v        (yağış yoksa)
DC = max(DC, 0)
```

---

### 4.4 ISI — Initial Spread Index

```
m  = 147.2 × (101 − FFMC) / (59.5 + FFMC)
fw = exp(0.05039 × wind)
ff = 91.9 × exp(−0.1386 × m) × (1 + m^5.31 / 49.300.000)
ISI = 0.208 × fw × ff
```

---

### 4.5 BUI — Build Up Index

```
eğer DMC ≤ 0.4 × DC:
    BUI = 0.8 × DMC × DC / (DMC + 0.4×DC)
aksi hâlde:
    BUI = DMC − (1 − 0.8×DC / (DMC + 0.4×DC)) × (0.92 + (0.0114×DMC)^1.7)
BUI = max(BUI, 0)
```

---

### 4.6 FWI — Fire Weather Index

```
fD = 0.626 × BUI^0.809 + 2           [BUI ≤ 80 ise]
   = 1000 / (25 + 108.64×exp(−0.023×BUI))   [BUI > 80 ise]

B = 0.1 × ISI × fD

FWI = B                               [B ≤ 1 ise]
    = exp(2.72 × (0.434×log(B))^0.647)  [B > 1 ise]
FWI = max(FWI, 0)
```

---

### 4.7 DSR — Daily Severity Rating (opsiyonel)

```
DSR = 0.0272 × FWI^1.77
```

---

## 5. FWI Tehlike Sınıfları

| Sınıf | FWI Aralığı | Renk |
|-------|------------|------|
| Düşük | 0 – 5 | Yeşil |
| Orta | 5 – 10 | Sarı |
| Yüksek | 10 – 20 | Turuncu |
| Çok Yüksek | 20 – 30 | Kırmızı |
| Aşırı | > 30 | Mor/Siyah |

---

## 6. Veri Formatı Gereksinimleri

### Tek günlük hesaplama (scalar):
```python
inputs = {
    "temp": float,     # °C
    "rh": float,       # %
    "wind": float,     # km/h
    "precip": float,   # mm
    "month": int,      # 1–12
    "ffmc0": float,    # önceki gün FFMC
    "dmc0": float,     # önceki gün DMC
    "dc0": float,      # önceki gün DC
}
```

### Çok günlük / grid hesaplama:
- NumPy array desteği mevcut (her iki kaynak da destekliyor)
- NaN değerleri maskelenerek işleniyor

---

## 7. Önemli Notlar

1. **Sıcaklık alt sınırı:** FFMC için `temp >= -1.1°C`, DC için `temp >= -2.8°C` uygulanır
2. **Yağış eşikleri farklı:** FFMC `> 0.5mm`, DMC `> 1.5mm`, DC `> 2.8mm`
3. **Aylık faktörler:** `Le` (DMC) ve `Lf` (DC) değerleri enlem ve aya göre değişir — Türkiye için `≥ 30°N` tablosu geçerli
4. **Günlük/saatlik mod:** FFMC hem günlük hem saatlik hesaplanabilir (katsayı farkı: `0.581` günlük, `0.0579` saatlik)
5. **Sezon başı:** Sezon başında FFMC=85, DMC=6, DC=15 kullanılır

---

## 8. Sonuç: Faz 2 için Gereksinim Listesi

- [x] Girdiler netleştirildi
- [x] Tüm formüller dokümante edildi
- [x] Başlangıç değerleri belirlendi
- [x] Aylık faktör tabloları çıkarıldı
- [x] Veri formatı (scalar + array) belirlendi
- [ ] **Sonraki adım:** Python modülü yaz, Van Wagner referans değerleriyle doğrula
