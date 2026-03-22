# Proje Checkpoint — 22 Mart 2026 (Son güncelleme: 22 Mart 2026 gece)

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
| Hakkında | 5 indeks tanıtımı, özellikler, veri kaynağı, sistem mimarisi | ✅ Güncel |
| Hesaplayıcı | Manuel giriş (T, RH, W, P, Td, T_max), Open-Meteo otomatik, CSV | ✅ 5 indeks |
| 7 Günlük Tahmin | Harita + koordinat, bar grafik, günlük kartlar | ⚠️ Grafik/istatistik hala FWI odaklı |
| Hesaplama Yöntemi | Sekme tabanlı (FWI, Angström, Nesterov, KBDI, Carrega), her biri eşik tablolu | ✅ Güncel |
| Doğrulama | FWI referans testi + 3 yangın olayı (5 indeks renk kodlu) | ✅ Güncel |

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
│   ├── index_v2.html    — Web arayüzü (SPA, ~3500+ satır)
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
| `/csv` | POST | CSV toplu hesaplama |
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
- **7 Günlük Tahmin:** Grafik ve istatistikler hala sadece FWI odaklı — 5 indeks eşit gösterilmeli
- **CSV hesaplama:** Backend'de ek indeks entegrasyonu eksik (sadece FWI hesaplıyor)
- **Doğrulama:** Sadece 3 yangın olayı var — 8-10'a çıkarılmalı
- **Mobil:** Test edilmeli
- **İngilizce çeviriler:** Yeni eklenen metinler çevrilmedi

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

## 9. Bu Oturumda Yapılanlar (22 Mart 2026)

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

### Frontend Güncellemeleri
20. Hakkında sayfası: 5 indeks, özellikler kartı, sistem mimarisi diyagramı
21. Hesaplayıcı: manuel formda çiy noktası + T_max alanları
22. Hesaplayıcı: tablo sadeleştirildi (FWI alt bileşenleri kaldırıldı, 5 indeks renk kodlu)
23. Hesaplayıcı: sonuç alanında tüm indeksler eşit seviyede
24. 7 Günlük Tahmin: kartlarda 5 indeks eşit seviyede renk kodlu
25. Hesaplama Yöntemi: sekme tabanlı yapı (FWI, Angström, Nesterov, KBDI, Carrega)
26. Hesaplama Yöntemi: her indekse özel formül kartları + eşik tabloları
27. Doğrulama: test kartlarında 5 indeks renk kodlu
28. Doğrulama: backend ek indeksler döndürüyor
29. PDF rapor: manuel ve çoklu gün raporlarında 4 ek indeks
30. CSV format açıklaması güncellendi (badge'li gösterim)
31. Nesterov büyük değerler K formatında (25188 → 25.2K)
32. Türkçe karakter desteği (sinifCevir, Yangını, Muğla, İzmir)

### UI/UX Düzeltmeleri
33. FWI System → Fire-EWS isim değişikliği
34. Sidebar taşma düzeltildi (iki satır)
35. İndeks badge'leri kısaltıldı (ANG, NES, CAR)
36. Title, favicon güncellendi
37. Footer: Fire-EWS + 5 indeks
38. Formüllerdeki parantez açıklamaları şık badge'lere dönüştürüldü
39. Mobil uyumluluk iyileştirmeleri (dokunma alanları, grid'ler, breakpoint'ler)
40. Özellikler kartı düzenlendi (badge hizalama, boşluk)
41. Referans testi başlığı güncellendi + ek indeks doğrulama notu
42. API retry mekanizması (429 rate limit)

---

## 10. Sonraki Oturum İçin Yapılacaklar

### Öncelikli
- [ ] **7 Günlük Tahmin** grafik ve istatistikleri 5 indeks eşit gösterecek şekilde güncelle
- [ ] **CSV hesaplama** backend'de ek indeks entegrasyonu
- [ ] **Mobil test** — telefonda kontrol, sorunları düzelt

### Orta Öncelik
- [ ] Daha fazla yangın olayı (3 → 8-10)
- [ ] İngilizce çeviriler güncelleme
- [ ] Loading animasyonları

### Düşük Öncelik
- [ ] Tarihsel trend analizi
- [ ] Favori konumlar (localStorage)
- [ ] Türkiye tehlike haritası

---

## 11. Görev Dağılımı (Takım)

| Kişi | Görev | Durum |
|---|---|---|
| Seda | KBDI + FWI DC/DMC (uzun vadeli kuraklık) | ✅ Kod tamamlandı |
| Emre | ISI, BUI, FWI + Sistem Tasarımı | ✅ Kod tamamlandı |
| Zeynep | Nesterov + FWI FFMC (anlık tutuşma) | ✅ Kod tamamlandı |
| Ahsen | Carrega I87 + Angström (günlük su dengesi) | ✅ Kod tamamlandı |
| Doğukan | Meteorolojik Veri Altyapısı | ✅ openmeteo.py + forecast.py |
