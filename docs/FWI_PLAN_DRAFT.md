# FWI Orman Yangini Erken Uyari Sistemi

## Bu Proje Nedir?

Bu proje, meteorolojik verileri kullanarak orman yangini tehlike seviyesini onceden hesaplayan
web tabanli bir erken uyari sistemidir. Meteoroloji Muhendisligi bolumu tasarim projesi olarak
gelistirilmistir.

Sistem, kullanicidan aldigi hava durumu bilgilerini (sicaklik, nem, ruzgar, yagis) matematiksel
formullere sokarak o gun icin yangin tehlike seviyesini belirler. Sonuc olarak "Dusuk", "Orta",
"Yuksek", "Cok Yuksek" veya "Asiri" seklinde bir tehlike sinifi uretir.


## Neden Bu Projeyi Yapiyoruz?

Turkiye, ozellikle Akdeniz ve Ege kusaginda her yil ciddi orman yanginlari yasayan bir ulkedir.
2021 yazinda Manavgat ve Marmaris'te yasanan felaketler, erken uyari sistemlerinin ne kadar
kritik oldugunu bir kez daha gostermistir.

Mevcut durumda Turkiye'de kamuya acik, meteorolojik veriye dayali, otomatik calisan bir FWI
hesaplama araci bulunmamaktadir. Bu proje, bu boslugu doldurmak amaciyla uluslararasi kabul
gormmus bilimsel bir yontemi (Van Wagner FWI) Turkiye kosullarina uyarlayarak herkesin
erisebilecegi bir web uygulamasi haline getirmeyi hedefler.


## Hedeflerimiz

1. Van Wagner (1987) FWI formullerini bilimsel olarak dogru bicimde uygulamak
2. Turkiye'nin Akdeniz iklim kusagina uygun tehlike esiklerini (EFFIS) kullanmak
3. Gercek hava verisiyle otomatik calisan, kullanici dostu bir web arayuzu sunmak
4. Hesaplamalarin dogrulugunu referans testler ve gercek yangin olaylariyla kanitlamak
5. Sistemi herkesin erisebilecegi sekilde canli olarak yayimlamak


## Hangi Yontemi Kullaniyor?

Sistem, Kanada Orman Servisi'nin 1987 yilinda yayimladigi FWI (Fire Weather Index) yontemini
kullanir. Bu yontemi C.E. Van Wagner gelistirmistir ve bugun dunyada en yaygin kullanilan
orman yangini tehlike degerlendirme sistemidir.

FWI sistemi tek bir sayi degil, birbirine bagli 6 alt bilesenden olusur:

**Nem Kodlari (onceki gunlerin etkisini tasir):**
- FFMC — Ince Ust Tabaka Yanici Madde Nem Kodu (IYMNK): Olu ortunun ust tabakasindaki kucuk dallar,
  yapraklar gibi ince yanici maddelerin ne kadar kuru oldugunu gosterir. Birka saat icinde kurur veya nemlenir.
- DMC — Humus Nem Kodu: Orta derinlikteki hafif sikistirilmis organik (humus) tabakanin
  nem durumunu gosterir. Kurumasi veya nemlenmesi birka gun surer.
- DC — Derin Organik Tabaka Nem Kodu (DONK): Derin sikistirilmis organik tabakanin
  nem durumunu olcer. Mevsimsel kurakligin etkisini gosterir. Haftalarca surecek bir gosterge.

**Davranis Indisleri (o anki kosullari yansitir):**
- ISI — Ilk Yayilma Indeksi: Ruzgar hizi ve FFMC'den hesaplanir. Bir yangin baslarsa
  ne kadar hizli yayilacagini tahmin eder.
- BUI — Birikmis Yanici Madde Indeksi: DMC ve DC'den hesaplanir. Yanacak malzeme miktarini,
  yani yanginin ne kadar siddetli olacagini gosterir.
- FWI — Yangin Hava Indeksi: ISI ve BUI'yi birlestiren nihai skor. Genel yangin
  tehlike seviyesini tek bir sayiyla ifade eder.

Hesaplama sirasi soyledir:
Hava verileri → FFMC, DMC, DC → ISI, BUI → FWI


## Turkiye Icin Ne Yapildi?

FWI formullerinin kendisi evrenseldir ve degistirilmez. Ancak iki noktada bolgesel uyarlama
yapilmistir:

1. **Gun uzunlugu faktorleri:** DMC ve DC hesaplarinda kullanilan Le ve Lf degerleri enleme
   gore degisir. Sistem, kullanicinin girdigi koordinata gore Turkiye'nin enlem bandina
   (36-42 derece Kuzey) uygun tabloyu otomatik secer.

2. **Tehlike sinifi esikleri:** Kanada'nin standart esikleri yerine, Avrupa Orman Yangini
   Bilgi Sistemi'nin (EFFIS) Akdeniz iklimi icin belirledigiesikler kullanilmaktadir.
   Turkiye'nin Akdeniz iklim kusaginda olmasi nedeniyle bu esikler daha gercekci sonuclar
   uretir.


## Sistem Nasil Calisiyor?

Kullanicinin iki secenegi vardir:

**Manuel Giris:** Kullanici sicaklik, nem, ruzgar hizi, yagis ve ay bilgisini elle girer.
Sistem aninda FWI hesaplar ve tehlike sinifini gosterir.

**Otomatik Hesaplama:** Kullanici enlem, boylam ve tarih araligi girer. Sistem, Open-Meteo
API uzerinden o konumun gercek hava verilerini otomatik olarak ceker ve her gun icin
ayri ayri FWI hesaplar. Sonuclar tablo halinde gosterilir ve PDF olarak indirilebilir.

Hava verileri ogle saati (12:00 yerel saat) degerleri olarak alinir. Bunun sebebi,
Van Wagner'in FWI formullerini ogle gozlemleri uzerine tasarlamis olmasidir.


## Dogrulama Nasil Yapildi?

Sistemin dogru hesap yaptigini kanitlamak icin iki yontem kullanilmistir:

1. **Van Wagner Referans Testi:** Van Wagner'in raporundaki bilinen girdi degerlerıyle
   (T=17C, H=%42, W=25 km/h, r=0 mm) hesaplama yapilir. Sonuclar beklenen ciktilarla
   karsilastirilir. Tum ara adimlar (mo, ed, ew, K, Lf vb.) ayri ayri gosterilir.

2. **Gercek Yangin Olaylari:** Turkiye'de yasanmis buyuk orman yanginlarinin
   (2021 Manavgat, 2021 Marmaris, 2019 Izmir) tarih ve koordinatlari girilir. O gunun
   gercek hava verileriyle FWI hesaplanir. Beklenti, bu olaylarin yuksek tehlike
   sinifina dusmesidir — ki oyle cikmistir.


## Hangi Kaynaklar Kullaniliyor?

| Kaynak | Ne Icin | Guvenilirlik |
|---|---|---|
| Van Wagner (1987) — Forestry Technical Report 35 | Tum FWI formulleri | Kanada Orman Servisi resmi yayini, 37 yildir dunya standardi |
| cffdrs R paketi (bcgov/cffdrs) | Formul ve katsayi dogrulama | Kanada hukumetinin acik kaynakli referans uygulamasi |
| EFFIS (Avrupa Komisyonu) | Akdeniz tehlike sinifi esikleri | AB resmi orman yangini bilgi sistemi |
| Open-Meteo / ERA5 (ECMWF) | Gercek zamanli hava verisi | Dunya genelinde en cok kullanilan atmosfer yeniden analiz verisi |


## Teknik Altyapi

| Bilesen | Teknoloji |
|---|---|
| Hesaplama motoru | Python |
| Web sunucu | Flask |
| Hava verisi API | Open-Meteo (ERA5 tabanli) |
| PDF rapor | ReportLab |
| Canli yayin | Railway (su an) → DigitalOcean (gelecek) |
| Versiyon kontrolu | Git + GitHub |
| Arayuz | HTML/CSS/JavaScript (tek sayfa uygulama) |
| Harita gorsellestirme (gelecek) | CARTO / Leaflet.js |


## Projenin Dosya Yapisi

```
Claude/
├── fwi_hesap.py      — FWI hesaplama motoru (tum formuller)
├── app.py             — Flask web sunucusu ve API endpointleri
├── openmeteo.py       — Open-Meteo API ile veri cekme
├── templates/
│   └── index.html     — Web arayuzu (tek sayfa, tum sekmeler dahil)
├── test_fwi.py        — Birim testleri
└── generate_pdf.py    — Kaynak guvenilirligi PDF olusturucu
```


## Mevcut Eksiklikler ve Tamamlanmasi Gereken Isler

1. **EFFIS Esik Uyarlamasi:** Tehlike sinifi esikleri halen Kanada standartlarini kullaniyor.
   EFFIS Akdeniz esiklerine (5.2 / 11.2 / 21.3 / 38.0) guncellenmeli. Web arayuzundeki
   esik bilgileri de buna paralel duzeltilmeli.

2. **Mobil Uyumluluk Iyilestirmeleri:** Bazi butonlarin ve sekme basliklarin dokunma alanlari
   mobil cihazlarda kucuk kaliyor (minimum 44px olmali). Kucuk ekranlarda bazi kartlarin
   ic boslugu azaltilmali.

3. **Daha Fazla Validasyon Olaylari:** Su an 3 yangin olayiyla dogrulama yapiliyor
   (Manavgat, Marmaris, Izmir). En az 8-10 olaya cikarilmasi sistemin guvenilirligini
   daha guclu kanitlar.


## Gelecek Planlamasi — Eklenebilecek Ozellikler

### Kisa Vadeli (Dusuk Efor)
- **PDF Rapor Indirme:** Kullanici hesaplama yaptiktan sonra sonuclari PDF olarak
  indirebilmeli. Altyapi (ReportLab) zaten mevcut, sadece kullanici arayuzune buton
  ve endpoint eklenmesi gerekiyor.
- **Daha Fazla Yangin Olaylari:** Validasyon sayfasina 2022-2024 arasi Turkiye yanginlari
  eklenerek dogrulama veri seti genisletilebilir.

### Orta Vadeli (Orta Efor)
- **7 Gunluk FWI Tahmin Grafigi:** Open-Meteo'nun forecast API'si kullanilarak onumuzdeki
  7 gunun tahmini FWI degerleri hesaplanip Chart.js ile gorsellestirilir. Sistemi
  "hesaplayici"dan gercek bir "erken uyari sistemi"ne donusturur.
- **Interaktif Harita:** Leaflet.js ile Turkiye haritasi eklenir. Kullanici haritaya
  tiklayarak konum secer, koordinatlari elle yazmak zorunda kalmaz.
- **Tarihsel Trend Analizi:** Secilen konum icin gecmis 1 yilin FWI degerlerini grafik
  olarak gostermek. Mevsimsel oruntuleri ve en riskli donemleri gorsellestirmek.

### Altyapi Gecisi
- **DigitalOcean'a Tasima:** Proje buyudukce Railway'den DigitalOcean'a gecis yapilacak.
  GitHub Student Developer Pack uzerinden $200 kredi (1 yil) mevcut. Kendi sunucu,
  veritabani, cron job ve daha fazla kontrol imkani saglar.

### Uzun Vadeli (Yuksek Efor)
- **Turkiye Tehlike Haritasi:** Birden fazla konum icin toplu FWI hesaplayip harita
  uzerinde renk kodlu (heatmap) gostermek. Hangi bolgenin o gun en riskli oldugunu
  tek bakista gormek mumkun olur.
- **Otomatik Bildirim Sistemi:** Kullanicinin bir konumu kaydetmesi ve FWI belirli
  esigi astiginda e-posta ile uyarilmasi. Gercek bir operasyonel uyari sistemi
  ozelligi kazandirir.
- **Uydu Verisi Entegrasyonu:** MODIS veya VIIRS uydu verileriyle gercek yangin
  noktalarini harita uzerinde gostermek ve FWI tahminleriyle karsilastirmak.
