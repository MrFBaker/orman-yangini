# FWI Orman Yangını Erken Uyarı Sistemi

## Bu Proje Nedir?

Bu proje, meteorolojik verileri kullanarak orman yangını tehlike seviyesini önceden hesaplayan
web tabanlı bir erken uyarı sistemidir. Meteoroloji Mühendisliği bölümü tasarım projesi olarak
geliştirilmiştir.

Sistem, kullanıcıdan aldığı hava durumu bilgilerini (sıcaklık, nem, rüzgar, yağış) matematiksel
formüllere sokarak o gün için yangın tehlike seviyesini belirler. Sonuç olarak "Düşük", "Orta",
"Yüksek", "Çok Yüksek" veya "Aşırı" şeklinde bir tehlike sınıfı üretir.


## Neden Bu Projeyi Yapıyoruz?

Türkiye, özellikle Akdeniz ve Ege kuşağında her yıl ciddi orman yangınları yaşayan bir ülkedir.
2021 yazında Manavgat ve Marmaris'te yaşanan felaketler, erken uyarı sistemlerinin ne kadar
kritik olduğunu bir kez daha göstermiştir.

Mevcut durumda Türkiye'de kamuya açık, meteorolojik veriye dayalı, otomatik çalışan bir FWI
hesaplama aracı bulunmamaktadır. Bu proje, bu boşluğu doldurmak amacıyla uluslararası kabul
görmüş bilimsel bir yöntemi (Van Wagner FWI) Türkiye koşullarına uyarlayarak herkesin
erişebileceği bir web uygulaması haline getirmeyi hedefler.


## Hedeflerimiz

1. Van Wagner (1987) FWI formüllerini bilimsel olarak doğru biçimde uygulamak
2. Türkiye'nin Akdeniz iklim kuşağına uygun tehlike eşiklerini (EFFIS) kullanmak
3. Gerçek hava verisiyle otomatik çalışan, kullanıcı dostu bir web arayüzü sunmak
4. Hesaplamaların doğruluğunu referans testler ve gerçek yangın olaylarıyla kanıtlamak
5. Sistemi herkesin erişebileceği şekilde canlı olarak yayımlamak


## Hangi Yöntemi Kullanıyor?

Sistem, Kanada Orman Servisi'nin 1987 yılında yayımladığı FWI (Fire Weather Index) yöntemini
kullanır. Bu yöntemi C.E. Van Wagner geliştirmiştir ve bugün dünyada en yaygın kullanılan
orman yangını tehlike değerlendirme sistemidir.

FWI sistemi tek bir sayı değil, birbirine bağlı 6 alt bileşenden oluşur:

**Nem Kodları (önceki günlerin etkisini taşır):**
- FFMC — İnce Üst Tabaka Yanıcı Madde Nem Kodu: Ölü örtünün üst tabakasındaki küçük dallar,
  yapraklar gibi ince yanıcı maddelerin ne kadar kuru olduğunu gösterir. Birkaç saat içinde kurur veya nemlenir.
- DMC — Döküntü Nem Kodu: Orta derinlikteki hafif sıkıştırılmış organik (döküntü) tabakasının
  nem durumunu gösterir. Kuruması veya nemlenmesi birkaç gün sürer.
- DC — Derin Organik Tabaka Nem Kodu: Derin sıkıştırılmış organik tabakasının
  nem durumunu ölçer. Mevsimsel kuraklığın etkisini gösterir. Haftalarca sürecek bir gösterge.

**Davranış İndisleri (o anki koşulları yansıtır):**
- ISI — İlk Yayılma İndeksi: Rüzgar hızı ve FFMC'den hesaplanır. Bir yangın başlarsa
  ne kadar hızlı yayılacağını tahmin eder.
- BUI — Birikmiş Yanıcı Madde İndeksi: DMC ve DC'den hesaplanır. Yanacak malzeme miktarını,
  yani yangının ne kadar şiddetli olacağını gösterir.
- FWI — Yangın Hava İndeksi: ISI ve BUI'yi birleştiren nihai skor. Genel yangın
  tehlike seviyesini tek bir sayıyla ifade eder.

Hesaplama sırası şöyledir:
Hava verileri → FFMC, DMC, DC → ISI, BUI → FWI


## Türkiye İçin Ne Yapıldı?

FWI formüllerinin kendisi evrenseldir ve değiştirilmez. Ancak iki noktada bölgesel uyarlama
yapılmıştır:

1. **Gün uzunluğu faktörleri:** DMC ve DC hesaplarında kullanılan Le ve Lf değerleri enleme
   göre değişir. Sistem, kullanıcının girdiği koordinata göre Türkiye'nin enlem bandına
   (36-42 derece Kuzey) uygun tabloyu otomatik seçer.

2. **Tehlike sınıfı eşikleri:** Kanada'nın standart eşikleri yerine, Avrupa Orman Yangını
   Bilgi Sistemi'nin (EFFIS) Akdeniz iklimi için belirlediği eşikler kullanılmaktadır.
   Türkiye'nin Akdeniz iklim kuşağında olması nedeniyle bu eşikler daha gerçekçi sonuçlar
   üretir.


## Sistem Nasıl Çalışıyor?

Kullanıcının üç seçeneği vardır:

**Manuel Giriş:** Kullanıcı sıcaklık, nem, rüzgar hızı, yağış ve ay bilgisini elle girer.
Sistem anında FWI hesaplar ve tehlike sınıfını gösterir.

**Otomatik Hesaplama (Open-Meteo):** Kullanıcı haritaya tıklayarak veya elle enlem/boylam
ve tarih aralığı girer. Sistem, Open-Meteo Archive API üzerinden o konumun gerçek hava
verilerini otomatik olarak çeker ve her gün için ayrı ayrı FWI hesaplar. Sonuçlar tablo
ve grafik halinde gösterilir, PDF olarak indirilebilir.

**7 Günlük Tahmin:** Kullanıcı haritadan konum seçer veya koordinat girer. Open-Meteo
Forecast API üzerinden önümüzdeki 7 günün tahmini hava verileri çekilir, FWI hesaplanır.
Sonuçlar bar grafik ve günlük kartlar halinde gösterilir.

Hava verileri öğle saati (12:00 yerel saat) değerleri olarak alınır. Bunun sebebi,
Van Wagner'in FWI formüllerini öğle gözlemleri üzerine tasarlamış olmasıdır.

**Warmup Sistemi:** Hem otomatik hesaplama hem 7 günlük tahmin, 1 Ocak'tan itibaren
geçmiş verileri kullanarak FFMC/DMC/DC başlangıç değerlerini biriktirerek doğru sonuçlar üretir.


## Doğrulama Nasıl Yapıldı?

Sistemin doğru hesap yaptığını kanıtlamak için iki yöntem kullanılmıştır:

1. **Van Wagner Referans Testi:** Van Wagner'in raporundaki bilinen girdi değerleriyle
   (T=17°C, H=%42, W=25 km/h, r=0 mm) hesaplama yapılır. Sonuçlar beklenen çıktılarla
   karşılaştırılır. Tüm ara adımlar (mo, ed, ew, K, Lf vb.) ayrı ayrı gösterilir.

2. **Gerçek Yangın Olayları:** Türkiye'de yaşanmış büyük orman yangınlarının
   (2021 Manavgat, 2021 Marmaris, 2019 İzmir) tarih ve koordinatları girilir. O günün
   gerçek hava verileriyle FWI hesaplanır. Beklenti, bu olayların yüksek tehlike
   sınıfına düşmesidir — ki öyle çıkmıştır.


## Hangi Kaynaklar Kullanılıyor?

| Kaynak | Ne İçin | Güvenilirlik |
|---|---|---|
| Van Wagner (1987) — Forestry Technical Report 35 | Tüm FWI formülleri | Kanada Orman Servisi resmi yayını, 37 yıldır dünya standardı |
| cffdrs R paketi (bcgov/cffdrs) | Formül ve katsayı doğrulama | Kanada hükümetinin açık kaynaklı referans uygulaması |
| EFFIS (Avrupa Komisyonu) | Akdeniz tehlike sınıfı eşikleri | AB resmi orman yangını bilgi sistemi |
| Open-Meteo / ERA5 (ECMWF) | Gerçek zamanlı ve tahmin hava verisi | Dünya genelinde en çok kullanılan atmosfer yeniden analiz verisi |


## Teknik Altyapı

| Bileşen | Teknoloji |
|---|---|
| Hesaplama motoru | Python (fwi_hesap.py) |
| Web sunucu | Flask (app_v2.py) |
| Geçmiş hava verisi API | Open-Meteo Archive API (openmeteo.py) |
| Tahmin hava verisi API | Open-Meteo Forecast API (forecast.py) |
| PDF rapor | ReportLab (app_v2.py içinde) |
| Arayüz | HTML/CSS/JavaScript — tek sayfa uygulama (SPA) |
| Harita | Leaflet.js + Esri World Imagery (uydu görüntüsü) |
| Grafik | Chart.js (zaman serisi + tahmin bar grafikleri) |
| Çok dilli destek | TR/EN — ~260+ çeviri anahtarı (i18n) |
| Birim testleri | Python unittest (test_fwi.py) |


## Projenin Dosya Yapısı

```
Claude/
├── fwi_hesap.py        — FWI hesaplama motoru (Van Wagner formülleri)
├── app_v2.py           — Flask web sunucusu ve tüm API endpointleri
├── openmeteo.py        — Open-Meteo Archive API ile geçmiş veri çekme
├── forecast.py         — Open-Meteo Forecast API ile 7 günlük tahmin
├── test_fwi.py         — Birim testleri
├── templates/
│   ├── index_v2.html   — Web arayüzü (tek sayfa, tüm sekmeler dahil)
│   └── index.html      — Eski arayüz (arşiv)
├── docs/
│   ├── FWI_PLAN_DRAFT.md   — Bu doküman
│   └── teknik_referans.md  — Formül referans dokümanı
├── requirements.txt    — Python bağımlılıkları
└── Procfile            — Deploy yapılandırması
```


## Tamamlanan Özellikler

### Temel Hesaplama
- [x] Van Wagner (1987) FWI formüllerinin tam uygulaması (FFMC, DMC, DC, ISI, BUI, FWI, DSR)
- [x] Enleme göre dinamik Le/Lf tablo seçimi
- [x] Kanada standart tehlike sınıfı eşikleri
- [x] Warmup sistemi (1 Ocak'tan itibaren başlangıç değeri biriktirme)

### Web Arayüzü (5 Sayfa)
- [x] **Hakkında** — Projenin tanıtımı ve başlangıç sayfası
- [x] **Hesaplayıcı** — Manuel giriş, Open-Meteo otomatik veri çekimi, CSV toplu hesaplama
- [x] **7 Günlük Tahmin** — Open-Meteo Forecast API ile gelecek 7 günün FWI tahmini
- [x] **Hesaplama Yöntemi** — Tüm formüllerin adım adım açıklaması, akış diyagramı, eşik tabloları
- [x] **Doğrulama** — Van Wagner referans testi + gerçek yangın olayları (Manavgat, Marmaris, İzmir)

### Etkileşimli Özellikler
- [x] Leaflet.js interaktif haritalar (Esri uydu görüntüsü + sınır etiketleri)
- [x] Haritaya tıklayarak veya koordinat girerek konum seçimi (çift yönlü senkronizasyon)
- [x] Chart.js grafikleri (zaman serisi çizgi grafik + tahmin bar grafik)
- [x] PDF rapor indirme (manuel ve çoklu hesaplama sonuçları için)
- [x] TR/EN dil desteği (~260+ çeviri anahtarı)
- [x] Dark tema arayüz

### API Endpointleri
- [x] `POST /hesapla` — Tek günlük manuel FWI hesaplama
- [x] `POST /nasa` — Open-Meteo Archive API ile çoklu gün hesaplama
- [x] `POST /csv` — CSV dosyasından toplu hesaplama
- [x] `POST /tahmin` — 7 günlük FWI tahmini
- [x] `GET /referans` — Van Wagner referans testi
- [x] `GET /test` — Gerçek yangın olaylarıyla doğrulama
- [x] `POST /rapor-pdf` — PDF rapor oluşturma


## Mevcut Eksiklikler ve İyileştirme Fırsatları

1. **Mobil Uyumluluk İyileştirmeleri:** Bazı butonların ve sekme başlıklarının dokunma alanları
   mobil cihazlarda küçük kalıyor (minimum 44px olmalı). Küçük ekranlarda bazı kartların
   iç boşluğu azaltılmalı.

2. **Daha Fazla Validasyon Olayları:** Şu an 3 yangın olayıyla doğrulama yapılıyor
   (Manavgat, Marmaris, İzmir). En az 8-10 olaya çıkarılması sistemin güvenilirliğini
   daha güçlü kanıtlar.


## Gelecek Planlaması — Eklenebilecek Özellikler

### Kısa Vadeli (Düşük Efor)
- **Daha Fazla Yangın Olayları:** Validasyon sayfasına 2022-2024 arası Türkiye yangınları
  eklenerek doğrulama veri seti genişletilebilir.
- **Yükleme Animasyonları:** API çağrıları sırasında skeleton loader veya progress göstergesi.
- **Favori Konumlar:** Sık kullanılan konumları localStorage'da saklama.

### Orta Vadeli (Orta Efor)
- **Tarihsel Trend Analizi:** Seçilen konum için geçmiş 1 yılın FWI değerlerini grafik
  olarak göstermek. Mevsimsel örüntüleri ve en riskli dönemleri görselleştirmek.
- **Çoklu Konum Karşılaştırması:** Birden fazla konumun FWI değerlerini yan yana karşılaştırma.
- **Takvim Heatmap:** Yıllık FWI değerlerini takvim formatında renk kodlu gösterme.
- **PWA (Progressive Web App):** Offline kullanım ve mobil ana ekrana ekleme desteği.

### Uzun Vadeli (Yüksek Efor)
- **Türkiye Tehlike Haritası:** Birden fazla konum için toplu FWI hesaplayıp harita
  üzerinde renk kodlu (heatmap) göstermek. Hangi bölgenin o gün en riskli olduğunu
  tek bakışta görmek mümkün olur.
- **Otomatik Bildirim Sistemi:** Kullanıcının bir konumu kaydetmesi ve FWI belirli
  eşiği aştığında e-posta ile uyarılması.
- **Uydu Verisi Entegrasyonu:** MODIS veya VIIRS uydu verileriyle gerçek yangın
  noktalarını harita üzerinde göstermek ve FWI tahminleriyle karşılaştırmak.

### Altyapı
- **DigitalOcean'a Taşıma:** Proje büyüdükçe Railway'den DigitalOcean'a geçiş yapılacak.
  GitHub Student Developer Pack üzerinden $200 kredi (1 yıl) mevcut.
