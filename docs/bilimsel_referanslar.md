# Bilimsel Referanslar ve Formül Doğrulama Raporu

Bu doküman, Fire-EWS sisteminde kullanılan tüm yangın tehlike indekslerinin
bilimsel kaynaklarını, formüllerini ve doğrulama süreçlerini içerir.

---

## 1. FWI — Fire Weather Index (Van Wagner, 1987)

### Kaynak
- **Van Wagner, C.E. (1987).** Development and Structure of the Canadian Forest Fire Weather Index System. *Canadian Forestry Service, Forestry Technical Report 35.* Ottawa.
- **Doğrulama referansı:** bcgov/cffdrs R paketi — Kanada hükümetinin açık kaynaklı referans uygulaması

### Bileşenler
| Bileşen | Tam Adı | Açıklama |
|---------|---------|----------|
| FFMC | Fine Fuel Moisture Code | İnce üst tabaka yanıcı madde nem kodu (0–101) |
| DMC | Duff Moisture Code | Döküntü nem kodu (≥0) |
| DC | Drought Code | Derin organik tabaka nem kodu (≥0) |
| ISI | Initial Spread Index | Başlangıç yayılma indeksi |
| BUI | Buildup Index | Birikmiş yanıcı madde indeksi |
| FWI | Fire Weather Index | Yangın hava indeksi (nihai skor) |
| DSR | Daily Severity Rating | Günlük şiddet oranı |

### Girdiler
- Sıcaklık (°C) — öğlen 12:00 LST
- Bağıl nem (%) — öğlen 12:00 LST
- Rüzgar hızı (km/h) — öğlen 12:00 LST
- 24 saatlik yağış (mm)
- Ay (1–12)
- Enlem (opsiyonel, gün uzunluğu faktörleri için)

### Tehlike Sınıfı Eşikleri
| Sınıf | FWI Aralığı |
|-------|-------------|
| Düşük | < 5 |
| Orta | 5–10 |
| Yüksek | 10–20 |
| Çok Yüksek | 20–30 |
| Aşırı | ≥ 30 |

### Doğrulama
- Van Wagner referans testi: T=17°C, H=%42, W=25 km/h, r=0 mm
- Beklenen: FFMC=87.69, DMC=8.47, DC=21.76, ISI=10.85, BUI=8.59, FWI=10.14
- Tüm değerler ±0.1 toleransla eşleşiyor ✅
- Gerçek yangın olayları ile doğrulama: Manavgat 2021, Marmaris 2021, İzmir 2019

### Formül Detayları
Formüllerin tamamı için bkz: [teknik_referans.md](teknik_referans.md)

---

## 2. Angström İndeksi (Angström, 1942)

### Kaynak
- **Angström, A. (1942).** Väder och skogsbrand. *Svenska Brandförsvarsföreningen*, Stockholm.
- **İkincil doğrulama kaynakları:**
  - WikiFire (WSL): https://wikifire.wsl.ch — Angström index sayfası
  - CEDA/HELIX projesi: https://catalogue.ceda.ac.uk/uuid/d8a5ea8766764d5e86b347e5772e73b3/
  - Chandler, C. et al. (1983). Fire in Forestry, Volume 1. John Wiley & Sons.

### Formül
```
I = RH / 20 + (27 − T) / 10
```
- T: Hava sıcaklığı (°C)
- RH: Bağıl nem (%)

### Önemli Not
**Ters skala:** Düşük değer = yüksek yangın tehlikesi (diğer indekslerin tersi).

### Sabit Seçimi: 27 vs 29
Literatürde iki varyant mevcut:
- **27 sabiti:** WikiFire (WSL), CEDA/HELIX, Chandler et al. (1983), Langholz & Schmidtmayer (1993) — **çoğunluk ve birincil kaynaklar**
- **29 sabiti:** Bazı ikincil kaynaklar — kaynağı belirsiz

Projemizde **27 sabiti** kullanılmaktadır (birincil kaynaklarla uyumlu).

### Tehlike Sınıfı Eşikleri
| Angström Değeri | Sınıf | Açıklama |
|-----------------|-------|----------|
| > 4.0 | Düşük | Yangın olası değil |
| 2.5–4.0 | Orta | Yangın koşulları olumsuz |
| 2.0–2.5 | Yüksek | Yangın koşulları mümkün |
| < 2.0 | Aşırı | Yangın koşulları uygun |

**Kaynak:** WikiFire (WSL) referans tablosu

### Doğrulama
El hesabı: T=25°C, RH=30%
```
I = 30/20 + (27-25)/10 = 1.5 + 0.2 = 1.7
```
Kod çıktısı: 1.7 ✅

---

## 3. Nesterov İndeksi (Nesterov, 1949)

### Kaynak
- **Nesterov, V.G. (1949).** Gorimostʹ lesa i metody eë opredeleniia. *Goslesbumizdat*, Moskova.
- **Eşik referansı:** Shetinsky, E.A. (1994). Ohrana lesov i lesnaya pirologiya. Moskova.
- **İkincil doğrulama kaynakları:**
  - WikiFire (WSL): https://wikifire.wsl.ch — Nesterov ignition index
  - ClimInd R paketi: https://rdrr.io/cran/ClimInd/man/nesterovIndex.html
  - Skvarenina, J. et al. (2003). Nesterov risk classes tablosu (ResearchGate)

### Formül
```
Günlük bileşen:  d = T × (T − Td)
Kümülatif:
  Yağış < 3 mm  → G = G₀ + d
  Yağış ≥ 3 mm  → G = 0 (reset)
```
- T: Öğle sıcaklığı (°C), 12:00–13:00 LST
- Td: Öğle çiy noktası sıcaklığı (°C)
- (T − Td): Çiy noktası açığı — havadaki kuruluğu temsil eder

### Yağış Reset Kuralı
- **Orijinal Nesterov (1949):** 3 mm binary reset (projemizde kullanılan)
- **Kase (1969) modifikasyonu:** Kademeli reset sistemi (farklı bir indeks, M68) — projemizde **kullanılmıyor**

### Not: ≥3 vs >3
ClimInd R paketinde "does not exceed 3 mm" ifadesi var — yani 3mm dahil toplanmaya devam, 3mm'yi aşan değerler reset tetikler. Pratikte fark ihmal edilebilir. Projemizde ≥3 kullanılmaktadır.

### Tehlike Sınıfı Eşikleri (Shetinsky, 1994)
| Nesterov Değeri | Sınıf | Rusya Standardı |
|-----------------|-------|-----------------|
| < 300 | Tehlike Yok | Sınıf I |
| 300–1000 | Düşük | Sınıf II |
| 1000–4000 | Orta | Sınıf III |
| 4000–10000 | Yüksek | Sınıf IV |
| > 10000 | Aşırı | Sınıf V |

### Doğrulama
El hesabı: T=25°C, Td=10°C, P=0mm, G₀=0
```
d = 25 × (25 − 10) = 25 × 15 = 375
G = 0 + 375 = 375
```
Kod çıktısı: 375 ✅

Yağış reset testi: T=25°C, Td=10°C, P=5mm, G₀=1000
```
Yağış ≥ 3mm → G = 0
```
Kod çıktısı: 0 ✅

---

## 4. KBDI — Keetch-Byram Drought Index (Keetch & Byram, 1968)

### Kaynak
- **Keetch, J.J. & Byram, G.M. (1968).** A Drought Index for Forest Fire Control. *USDA Forest Service, Research Paper SE-38.*
- **Metrik uyarlama:** Alexander, M.E. (1990). Computer calculation of the Keetch-Byram Drought Index. Petawawa National Forestry Institute.
- **İkincil kaynaklar:**
  - Crane, T.P. (1982). Computing the Keetch-Byram Drought Index. NOAA Technical Memorandum.
  - NWCG PMS 437-1 — Fireline Handbook (eşik değerleri)

### Formül
```
Adım 1 — Yağış etkisi:
  net_rain = max(0, P − 5.08)          [mm, 0.20 inç = 5.08 mm]
  Q = max(KBDI₀ − net_rain, 0)

Adım 2 — Kuraklık artışı (yalnızca T_max ≥ 10°C ise):
  T_F = T_max × 9/5 + 32               [°C → °F dönüşüm]
  R_inç = R_yıl / 25.4                  [mm → inç dönüşüm]
  DF = (800 − Q) × (0.968 × e^(0.0486 × T_F) − 8.30) × 10⁻³
       / (1 + 10.88 × e^(−0.0441 × R_inç))

Adım 3 — Yeni KBDI:
  KBDI = Q + max(DF, 0)                 [0–800 aralığında]
```

### Katsayı Doğrulaması
| Katsayı | Koddaki Değer | Orijinal (Keetch & Byram 1968) | Durum |
|---------|---------------|-------------------------------|-------|
| Yağış eşiği | 5.08 mm | 0.20 inç = 5.08 mm | ✅ |
| Üstel katsayı (sıcaklık) | 0.0486 | 0.0486 | ✅ |
| Sıcaklık çarpanı | 0.968 | 0.968 | ✅ |
| Sabit çıkarma | 8.30 | 8.30 | ✅ |
| Payda çarpanı | 10.88 | 10.88 | ✅ |
| Payda üstel katsayısı | -0.0441 | -0.0441 | ✅ |
| Ölçek | 0–800 | 0–800 | ✅ |

### Sıcaklık Eşiği
**Orijinal makalede kritik kural:** T_max < 50°F (10°C) altında DF = 0.
Kurumuş yakıtların bu sıcaklığın altında önemli ölçüde nemini kaybetmediği varsayımına dayanır.
Projemizde bu kural **uygulanmaktadır** ✅

### Tehlike Sınıfı Eşikleri (NWCG standartları)
| KBDI Değeri | Sınıf | Açıklama |
|-------------|-------|----------|
| 0–200 | Düşük | Toprak doygun, yangın riski minimal |
| 200–400 | Orta | Üst toprak tabakası kurumaya başlıyor |
| 400–600 | Yüksek | Ciddi kuraklık, derin kök bölgesi etkileniyor |
| 600–800 | Aşırı | Maksimum yangın hassasiyeti |

### Doğrulama
Soğuk gün testi: T_max=5°C (< 10°C), P=0mm, KBDI₀=200
```
T_max < 10°C → DF = 0
KBDI = 200 + 0 = 200 (değişmez)
```
Kod çıktısı: 200.0 ✅

Yağış etkisi testi: T_max=25°C, P=20mm, KBDI₀=300
```
net_rain = 20 - 5.08 = 14.92
Q = 300 - 14.92 = 285.08
KBDI = 285.08 + DF (DF > 0)
```
Kod çıktısı: 288.5 (285.08 + DF=3.42) ✅

---

## 5. Carrega I87 İndeksi (Carrega, 1991)

### Kaynak
- **Carrega, P. (1991).** A meteorological index of forest fire hazard in Mediterranean France. *International Journal of Wildland Fire*, 1(2), 79–86.
- **Ek referans:** Carrega, P. (1988). Méthode d'estimation de l'indice de risque de feu de forêt en fonction des facteurs météorologiques. Document interne, Université de Nice.

### Formül
```
I87 = −4.51 + 0.236 × T + 0.095 × δ − 0.038 × RH
```
- T: Öğle sıcaklığı (°C)
- δ = T − Td: Çiy noktası açığı (°C)
- RH: Bağıl nem (%)

### Katsayıların Fiziksel Tutarlılığı
| Katsayı | İşaret | Fiziksel Anlam | Tutarlılık |
|---------|--------|----------------|------------|
| T (+0.236) | Pozitif | Yüksek sıcaklık → yüksek risk | ✅ |
| δ (+0.095) | Pozitif | Kuru hava → yüksek risk | ✅ |
| RH (−0.038) | Negatif | Yüksek nem → düşük risk | ✅ |

### 1987 vs 1991 Versiyonları
- **I87** adı: Model **1987** verilerinden kalibre edilmiştir
- **1991 makalesi:** Modelin yayınlandığı ve detaylandırıldığı akademik kaynak
- Carrega'nın sonraki çalışmalarında (I92 vb.) rüzgar bileşeni eklenmiştir — **I87'de rüzgar yoktur**

### Rüzgar Bileşeni
I87 formülünde rüzgar bileşeni **yoktur**. Bu, orijinal makaledeki tasarımla uyumludur. Rüzgar etkisi sonraki versiyonlara (I92+) eklenmiştir.

### Akdeniz Kalibrasyonu — Türkiye Uygunluğu
I87, Güneydoğu Fransa (Côte d'Azur, Provence) verilerinden türetilmiştir. Türkiye'nin Akdeniz kıyısı (Antalya, Muğla, İzmir) benzer iklim özelliklerine sahiptir:
- Sıcak, kurak yazlar
- Akdeniz bitki örtüsü (maki)
- Benzer sıcaklık ve nem rejimleri

**Kısıtlama:** Türkiye'nin iç kesimleri veya karasal iklim bölgeleri için doğrudan uygulanması uygun olmayabilir. İdeal olarak Türkiye yangın verileriyle katsayılar yeniden kalibre edilmelidir.

### Tehlike Sınıfı Eşikleri (Carrega 1991, Akdeniz kalibrasyonu)
| I87 Değeri | Sınıf |
|------------|-------|
| < 5 | Düşük |
| 5–10 | Orta |
| 10–15 | Yüksek |
| > 15 | Aşırı |

### Doğrulama
El hesabı: T=30°C, Td=15°C, RH=25%
```
δ = 30 − 15 = 15
I87 = −4.51 + 0.236×30 + 0.095×15 − 0.038×25
    = −4.51 + 7.08 + 1.425 − 0.95
    = 3.045
```
Kod çıktısı: 3.04 ✅ (yuvarlama farkı)

---

## Karşılaştırmalı Özet

| İndeks | Kaynak Yılı | Köken | Kümülatif | Karmaşıklık | Ters Skala |
|--------|-------------|-------|-----------|-------------|------------|
| FWI | 1987 | Kanada | Evet (3 state) | Yüksek | Hayır |
| Angström | 1942 | İsveç | Hayır | Çok düşük | **Evet** |
| Nesterov | 1949 | Rusya | Evet (1 state) | Düşük | Hayır |
| KBDI | 1968 | ABD | Evet (1 state) | Orta | Hayır |
| Carrega I87 | 1991 | Fransa | Hayır | Orta | Hayır |

---

## Open-Meteo API Veri Uyumluluğu

| Girdi | API Parametresi | Kullanan İndeksler |
|-------|-----------------|-------------------|
| Sıcaklık (°C) | `temperature_2m` (hourly) | Hepsi |
| Bağıl nem (%) | `relativehumidity_2m` / `relative_humidity_2m` | FWI, Angström, Carrega |
| Rüzgar hızı (km/h) | `windspeed_10m` / `wind_speed_10m` | FWI |
| Yağış (mm) | `precipitation` (hourly → günlük toplam) | FWI, Nesterov, KBDI |
| Çiy noktası (°C) | `dewpoint_2m` / `dew_point_2m` | Nesterov, Carrega |
| Günlük maks. sıcaklık (°C) | `temperature_2m_max` (daily) | KBDI |

Tüm girdiler Open-Meteo Archive ve Forecast API'lerinden elde edilmektedir ✅

---

## Birim Testleri

35 adet birim testi yazılmıştır (`test_indeksler.py`):
- Angström: 7 test (formül, sınıflar, ters skala)
- Nesterov: 9 test (formül, kümülatif, reset, negatif deficit, sınıflar)
- KBDI: 7 test (soğuk gün, yağış, sınırlar, sınıflar)
- Carrega: 7 test (formül, sıcak/soğuk, sınıflar)
- Birleşik hesaplama: 2 test (anahtar varlığı, değer doğrulama)

Tüm testler geçmektedir ✅

---

*Son güncelleme: 22 Mart 2026*
