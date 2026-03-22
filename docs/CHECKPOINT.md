# Proje Checkpoint — 23 Mart 2026 (Son güncelleme: 23 Mart 2026)

## Proje Adı
**Fire-EWS — Meteorolojik Veri Tabanlı Orman Yangını Erken Uyarı Sistemi**

## Canlı Site
- **URL:** https://fire-ews.tech
- **IP:** 165.22.92.106
- **Giriş:** admin / fire2026 (Basic Auth)
- **noindex/nofollow:** Arama motorlarından gizli

---

## 1. Hesaplama Sistemi — 5 İndeks

### FWI — Van Wagner (1987)
- 6 alt bileşen: FFMC, DMC, DC, ISI, BUI, FWI + DSR
- Enleme göre dinamik Le/Lf tablo seçimi
- Warmup: 1 Ocak'tan itibaren state biriktirme
- Dosya: `fwi_hesap.py`

### Angström (1942)
- Formül: `I = RH/20 + (27-T)/10`
- Anlık, state yok. Ters skala (düşük=tehlikeli)
- Dosya: `indeksler.py`

### Nesterov (1949)
- Formül: `G = G₀ + T×(T-Td)`, yağış ≥ 3mm → reset
- Kümülatif, çiy noktası tabanlı
- Akdeniz'de on binlere çıkması normal → K formatıyla gösteriliyor
- Dosya: `indeksler.py`

### KBDI — Keetch-Byram (1968)
- Toprak nem eksikliği 0-800
- Yağış eşiği 5.08mm, sıcaklık eşiği 10°C
- Dosya: `indeksler.py`

### Carrega I87 (1991)
- Akdeniz regresyon modeli: `I87 = -4.51 + 0.236T + 0.095δ - 0.038RH`
- **Sınırlama:** Güney Fransa kalibrasyonlu, Türkiye'de yangın günlerinde bile "Orta" çıkabiliyor
- Dosya: `indeksler.py`

---

## 2. Web Arayüzü (5 Sayfa)

| Sayfa | İçerik | Durum |
|---|---|---|
| Hakkında | Proje bilgisi, ekip, 5 indeks, özellikler, veri kaynağı, sistem mimarisi | ✅ Yeniden düzenlendi |
| Hesaplayıcı | Manuel (5 indeks renk kodlu + FWI alt bileşenler detay), Open-Meteo otomatik, CSV | ✅ 5 indeks eşit |
| 7 Günlük Tahmin | Harita + koordinat, 5 indeks çizgi grafik, günlük kartlar (5 indeks) | ✅ 5 indeks eşit |
| Hesaplama Yöntemi | Sekme tabanlı (FWI, Angström, Nesterov, KBDI, Carrega), tümü bar stilinde eşik tablosu | ✅ Güncel |
| Doğrulama | FWI referans testi + 3 yangın olayı (5 indeks renk kodlu, çevrilebilir) | ✅ Güncel |

---

## 3. Dosya Yapısı

```
Claude/
├── app_v2.py            — Flask sunucu, tüm endpoint'ler, Sentry, Basic Auth
├── fwi_hesap.py         — FWI hesaplama motoru (Van Wagner 1987)
├── indeksler.py         — 4 ek indeks: Angström, Nesterov, KBDI, Carrega I87
├── openmeteo.py         — Open-Meteo Archive API (geçmiş veri + retry + dew_point + temp_max)
├── forecast.py          — Open-Meteo Forecast API (7 günlük tahmin + retry + dew_point + temp_max)
├── test_fwi.py          — FWI birim testleri
├── test_indeksler.py    — Ek indeks birim testleri (35 test)
├── requirements.txt     — Python bağımlılıkları
├── Procfile             — gunicorn app_v2:app
├── templates/
│   ├── index_v2.html    — Web arayüzü (SPA, ~3700+ satır)
│   └── index.html       — Eski arayüz (arşiv)
├── docs/
│   ├── CHECKPOINT.md         — Bu doküman
│   ├── FWI_PLAN_DRAFT.md     — Proje planı
│   ├── teknik_referans.md    — FWI formül referansı
│   └── bilimsel_referanslar.md — 5 indeks bilimsel doğrulama raporu
```

---

## 4. Altyapı

### Sunucu (DigitalOcean)
- **Droplet:** ormanyangini-server — Frankfurt (FRA1)
- **Plan:** Regular $6/ay (1 GB RAM, 1 CPU, 25 GB SSD)
- **OS:** Ubuntu 24.04 LTS
- **Kredi:** $200 GitHub Student Pack (Mart 2027'ye kadar)

### Domain & SSL
- **Domain:** fire-ews.tech (get.tech, ücretsiz 1 yıl → Mart 2027)
- **DNS:** A record → 165.22.92.106 (@ ve www)
- **SSL:** Let's Encrypt (certbot + nginx)

### Sunucu Yapısı
- Uygulama: /opt/app — Nginx → Gunicorn (127.0.0.1:5002, 2 worker)
- Systemd: fwi.service + webhook.service
- Firewall (ufw): 22, 80, 443, 9000

### Otomatik Deploy
- GitHub push → webhook (port 9000) → /opt/deploy.sh → git pull + restart

---

## 5. API Endpointleri

| Endpoint | Yöntem | Açıklama |
|---|---|---|
| `/` | GET | Ana sayfa |
| `/hesapla` | POST | Tek gün hesaplama (FWI + 4 ek indeks) |
| `/nasa` | POST | Open-Meteo çoklu gün (tüm indeksler) |
| `/csv` | POST | CSV toplu hesaplama (tüm indeksler) |
| `/tahmin` | POST | 7 günlük tahmin (tüm indeksler) |
| `/referans` | GET | Van Wagner referans testi |
| `/test` | GET | Gerçek yangın olayları (tüm indeksler) |
| `/rapor-pdf` | POST | PDF rapor (tüm indeksler dahil) |

---

## 6. Bilimsel Referanslar

| İndeks | Kaynak | Doğrulama |
|---|---|---|
| FWI | Van Wagner (1987) Forestry Technical Report 35 | ✅ Referans testi + cffdrs R paketi |
| Angström | Angström (1942) Svenska Brandförsvarsföreningen | ✅ El hesabı + WikiFire (WSL) |
| Nesterov | Nesterov (1949) / Shetinsky (1994) eşikleri | ✅ ClimInd R paketi |
| KBDI | Keetch & Byram (1968) USDA Research Paper SE-38 | ✅ Katsayı doğrulaması |
| Carrega | Carrega (1991) Int. J. Wildland Fire 1(2), 79-86 | ✅ Katsayı tutarlılığı |

Detaylı doğrulama: `docs/bilimsel_referanslar.md`

---

## 7. Bilinen Sınırlamalar & Sorunlar

- **Nesterov Akdeniz sorunu:** Rusya için tasarlanmış, Akdeniz'de on binlere çıkıyor → K formatıyla gösteriliyor
- **Carrega Türkiye uyumu:** Güney Fransa kalibrasyonlu, Türkiye'de yangın günlerinde "Orta" çıkabiliyor
- **Grafik işlevselliği:** 5 indeks çizgi grafik (tehlike sınıfı normalize) çalışıyor ama daha işlevsel hale getirilebilir
- **Doğrulama:** Sadece 3 yangın olayı var — 8-10'a çıkarılmalı
- **Mobil:** Temel düzeltmeler yapıldı (z-index, scroll, dil butonu) ama grafik mobilde sınırlı

---

## 8. Hesaplar & Erişim

| Servis | Hesap |
|---|---|
| GitHub | MrFBaker (repo: orman-yangini) |
| DigitalOcean | GitHub ile giriş ($200 kredi aktif) |
| get.tech | ahmetemreekmekci@gmail.com (fire-ews.tech) |
| Sentry | GitHub ile giriş (fire-ews projesi) |
| Sunucu SSH | root@165.22.92.106 |
| Site girişi | admin / fire2026 |

---

## 9. Oturum 1 — 22 Mart 2026

### Altyapı (sıfırdan kuruldu)
1. DigitalOcean Droplet ($6/ay, Frankfurt, $200 kredi)
2. Python + Gunicorn + Nginx + systemd kurulumu
3. fire-ews.tech domain (get.tech, ücretsiz 1 yıl)
4. SSL sertifikası (Let's Encrypt + certbot)
5. Otomatik deploy (GitHub webhook + deploy script)
6. Firewall (ufw — 22, 80, 443, 9000)
7. Sentry hata izleme entegrasyonu
8. Basic Auth şifre koruması
9. noindex/nofollow (arama motorlarından gizleme)
10. Railway silindi (eski altyapı)

### 4 Ek İndeks (sıfırdan eklendi)
11. indeksler.py oluşturuldu (Angström, Nesterov, KBDI, Carrega I87)
12. Bilimsel doğrulama yapıldı (orijinal makalelerle katsayı karşılaştırması)
13. KBDI düzeltmeleri (yağış eşiği 5.08mm, sıcaklık eşiği 10°C)
14. Nesterov sınıf isimleri Shetinsky (1994) referansına hizalandı
15. Open-Meteo modüllerine dew_point ve temp_max verileri eklendi
16. Tüm endpoint'ler ek indekslerle entegre edildi
17. Warmup fonksiyonu genişletildi (KBDI + Nesterov state biriktirme)
18. 35 birim testi yazıldı (test_indeksler.py)
19. bilimsel_referanslar.md oluşturuldu

### Frontend (ilk geçiş)
20–42. Hakkında, Hesaplayıcı, Tahmin, Yöntem, Doğrulama sayfaları güncellendi (detaylar önceki checkpoint'te)

---

## 10. Oturum 2 — 23 Mart 2026

### FWI Odaklı → 5 İndeks Eşit Gösterim
1. **7 Günlük Tahmin:** İstatistik kutuları kaldırıldı, 5 indeks çizgi grafik (tehlike sınıfı normalize, farklı çizgi/nokta stilleri, çakışma önleme ofset)
2. **Hesaplayıcı Otomatik Veri:** Aynı 5 indeks çizgi grafik, istatistik kutuları kaldırıldı
3. **Manuel Hesaplama:** FWI banner kaldırıldı, 5 indeks eşit renk kodlu kutu, FWI alt bileşenleri açılır detay (details/summary)
4. **CSV Backend:** `/csv` endpoint'ine ek indeks entegrasyonu (KBDI₀, Nesterov₀ state tracking)
5. **Gelişmiş Ayarlar:** Manuel ve CSV'ye KBDI₀ ve Nesterov₀ başlangıç değerleri eklendi

### i18n — Kapsamlı Çeviri Düzeltmesi
6. Özellikler kartı: badge + açıklama çevirileri (Harita→Map, Tahmin→Forecast, Oto Veri→Auto Data)
7. Veri kaynağı: Çiy Noktası→Dew Point, T_max açıklamaları
8. Form label'ları: Çiy Noktası (°C), T_max (°C), Enlem (opsiyonel)
9. Gelişmiş Ayarlar: FWI Başlangıç→FWI Initial Values, Kümülatif İndeks Başlangıç→Cumulative Index Initial Values
10. FWI Alt Bileşenleri → FWI Sub-Components
11. Sistem Mimarisi: Meteorolojik Veri→Meteorological Data, Tehlike Seviyesi→Danger Level
12. Kullanılan İndeksler: 5 indeks açıklaması EN çevirileri
13. Doğrulama: girdi bilgisi, ek indeks notu, yangın isimleri (Manavgat Fire vb.)
14. CSV bölümü: Sütunları başlığı ve açıklama çevirisi
15. Sayfa title: Fire-EWS uyumu
16. card_features_title TR/EN tanımı eklendi

### Hesaplama Yöntemi
17. Tüm 5 indeks tehlike sınıfları aynı bar stiliyle (tehlike-olcek) — FWI eskisi gibi, diğerleri de aynı
18. Angström/Nesterov/KBDI/Carrega panelleri lang-tr dışına taşındı (EN'de de görünür)
19. EN FWI paneli yontem-panel class'ıyla sarıldı, sekme değiştirme düzgün çalışıyor
20. FWI Sistemi sekme butonu data-i18n eklendi

### Hakkında Sayfası Yeniden Düzenleme
21. Proje + Ekip: tam genişlik kart, ekip isimleri (Ahmet Emre EKMEKCİ, Ahsen REYHAN, Doğukan TOPAL, Sedanur BAYAZTAŞ, Zeynep Selma OTLUOĞLU)
22. İndeksler: tam genişlik kart
23. Özellikler + Veri Kaynağı: yan yana 2 sütun (mobilde 1 sütun)
24. Sistem Mimarisi: tam genişlik akış diyagramı
25. Badge'ler sabit 56px genişlik — yazılar hizalı
26. Open-Meteo açıklama metni 5 indeks kapsayacak şekilde güncellendi

### Mobil Düzeltmeler
27. Harita container z-index:0 — sidebar/overlay üst üste binme düzeltildi
28. Metodoloji sekmeleri: mobilde yatay scroll, gap ile ayrık, pill stili
29. Dil seçimi sidebar'da nav linklerinin hemen altına taşındı
30. Sistem Mimarisi mobilde dikey akış (oklar ↓, indeksler 3 sütun grid)
31. Grafik mobil: yatay scroll wrapper, kısa Y ekseni etiketleri (D, O, Y, ÇY, A), legend altta

---

## 11. Sonraki Oturum İçin Yapılacaklar

### Öncelikli
- [ ] **Grafikleri iyileştir** — mevcut çizgi grafik işlevsel değil, daha kullanışlı bir görselleştirme bul
- [ ] **Mobil genel test** — tüm sayfaları telefonda kontrol et, kalan sorunları düzelt

### Orta Öncelik
- [ ] Daha fazla yangın olayı (3 → 8-10)
- [ ] Loading animasyonları (API çağrıları sırasında spinner)
- [ ] i18n kalan eksikler (metodoloji formül adımları, açıklamalar)

### Düşük Öncelik
- [ ] Tarihsel trend analizi
- [ ] Favori konumlar (localStorage)
- [ ] Türkiye tehlike haritası

---

## 12. Görev Dağılımı (Takım)

| Kişi | Görev | Durum |
|---|---|---|
| Sedanur BAYAZTAŞ | KBDI + FWI DC/DMC (uzun vadeli kuraklık) | ✅ Kod tamamlandı |
| Ahmet Emre EKMEKCİ | ISI, BUI, FWI + Sistem Tasarımı | ✅ Kod tamamlandı |
| Zeynep Selma OTLUOĞLU | Nesterov + FWI FFMC (anlık tutuşma) | ✅ Kod tamamlandı |
| Ahsen REYHAN | Carrega I87 + Angström (günlük su dengesi) | ✅ Kod tamamlandı |
| Doğukan TOPAL | Meteorolojik Veri Altyapısı | ✅ openmeteo.py + forecast.py |
