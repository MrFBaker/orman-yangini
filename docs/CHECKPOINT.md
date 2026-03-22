# Proje Checkpoint — 22 Mart 2026 (Son güncelleme: 22 Mart 2026 akşam)

## Proje Adı
**Fire-EWS — Meteorolojik Veri Tabanlı Orman Yangını Erken Uyarı Sistemi**

## Canlı Site
- **URL:** https://fire-ews.tech
- **IP:** 165.22.92.106
- **Giriş:** admin / fire2026 (Basic Auth)

---

## 1. Ne Yaptık?

### Hesaplama Motoru
- Van Wagner (1987) FWI formüllerinin tam uygulaması
- 6 alt bileşen: FFMC, DMC, DC, ISI, BUI, FWI + DSR
- Enleme göre dinamik Le/Lf tablo seçimi (Türkiye: 36-42°N)
- Warmup sistemi: 1 Ocak'tan itibaren başlangıç değerleri biriktirme
- Kanada standart tehlike sınıfı eşikleri (Düşük/Orta/Yüksek/Çok Yüksek/Aşırı)

### Web Arayüzü (5 Sayfa — Tek Sayfa Uygulama)
1. **Hakkında** — Proje tanıtımı
2. **Hesaplayıcı** — Manuel giriş, Open-Meteo otomatik veri çekimi, CSV toplu hesaplama
3. **7 Günlük Tahmin** — Open-Meteo Forecast API ile gelecek 7 gün FWI tahmini
4. **Hesaplama Yöntemi** — Formüller, akış diyagramı, eşik tabloları
5. **Doğrulama** — Van Wagner referans testi + gerçek yangın olayları (Manavgat, Marmaris, İzmir)

### Özellikler
- Leaflet.js interaktif haritalar (Esri uydu görüntüsü + sınır etiketleri)
- Haritaya tıklayarak veya koordinat girerek konum seçimi (çift yönlü senkronizasyon)
- Chart.js grafikleri (zaman serisi çizgi grafik + tahmin bar grafik)
- PDF rapor indirme (manuel ve çoklu hesaplama sonuçları)
- TR/EN dil desteği (~260+ çeviri anahtarı)
- Dark tema arayüz
- Formül açıklamaları şık badge'lerle (f-not CSS sınıfı)

### API Endpointleri
| Endpoint | Yöntem | Açıklama |
|---|---|---|
| `/` | GET | Ana sayfa |
| `/hesapla` | POST | Tek günlük manuel FWI hesaplama |
| `/nasa` | POST | Open-Meteo Archive API ile çoklu gün hesaplama |
| `/csv` | POST | CSV dosyasından toplu hesaplama |
| `/tahmin` | POST | 7 günlük FWI tahmini |
| `/referans` | GET | Van Wagner referans testi |
| `/test` | GET | Gerçek yangın olaylarıyla doğrulama |
| `/rapor-pdf` | POST | PDF rapor oluşturma |

---

## 2. Dosya Yapısı

```
Claude/
├── app_v2.py           — Flask sunucu + tüm API endpointleri + Sentry
├── fwi_hesap.py        — FWI hesaplama motoru (Van Wagner formülleri)
├── openmeteo.py        — Open-Meteo Archive API (geçmiş veri + retry)
├── forecast.py         — Open-Meteo Forecast API (7 günlük tahmin + retry)
├── test_fwi.py         — Birim testleri
├── requirements.txt    — Python bağımlılıkları
├── Procfile            — Deploy yapılandırması (gunicorn app_v2:app)
├── vercel.json         — Vercel yapılandırması (yedek)
├── templates/
│   ├── index_v2.html   — Web arayüzü (SPA, ~3000+ satır)
│   └── index.html      — Eski arayüz (arşiv)
├── docs/
│   ├── CHECKPOINT.md   — Bu doküman
│   ├── FWI_PLAN_DRAFT.md   — Proje planı (güncel)
│   └── teknik_referans.md  — Formül referans dokümanı
```

---

## 3. Altyapı

### Sunucu (DigitalOcean)
- **Droplet:** ormanyangini-server
- **IP:** 165.22.92.106
- **Region:** Frankfurt (FRA1)
- **Plan:** Regular $6/ay (1 GB RAM, 1 CPU, 25 GB SSD)
- **OS:** Ubuntu 24.04 LTS
- **Kredi:** $200 GitHub Student Pack (Mart 2027'ye kadar, ~33 ay yeter)

### Domain & SSL
- **Domain:** fire-ews.tech (get.tech, 1 yıl ücretsiz → Mart 2027)
- **DNS:** A record → 165.22.92.106 (@ ve www)
- **SSL:** Let's Encrypt (certbot + nginx, otomatik yenileme)

### Sunucu Yapısı
- **Uygulama:** /opt/app (git clone)
- **Virtual env:** /opt/app/venv
- **Web stack:** Nginx → reverse proxy → Gunicorn (127.0.0.1:5002, 2 worker)
- **Systemd:** fwi.service (otomatik başlatma + crash recovery)
- **Nginx config:** /etc/nginx/sites-available/fwi

### Otomatik Deploy
- GitHub'a push → webhook tetiklenir → sunucu otomatik güncellenir
- **Webhook:** /opt/webhook.py (Flask, port 9000)
- **Deploy script:** /opt/deploy.sh (git pull → pip install → restart fwi)
- **GitHub webhook URL:** http://165.22.92.106:9000/deploy
- **Systemd:** webhook.service

### Güvenlik
- **Firewall (ufw):** Sadece 22, 80, 443, 9000 portları açık
- **Sentry:** Hata izleme aktif (sentry.io, fire-ews projesi)
- **Basic Auth:** admin / fire2026 (deploy endpoint hariç)
- **noindex/nofollow:** Arama motorlarından gizli

### Eski Altyapı (silindi)
- Railway → silindi (paylaşımlı IP Open-Meteo rate limit sorununa neden oluyordu)

---

## 4. Teknoloji Yığını

| Katman | Teknoloji |
|---|---|
| Backend | Python, Flask |
| Hesaplama | fwi_hesap.py (Van Wagner 1987) |
| Hava verisi (geçmiş) | Open-Meteo Archive API |
| Hava verisi (tahmin) | Open-Meteo Forecast API |
| Frontend | HTML, CSS, JavaScript (SPA) |
| Harita | Leaflet.js + Esri World Imagery |
| Grafik | Chart.js |
| PDF | ReportLab |
| Web sunucu | Nginx + Gunicorn |
| Hosting | DigitalOcean |
| Domain | fire-ews.tech (get.tech) |
| SSL | Let's Encrypt (certbot) |
| Hata izleme | Sentry |
| Versiyon kontrolü | Git + GitHub (MrFBaker/orman-yangini) |
| Deploy | Otomatik (GitHub webhook) |

---

## 5. Kaynaklar & Referanslar

| Kaynak | Ne İçin |
|---|---|
| Van Wagner (1987) — Forestry Technical Report 35 | FWI formülleri |
| cffdrs R paketi (bcgov/cffdrs) | Formül doğrulama |
| EFFIS (Avrupa Komisyonu) | Akdeniz tehlike eşikleri |
| Open-Meteo / ERA5 (ECMWF) | Hava verisi |

---

## 6. Bilinen Sorunlar

- Open-Meteo Forecast API zaman zaman 429 (rate limit) verebilir — retry mekanizması ekli (üstel bekleme, 3 deneme). DigitalOcean'a taşındıktan sonra sorun çözüldü.
- Doğrulama sayfasında sadece 3 yangın olayı var — daha fazla eklenmeli
- Mobil uyumluluk iyileştirmeleri yapıldı (dokunma alanları, grid'ler, font boyutları) — telefonda test edilmeli

---

## 7. Gelecek Planları

### Kısa Vadeli
- Daha fazla yangın olayı ile doğrulama
- Yükleme animasyonları
- Favori konumlar (localStorage)

### Orta Vadeli
- Tarihsel trend analizi
- Çoklu konum karşılaştırması
- Takvim heatmap
- PWA (Progressive Web App)

### Uzun Vadeli
- Türkiye tehlike haritası (heatmap)
- Otomatik bildirim sistemi (email)
- Uydu verisi entegrasyonu (MODIS/VIIRS)
- ~~Ek yangın indeksleri~~ → 4 tanesi eklendi (aşağıya bak), frontend entegrasyonu kısmen tamamlandı

---

## 8. Hesaplar & Erişim

| Servis | Hesap |
|---|---|
| GitHub | MrFBaker (repo: orman-yangini) |
| DigitalOcean | GitHub ile giriş ($200 kredi aktif) |
| get.tech | ahmetemreekmekci@gmail.com (fire-ews.tech domain) |
| Sentry | GitHub ile giriş (fire-ews projesi) |
| Sunucu SSH | root@165.22.92.106 |
| Site girişi | admin / fire2026 |

## 9. Bu Oturumda Yapılanlar (22 Mart 2026)

1. Sidebar sırası düzeltildi (7 Günlük Tahmin → Hesaplayıcı'dan sonra)
2. Formüllerdeki parantez açıklamaları şık badge'lere dönüştürüldü (.f-not)
3. FWI_PLAN_DRAFT.md güncellendi (tamamlanan özellikler, Türkçe karakterler)
4. Eski planlama dosyaları temizlendi (faz1, faz2, plan.md)
5. Railway'e push + deploy (Procfile app_v2 olarak güncellendi)
6. API retry mekanizması eklendi (429 rate limit çözümü)
7. DigitalOcean Droplet oluşturuldu ($6/ay, Frankfurt)
8. Sunucu kurulumu (Python, Gunicorn, Nginx, systemd)
9. fire-ews.tech domain alındı (get.tech, ücretsiz 1 yıl)
10. SSL sertifikası (Let's Encrypt + certbot)
11. Otomatik deploy (GitHub webhook + deploy script)
12. Firewall ayarı (ufw)
13. Sentry hata izleme entegrasyonu
14. Railway silindi
15. Mobil uyumluluk iyileştirmeleri (dokunma alanları, grid'ler, breakpoint'ler)
16. FWI System → Fire-EWS isim değişikliği
17. Title, favicon güncellendi
18. noindex/nofollow (arama motorlarından gizleme)
19. Basic Auth şifre koruması (admin/fire2026)
20. 4 ek yangın indeksi: Angström, Nesterov, KBDI, Carrega I87 (indeksler.py)
21. Open-Meteo modüllerine dew_point ve temp_max verileri eklendi
22. Tüm endpoint'ler ek indekslerle entegre edildi
23. Frontend: manuel hesaplama, tablo, tahmin kartları, doğrulama — 5 indeks eşit seviyede
24. Türkçe karakter desteği (sinifCevir fonksiyonu)
25. Hesaplama Yöntemi: sekme tabanlı yapı + her indekse özel eşik tablosu
26. Doğrulama: 5 indeks renk kodlu karşılaştırmalı test kartları
27. 35 birim testi (test_indeksler.py)
28. Tablo sadeleştirildi (FWI alt bileşenleri kaldırıldı)
29. Hakkında sayfası + akış diyagramı + footer güncellendi
30. Nesterov K formatı (25188 → 25.2K)
31. bilimsel_referanslar.md oluşturuldu
32. Sidebar taşma düzeltildi, badge'ler kısaltıldı

## 10. Eklenen 4 Yeni İndeks

| İndeks | Kaynak | Dosya | Durum |
|---|---|---|---|
| Angström | Angström (1942) | indeksler.py | ✅ Backend + Frontend tamam |
| Nesterov | Nesterov (1949) / Shetinsky (1994) | indeksler.py | ✅ Backend + Frontend tamam |
| KBDI | Keetch & Byram (1968) USDA SE-38 | indeksler.py | ✅ Backend + Frontend tamam |
| Carrega I87 | Carrega (1991) Int. J. Wildland Fire | indeksler.py | ✅ Backend + Frontend tamam |

### Bilimsel Doğrulama Yapıldı
- Tüm formüller orijinal makalelerle karşılaştırıldı
- KBDI: yağış eşiği 5.08mm (0.20 inç), sıcaklık eşiği 10°C eklendi
- Nesterov: sınıf isimleri Shetinsky (1994) referansına hizalandı
- El hesabı doğrulaması: Angström T=25/RH=30 → 1.7 ✅

### Tamamlanan Ek İşler (aynı oturum)
- [x] Hesaplama Yöntemi: sekme tabanlı yapı (FWI, Angström, Nesterov, KBDI, Carrega)
- [x] Her indeksin kendi eşik tablosu kendi sekmesinde
- [x] Doğrulama sayfası: 5 indeks renk kodlu karşılaştırmalı test kartları
- [x] test_indeksler.py: 35 birim testi (tümü geçiyor)
- [x] Tablo sadeleştirildi: FWI alt bileşenleri kaldırıldı, 5 indeks renk kodlu
- [x] Tahmin kartları: 5 indeks eşit seviyede renk kodlu
- [x] Hakkında sayfası güncellendi (5 indeks, özellikler kartı)
- [x] Akış diyagramı güncellendi (5 indeks birlikte)
- [x] İndeks badge'leri kısaltıldı (ANG, NES, CAR)
- [x] Sidebar taşma düzeltildi (iki satır)
- [x] Nesterov büyük değerler K formatında (25188 → 25.2K)
- [x] Footer güncellendi (Fire-EWS + 5 indeks)
- [x] bilimsel_referanslar.md oluşturuldu

### Bilinen Sınırlamalar
- **Nesterov:** Akdeniz ikliminde on binlere çıkması normal (Rusya için tasarlanmış, uzun kurak dönemde kümülatif birikim). K formatıyla gösteriliyor.
- **Carrega I87:** Güney Fransa kalibrasyonlu, Türkiye yaz sıcaklıkları daha yüksek olduğu için büyük yangın günlerinde bile "Orta" çıkabiliyor. Eşikler yerel kalibrasyon gerektirebilir.

### Kalan İşler
- [ ] Mobil görünüm test edilmeli (telefonda kontrol)
- [ ] Daha fazla yangın olayı eklenmeli (3'ten 8-10'a çıkarılmalı)
- [ ] İngilizce çeviriler güncellenecek (yeni eklenen metinler)

## 11. Görev Dağılımı (Takım)

| Kişi | Görev | Durum |
|---|---|---|
| Seda | KBDI + FWI DC/DMC (uzun vadeli kuraklık) | ✅ Kod tamamlandı |
| Emre | ISI, BUI, FWI + Sistem Tasarımı | ✅ Kod tamamlandı |
| Zeynep | Nesterov + FWI FFMC (anlık tutuşma) | ✅ Kod tamamlandı |
| Ahsen | Carrega I87 + Angström (günlük su dengesi) | ✅ Kod tamamlandı |
| Doğukan | Meteorolojik Veri Altyapısı | ✅ openmeteo.py + forecast.py |
