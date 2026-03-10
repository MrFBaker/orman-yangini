# -*- coding: utf-8 -*-
"""
FWI Dogrulama Testi
Referans: Van Wagner (1987) + cffdrs R paketi ornekleri
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import fwi_hesap as f

# --- TEST 1: Ardisik 5 gunluk hesaplama ---
# Baslangic: ffmc0=85, dmc0=6, dc0=15 (Van Wagner 1987 standart)
print("=" * 90)
print("TEST 1 - Ardisik 5 Gunluk Hesaplama (Temmuz, Baslangic: FFMC=85 DMC=6 DC=15)")
print("=" * 90)

test_data = [
    # (gun, temp, rh, wind, precip)
    (1, 17.0, 42.0, 25.0, 0.0),
    (2, 20.0, 35.0, 20.0, 0.0),
    (3, 25.0, 25.0, 30.0, 0.0),
    (4, 18.0, 55.0, 10.0, 5.0),
    (5, 22.0, 40.0, 15.0, 0.0),
]

header = "{:>3}  {:>5} {:>5} {:>5} {:>5} | {:>6} {:>6} {:>6} {:>6} {:>6} {:>6}  {}"
row    = "{:>3}  {:>5.1f} {:>5.1f} {:>5.1f} {:>5.1f} | {:>6.2f} {:>6.2f} {:>6.2f} {:>6.2f} {:>6.2f} {:>6.2f}  {}"
print(header.format("Gun", "Temp", "RH", "Wind", "Prec", "FFMC", "DMC", "DC", "ISI", "BUI", "FWI", "Sinif"))
print("-" * 90)

ffmc0, dmc0, dc0 = 85.0, 6.0, 15.0
for gun, temp, rh, wind, precip in test_data:
    r = f.hesapla(temp, rh, wind, precip, 7, ffmc0, dmc0, dc0)
    print(row.format(gun, temp, rh, wind, precip,
                     r["ffmc"], r["dmc"], r["dc"],
                     r["isi"], r["bui"], r["fwi"], r["sinif"]))
    ffmc0, dmc0, dc0 = r["ffmc"], r["dmc"], r["dc"]

# --- TEST 2: Van Wagner (1987) Tablo 1 Referans Degerleri ---
# Gün 1 icin bilinen referans deger: ffmc0=85 -> FFMC=87.69
print()
print("=" * 60)
print("TEST 2 - Referans Deger Karsilastirmasi (Gun 1)")
print("=" * 60)

# Beklenen degerler (Van Wagner 1987 / cffdrs R paketi)
beklenen = {
    "ffmc": 87.69,
    "dmc":  8.47,
    "dc":   21.76,
    "isi":  10.85,
    "bui":  8.58,
    "fwi":  10.14,
}

r1 = f.hesapla(17.0, 42.0, 25.0, 0.0, 7, 85.0, 6.0, 15.0)

print("{:>6}  {:>10}  {:>10}  {:>8}".format("Indeks", "Hesaplanan", "Beklenen", "Fark %"))
print("-" * 42)
tum_gecti = True
for indeks, bek in beklenen.items():
    hes = r1[indeks]
    fark = abs(hes - bek) / bek * 100 if bek != 0 else 0
    durum = "OK" if fark < 1.0 else "!! HATA !!"
    if fark >= 1.0:
        tum_gecti = False
    print("{:>6}  {:>10.4f}  {:>10.4f}  {:>7.4f}%  {}".format(indeks.upper(), hes, bek, fark, durum))

print()
if tum_gecti:
    print(">> TUM TESTLER GECTI - Modül dogrulanmistir.")
else:
    print(">> BAZI TESTLER BASARISIZ - Formülleri kontrol et.")

# --- TEST 3: Sinir degerleri ---
print()
print("=" * 60)
print("TEST 3 - Sinir Deger Testleri")
print("=" * 60)

# Dusuk sicaklik
r_soguk = f.hesapla(-5.0, 90.0, 5.0, 0.0, 4, 85.0, 6.0, 15.0)
print("Soguk hava (-5C, %90 nem): FWI={}, FFMC={}".format(r_soguk["fwi"], r_soguk["fwi"]))
assert r_soguk["ffmc"] >= 0, "FFMC negatif olmamali"
assert r_soguk["dmc"]  >= 0, "DMC negatif olmamali"
assert r_soguk["dc"]   >= 0, "DC negatif olmamali"

# Cok sicak ve kuru
r_sicak = f.hesapla(40.0, 10.0, 60.0, 0.0, 7, 90.0, 50.0, 300.0)
print("Sicak kuru hava (40C, %10 nem): FWI={} -> {}".format(r_sicak["fwi"], r_sicak["sinif"]))
assert r_sicak["sinif"] == "Asiri", "Yuksek kuru kosullarda Asiri bekleniyor, alindi: " + r_sicak["sinif"]

# Yogun yagis
r_yagmur = f.hesapla(15.0, 80.0, 10.0, 30.0, 6, 85.0, 20.0, 100.0)
print("Yogun yagis (30mm): FFMC={}, DMC={}, DC={}".format(
    r_yagmur["ffmc"], r_yagmur["dmc"], r_yagmur["dc"]))

print()
print(">> SINIR DEGER TESTLERI TAMAMLANDI")
