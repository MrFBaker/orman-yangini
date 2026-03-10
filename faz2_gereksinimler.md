# Faz 2 — Gereksinim Belirleme Raporu

**Kaynak:** mesowx/CFFDRS + gagreene/cffdrs (Van Wagner 1987 standardı)

---

## 1. Meteorolojik Girdiler

### 1.1 Zorunlu Girdiler

| # | Değişken | Sembol | Birim | Geçerli Aralık | Ölçüm Zamanı |
|---|----------|--------|-------|----------------|--------------|
| 1 | Sıcaklık | `temp` | °C | −40 ile +60 arası | 12:00 LST (yerel standart) |
| 2 | Bağıl Nem | `rh` | % | 0 ile 100 arası | 12:00 LST |
| 3 | Rüzgar Hızı | `wind` | km/h | ≥ 0 | 12:00 LST |
| 4 | 24 Saatlik Yağış | `precip` | mm | ≥ 0 | Önceki 24 saat toplamı |
| 5 | Ay | `month` | tam sayı (1–12) | 1–12 | Hesaplama günü |

> **Kritik not:** Ölçümler öğlen saatinde alınmalıdır. Sabah veya akşam ölçümleri hatalı sonuç verir.

### 1.2 Alt Sınır Uygulamaları (Koddan çıkarıldı)

| Değişken | Alt Sınır | Uygulandığı Bileşen |
|----------|-----------|---------------------|
| `temp` | −1.1 °C | FFMC ve DMC |
| `temp` | −2.8 °C | DC |
| `precip` | 0 mm | Tüm bileşenler |
| `rh` | 0 % | Tüm bileşenler |
| `wind` | 0 km/h | Tüm bileşenler |

---

## 2. Durum Değişkenleri (Önceki Günden Taşınan)

Sistem **hafıza taşıyan** bir yapıdır. Her gün hesaplama yapmak için önceki günün değerleri gereklidir.

| Değişken | Sembol | Açıklama |
|----------|--------|----------|
| Önceki gün FFMC | `ffmc0` | Dünün FFMC sonucu bugünün girdisi olur |
| Önceki gün DMC | `dmc0` | Dünün DMC sonucu bugünün girdisi olur |
| Önceki gün DC | `dc0` | Dünün DC sonucu bugünün girdisi olur |

### 2.1 Başlangıç Değerleri (Sezon Başı)

Yangın sezonu başladığında (ilkbaharda) kullanılacak standart değerler:

| Değişken | Başlangıç Değeri |
|----------|-----------------|
| FFMC₀ | **85** |
| DMC₀ | **6** |
| DC₀ | **15** |

---

## 3. Yağış Eşik Değerleri

Her bileşenin yağışa duyarlılığı farklıdır:

| Bileşen | Yağış Eşiği | Açıklama |
|---------|------------|----------|
| FFMC | > 0.5 mm | Bu değerin altında yağış etkisi yok sayılır |
| DMC | > 1.5 mm | Bu değerin altında yağış etkisi yok sayılır |
| DC | > 2.8 mm | Bu değerin altında yağış etkisi yok sayılır |

---

## 4. Aylık Düzeltme Faktörleri

Gün uzunluğu ve güneş açısı mevsime göre değiştiğinden iki faktör tablosu kullanılır.

### 4.1 Le — DMC Gün Uzunluğu Faktörü

| Enlem | Oca | Şub | Mar | Nis | May | Haz | Tem | Ağu | Eyl | Eki | Kas | Ara |
|-------|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| ≥ 30°N | 6.5 | 7.5 | 9.0 | 12.8 | 13.9 | 13.9 | 12.4 | 10.9 | 9.4 | 8.0 | 7.0 | 6.0 |
| 10°N–30°N | 7.9 | 8.4 | 8.9 | 9.5 | 9.9 | 10.2 | 10.1 | 9.7 | 9.1 | 8.6 | 8.1 | 7.8 |
| −10°N–10°N | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 |
| −30°N–−10°N | 10.1 | 9.6 | 9.1 | 8.5 | 8.1 | 7.8 | 7.9 | 8.3 | 8.9 | 9.4 | 9.9 | 10.2 |
| < −30°N | 11.5 | 10.5 | 9.2 | 7.9 | 6.8 | 6.2 | 6.5 | 7.4 | 8.7 | 10.0 | 11.2 | 11.8 |

> **Türkiye için:** Ortalama enlem ~39°N → **≥ 30°N satırı** kullanılır.

### 4.2 Lf — DC Gün Uzunluğu Faktörü

| Enlem | Oca | Şub | Mar | Nis | May | Haz | Tem | Ağu | Eyl | Eki | Kas | Ara |
|-------|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| ≥ 20°N | −1.6 | −1.6 | −1.6 | 0.9 | 3.8 | 5.8 | 6.4 | 5.0 | 2.4 | 0.4 | −1.6 | −1.6 |
| −20°N–20°N | 1.4 | 1.4 | 1.4 | 1.4 | 1.4 | 1.4 | 1.4 | 1.4 | 1.4 | 1.4 | 1.4 | 1.4 |
| < −20°N | 6.4 | 5.0 | 2.4 | 0.4 | −1.6 | −1.6 | −1.6 | −1.6 | −1.6 | 0.9 | 3.8 | 5.8 |

> **Türkiye için:** Ortalama enlem ~39°N → **≥ 20°N satırı** kullanılır.

---

## 5. Zaman Adımı Kararı

| Mod | Katsayı | Kullanım |
|-----|---------|----------|
| **Günlük** | k = `0.581` | Standart FWI sistemi — öğlen ölçümü |
| Saatlik | k = `0.0579` | Daha hassas; saatlik meteoroloji verisi gerektirir |

> **Karar: Günlük mod** kullanılacak. Proje kapsamı için yeterli ve standart.

---

## 6. Veri Formatı

### 6.1 Tek Günlük Hesaplama (Scalar)

```python
# Girdi
{
    "temp":   float,   # °C
    "rh":     float,   # %
    "wind":   float,   # km/h
    "precip": float,   # mm
    "month":  int,     # 1–12
    "ffmc0":  float,   # önceki gün FFMC
    "dmc0":   float,   # önceki gün DMC
    "dc0":    float    # önceki gün DC
}

# Çıktı
{
    "ffmc": float,
    "dmc":  float,
    "dc":   float,
    "isi":  float,
    "bui":  float,
    "fwi":  float,
    "dsr":  float,
    "sinif": str       # "Düşük" / "Orta" / "Yüksek" / "Çok Yüksek" / "Aşırı"
}
```

### 6.2 Çok Günlük Hesaplama (Zaman Serisi)

```python
# Girdi: Her gün için bir satır — örnek CSV yapısı
tarih, temp, rh, wind, precip, month
2025-06-01, 28.5, 35, 20, 0.0, 6
2025-06-02, 31.0, 28, 25, 0.0, 6
2025-06-03, 29.0, 40, 15, 2.0, 6
...

# Çıktı: Aynı yapıya FFMC, DMC, DC, ISI, BUI, FWI, sinif sütunları eklenir
```

---

## 7. Çıktı: FWI Tehlike Sınıfları

| Sınıf | FWI Aralığı | Renk Kodu | Açıklama |
|-------|------------|-----------|----------|
| Düşük | 0 – 5.0 | `#78C84B` (Yeşil) | Yangın riski düşük |
| Orta | 5.0 – 10.0 | `#FFFF00` (Sarı) | Dikkatli olunmalı |
| Yüksek | 10.0 – 20.0 | `#FFA500` (Turuncu) | Yüksek risk |
| Çok Yüksek | 20.0 – 30.0 | `#FF0000` (Kırmızı) | Çok yüksek risk |
| Aşırı | > 30.0 | `#800080` (Mor) | Aşırı tehlike |

---

## 8. Gereksinim Özeti

| Gereksinim | Karar |
|------------|-------|
| Giriş sayısı | 8 değişken (5 meteorolojik + 3 durum) |
| Ölçüm zamanı | Öğlen 12:00 LST |
| Zaman adımı | Günlük |
| Enlem faktörü | ≥ 30°N (DMC) ve ≥ 20°N (DC) |
| Başlangıç değerleri | FFMC=85, DMC=6, DC=15 |
| Çıktı formatı | 7 indeks + tehlike sınıfı |
| Veri tipi | Scalar float veya NumPy array |
| Bağımlılık | Yalnızca `numpy` |

---

## 9. Sonraki Adım: Faz 3

Tüm gereksinimler netleşti. Faz 3'te yazılacak fonksiyonlar:

```
fwi_hesap.py
├── ffmc(temp, rh, wind, precip, ffmc0)        → float
├── dmc(temp, rh, precip, dmc0, month)         → float
├── dc(temp, precip, dc0, month)               → float
├── isi(ffmc, wind)                            → float
├── bui(dmc, dc)                               → float
├── fwi(isi, bui)                              → float
├── dsr(fwi)                                   → float
├── fwi_sinif(fwi)                             → str
└── hesapla(temp, rh, wind, precip, month,
            ffmc0, dmc0, dc0)                  → dict (tüm çıktılar)
```
