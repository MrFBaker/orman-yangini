# -*- coding: utf-8 -*-
"""
Ek Yangın İndeksleri Birim Testleri

Her indeks için el hesabıyla doğrulanmış test vakaları.
"""
import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
import indeksler as idx


class TestAngstrom(unittest.TestCase):
    """Angström (1942) — I = RH/20 + (27-T)/10"""

    def test_sicak_kuru(self):
        # T=25, RH=30 → 30/20 + (27-25)/10 = 1.5 + 0.2 = 1.7
        self.assertAlmostEqual(idx.angstrom(25, 30), 1.7, places=1)

    def test_soguk_nemli(self):
        # T=5, RH=90 → 90/20 + (27-5)/10 = 4.5 + 2.2 = 6.7
        self.assertAlmostEqual(idx.angstrom(5, 90), 6.7, places=1)

    def test_sinif_asiri(self):
        self.assertEqual(idx.angstrom_sinif(1.5), "Asiri")

    def test_sinif_yuksek(self):
        self.assertEqual(idx.angstrom_sinif(2.3), "Yuksek")

    def test_sinif_orta(self):
        self.assertEqual(idx.angstrom_sinif(3.0), "Orta")

    def test_sinif_dusuk(self):
        self.assertEqual(idx.angstrom_sinif(5.0), "Dusuk")

    def test_ters_skala(self):
        # Düşük değer = yüksek tehlike
        sicak = idx.angstrom(35, 20)
        soguk = idx.angstrom(5, 80)
        self.assertLess(sicak, soguk)


class TestNesterov(unittest.TestCase):
    """Nesterov (1949) — G = G_prev + T × (T - Td)"""

    def test_temel(self):
        # T=25, Td=10, P=0, G0=0 → d=25*(25-10)=375, G=375
        self.assertAlmostEqual(idx.nesterov(25, 10, 0, 0), 375, places=0)

    def test_kumulatif(self):
        # G0=500, T=20, Td=5, P=0 → d=20*15=300, G=800
        self.assertAlmostEqual(idx.nesterov(20, 5, 0, 500), 800, places=0)

    def test_yagis_reset(self):
        # Yağış >= 3mm → reset
        self.assertEqual(idx.nesterov(25, 10, 5, 1000), 0.0)

    def test_yagis_esik_alti(self):
        # Yağış < 3mm → devam
        result = idx.nesterov(25, 10, 2, 500)
        self.assertGreater(result, 500)

    def test_negatif_deficit(self):
        # Td > T (nadiren olur) → deficit 0 olarak alınmalı
        result = idx.nesterov(10, 15, 0, 100)
        self.assertEqual(result, 100)  # d=0, G=G0

    def test_sinif_tehlike_yok(self):
        self.assertEqual(idx.nesterov_sinif(100), "Tehlike Yok")

    def test_sinif_dusuk(self):
        self.assertEqual(idx.nesterov_sinif(500), "Dusuk")

    def test_sinif_orta(self):
        self.assertEqual(idx.nesterov_sinif(2000), "Orta")

    def test_sinif_yuksek(self):
        self.assertEqual(idx.nesterov_sinif(5000), "Yuksek")

    def test_sinif_asiri(self):
        self.assertEqual(idx.nesterov_sinif(15000), "Asiri")


class TestKBDI(unittest.TestCase):
    """Keetch & Byram (1968) — KBDI 0-800"""

    def test_soguk_gun(self):
        # T_max < 10°C → DF=0, KBDI değişmez
        self.assertEqual(idx.kbdi(5, 0, 200, 600), 200.0)

    def test_yagis_etkisi(self):
        # P=20mm, net_rain=20-5.08=14.92, KBDI=300-14.92=285.08 + DF
        result = idx.kbdi(25, 20, 300, 600)
        self.assertLess(result, 300)  # Yağış düşürmeli

    def test_kuru_sicak(self):
        # Sıcak gün, yağış yok → KBDI artmalı
        result = idx.kbdi(35, 0, 200, 600)
        self.assertGreater(result, 200)

    def test_sinir_0(self):
        # KBDI 0'ın altına düşmemeli
        result = idx.kbdi(5, 50, 10, 600)
        self.assertGreaterEqual(result, 0)

    def test_sinir_800(self):
        # KBDI 800'ü geçmemeli
        result = idx.kbdi(45, 0, 790, 200)
        self.assertLessEqual(result, 800)

    def test_sinif_dusuk(self):
        self.assertEqual(idx.kbdi_sinif(100), "Dusuk")

    def test_sinif_orta(self):
        self.assertEqual(idx.kbdi_sinif(300), "Orta")

    def test_sinif_yuksek(self):
        self.assertEqual(idx.kbdi_sinif(500), "Yuksek")

    def test_sinif_asiri(self):
        self.assertEqual(idx.kbdi_sinif(700), "Asiri")


class TestCarrega(unittest.TestCase):
    """Carrega (1991) — I87 = -4.51 + 0.236T + 0.095δ - 0.038RH"""

    def test_temel(self):
        # T=30, Td=15, RH=25 → -4.51 + 0.236*30 + 0.095*15 - 0.038*25
        # = -4.51 + 7.08 + 1.425 - 0.95 = 3.045
        self.assertAlmostEqual(idx.carrega(30, 15, 25), 3.04, places=1)

    def test_sicak_kuru(self):
        # Çok sıcak, çok kuru → yüksek I87
        result = idx.carrega(40, 10, 15)
        self.assertGreater(result, 5)

    def test_soguk_nemli(self):
        # Soğuk, nemli → düşük/negatif I87
        result = idx.carrega(5, 3, 90)
        self.assertLess(result, 0)

    def test_sinif_dusuk(self):
        self.assertEqual(idx.carrega_sinif(3), "Dusuk")

    def test_sinif_orta(self):
        self.assertEqual(idx.carrega_sinif(7), "Orta")

    def test_sinif_yuksek(self):
        self.assertEqual(idx.carrega_sinif(12), "Yuksek")

    def test_sinif_asiri(self):
        self.assertEqual(idx.carrega_sinif(20), "Asiri")


class TestHesaplaEk(unittest.TestCase):
    """Birleşik hesaplama fonksiyonu"""

    def test_tum_anahtarlar(self):
        r = idx.hesapla_ek(25, 30, 15, 0, 30, 10)
        for key in ["angstrom", "angstrom_sinif", "nesterov", "nesterov_sinif",
                     "kbdi", "kbdi_sinif", "carrega", "carrega_sinif"]:
            self.assertIn(key, r)

    def test_angstrom_degeri(self):
        r = idx.hesapla_ek(25, 30, 15, 0, 30, 10)
        self.assertAlmostEqual(r["angstrom"], 1.7, places=1)


if __name__ == "__main__":
    unittest.main()
