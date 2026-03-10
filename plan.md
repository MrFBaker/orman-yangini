# Orman Yangını Erken Uyarı Sistemi — Proje Planı

## Genel Bakış
Meteorolojik veri tabanlı orman yangını erken uyarı sistemi.
Bu belgede FWI (Fire Weather Index) modülünün geliştirilme süreci adım adım planlanmıştır.

---

## Faz 1: Kaynak & Kod Analizi ✅ TAMAMLANDI

- [x] `mesowx/CFFDRS` GitHub kodunu analiz et
- [x] `gagreene/cffdrs` GitHub kodunu analiz et
- [x] Tüm formüller, girdiler ve veri formatları dokümante edildi
- [x] **Çıktı:** [`faz1_analiz.md`](faz1_analiz.md)

**Bulgular özeti:**
- Girdiler: `temp (°C)`, `rh (%)`, `wind (km/h)`, `precip (mm)`, `month (1–12)` — öğlen ölçümü
- Durum değişkenleri: `ffmc0`, `dmc0`, `dc0` — önceki günden taşınır
- Başlangıç değerleri (sezon başı): FFMC=85, DMC=6, DC=15
- Hesaplama sırası: FFMC → DMC → DC → ISI → BUI → FWI → DSR
- Türkiye için enlem faktörü: ≥ 30°N tablosu geçerli
- Zaman adımı: **günlük** (saatlik mod da mümkün, farklı katsayı)

---

## Faz 2: Gereksinim Belirleme ✅ TAMAMLANDI

- [x] Zorunlu meteorolojik girdiler ve birimleri netleştirildi
- [x] Veri formatı belirlendi → scalar (float) veya NumPy array
- [x] Başlangıç değerleri belirlendi → FFMC=85, DMC=6, DC=15
- [x] Zaman adımı belirlendi → **günlük**
- [x] Yağış eşikleri netleştirildi → FFMC: >0.5mm, DMC: >1.5mm, DC: >2.8mm
- [x] Aylık faktör tabloları çıkarıldı (Le, Lf)
- [x] **Çıktı:** Gereksinimler `faz1_analiz.md` içinde dokümante edildi

---

## Faz 3: Python Modülü Geliştirme ← SIRADAKI ADIM

- [ ] `ffmc(temp, rh, wind, precip, ffmc0)` fonksiyonu yaz
- [ ] `dmc(temp, rh, precip, dmc0, month)` fonksiyonu yaz
- [ ] `dc(temp, precip, dc0, month)` fonksiyonu yaz
- [ ] `isi(ffmc, wind)` fonksiyonu yaz
- [ ] `bui(dmc, dc)` fonksiyonu yaz
- [ ] `fwi(isi, bui)` fonksiyonu yaz
- [ ] `fwi_class(fwi)` → tehlike sınıfı fonksiyonu yaz
- [ ] Referans değerlerle doğrulama testi yap
- [ ] **Çıktı:** `fwi_hesap.py` — çalışan ve test edilmiş Python modülü

---

## Faz 4: Web Sitesi

- [ ] API tasarımı (Backend — Flask veya FastAPI)
- [ ] Girdi formu tasarımı (Frontend)
- [ ] Sonuç görselleştirme (FWI skoru + risk seviyesi + renk kodlaması)
- [ ] Entegrasyon & sunum hazırlığı

---

## Kaynaklar

| Kaynak | Tür | URL |
|--------|-----|-----|
| Van Wagner (1987) | Teknik Rapor (PDF) | https://cfs.nrcan.gc.ca/pubwarehouse/pdfs/23688.pdf |
| NRCan FWI Sistemi | Resmi Sayfa | https://cwfis.cfs.nrcan.gc.ca/background/summary/fwi |
| gagreene/cffdrs | GitHub (Python) | https://github.com/gagreene/cffdrs |
| mesowx/CFFDRS | GitHub (Python) | https://github.com/mesowx/CFFDRS |

---

## Notlar

- Faz 1 ve Faz 2 tamamlandı — detaylar `faz1_analiz.md` dosyasında
- Türkiye enlemi (≥ 30°N) için Le ve Lf faktör tabloları belirli
- Tüm formüller Van Wagner (1987) standardına dayanmaktadır
