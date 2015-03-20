# -*- coding: utf-8 -*-
import unittest, datetime
from mingoparser import *


class SQLTest(unittest.TestCase):
    """Testiranje upisa u bazu i čitanja iz baze."""

    def setUp(self):
        self.baza = DatabaseConnection('db.test.sqlite3')
        self.baza.kreiraj_tablice()

        citac = CitacVrijednostiOffline('inputs/')
        self.vlasnici_citani = citac.gen_vlasnici_full()
        self.baza.popuni_osnovne_tablice(self.vlasnici_citani, '2015-02-23 11:23:45')
        self.baza.popuni_tablice(self.vlasnici_citani, '2015-02-23 11:23:45')
        
        self.vlasnici = self.baza.citaj_vlasnike()
        self.vlasnici = self.baza.citaj_indekse(self.vlasnici)
        self.vlasnici = self.baza.citaj_cijene_s_postajama(self.vlasnici)

    def test_cijene_sa_brojem_postaja(self):
        vlasnik_sql = self.vlasnici[5]
        vlasnik = self.vlasnici_citani[vlasnik_sql.id()]

        vrsta_goriva = 1
        self.assertEqual(vlasnik_sql.cijene_sa_brojem_postaja(vrsta_goriva), vlasnik.cijene_sa_brojem_postaja(vrsta_goriva))

    def test_broj_postaja(self):
        vlasnik_sql = self.vlasnici[5]
        vlasnik = self.vlasnici_citani[vlasnik_sql.id()]

        vrsta_goriva = 1
        self.assertEqual(vlasnik_sql.broj_postaja(vrsta_goriva), vlasnik.broj_postaja(vrsta_goriva))

    def test_prolaz_kroz_bazu(self):
        for vlasnik in self.vlasnici_citani.values():
            self.assertTrue(vlasnik.id() in self.vlasnici)

        for vlasnik_sql in self.vlasnici.values():
            self.assertTrue(vlasnik_sql.id() in self.vlasnici_citani)

        for vlasnik_sql in self.vlasnici.values():
            vlasnik = self.vlasnici_citani[vlasnik_sql.id()]
            
            self.assertEqual(vlasnik_sql.ime(), vlasnik.ime())
            self.assertEqual(vlasnik_sql.vrste_goriva().sort(), vlasnik.vrste_goriva().sort())
            self.assertEqual(vlasnik_sql.broj_postaja(), vlasnik.broj_postaja())
            for vrsta_goriva in vlasnik.vrste_goriva():
                self.assertEqual(vlasnik_sql.indeks(vrsta_goriva), vlasnik.indeks(vrsta_goriva))
                self.assertEqual(vlasnik_sql.broj_postaja(vrsta_goriva), vlasnik.broj_postaja(vrsta_goriva))
                self.assertEqual(vlasnik_sql.cijene_sa_brojem_postaja(vrsta_goriva), vlasnik.cijene_sa_brojem_postaja(vrsta_goriva))

    def test_visestruko_pisanje(self):
        self.baza.popuni_tablice(self.vlasnici_citani)
        self.baza.popuni_tablice(self.vlasnici_citani)
        self.baza.popuni_tablice(self.vlasnici_citani)

        self.vlasnici = self.baza.citaj_vlasnike()
        self.vlasnici = self.baza.citaj_indekse(self.vlasnici)
        self.vlasnici = self.baza.citaj_cijene_s_postajama(self.vlasnici)

        self.test_prolaz_kroz_bazu()

    def test_indeks_hrvatska(self):
        hrvatska = gen_hrvatska(self.vlasnici)

        self.assertEqual(hrvatska.ime(), "Hrvatska")
        self.assertEqual(round(hrvatska.indeks(2), 4), 9.3168)
        self.assertEqual(hrvatska.vrste_goriva(), [1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 20, 21, 22])
        self.assertEqual(map(lambda vrsta_goriva: round(hrvatska.indeks(vrsta_goriva), 4), hrvatska.vrste_goriva()), [9.4168, 9.3168, 9.6834, 9.7245, 9.9976, 8.9477, 8.8289, 4.3897, 5.2816, 5.1545, 66.7847, 94.6962, 3.3156])

    def test_indeksi(self):
        vrsta_goriva = 2
        limit = 4
        
        sortirani_vlasnici = sorted(self.vlasnici.values(), key=lambda v: v.indeks(vrsta_goriva))

        ocekivani_rezultati = [
            ["Konzum d.d.", {9.22: 4}, 4, 9.22],
            ["Crodux Derivati Dva d.o.o.", {9.38: 9, 9.28: 53, 9.23: 2}, 64, 9.29],
            ["Interpetrol d.o.o.", {9.32: 2, 9.27: 2}, 4, 9.29],
            ["KTC d.d.", {9.32: 4, 9.27: 1}, 5, 9.31],
            ["LUKOIL Croatia d.o.o.", {9.31: 48}, 48, 9.31],
            ["Tifon d.o.o.", {9.32: 28, 9.27: 4, 9.3: 4}, 36, 9.31],
            ["Adria Oil d.o.o.", {9.32: 10, 9.27: 1}, 11, 9.32],
            ["INA – Industrija nafte d.d.", {9.32: 265, 9.27: 21, 8.23: 1, 9.42: 8}, 295, 9.32],
            ["Apios d.o.o.", {9.32: 5}, 5, 9.32],
            ["INA - Osijek Petrol d.d.", {9.32: 10}, 10, 9.32],
            ["Energoinvest-Hrvatska d.o.o.", {9.5: 2, 9.4: 9}, 11, 9.42],
            ["Crno Zlato d o o", {9.6: 4}, 4, 9.60]
            ]

        i = 0
        for vlasnik in sortirani_vlasnici:
            if vlasnik.nudi_gorivo(vrsta_goriva):
                if vlasnik.broj_postaja(vrsta_goriva) >= limit:
                    self.assertEqual([vlasnik.ime(), vlasnik.cijene_sa_brojem_postaja(vrsta_goriva), vlasnik.broj_postaja(vrsta_goriva), round(vlasnik.indeks(vrsta_goriva), 2)], ocekivani_rezultati[i])
                    i += 1

    def test_cijene(self):
        vrsta_goriva = 2
        limit = 4
        
        cijene_sa_vlasnicima = gen_cijene_sa_vlasnicima(self.vlasnici)

        ocekivani_rezultati = [
            [9.28, [('Crodux Derivati Dva d.o.o.', 53)]],
            [9.32, [('Adria Oil d.o.o.', 10), ('Apios d.o.o.', 5), ('INA - Osijek Petrol d.d.', 10), ('INA \xe2\x80\x93 Industrija nafte d.d.', 265), ('KTC d.d.', 4), ('Tifon d.o.o.', 28)]],
            [9.4, [('Energoinvest-Hrvatska d.o.o.', 9)]],
            [9.27, [('INA \xe2\x80\x93 Industrija nafte d.d.', 21), ('Tifon d.o.o.', 4)]],
            [9.31, [('LUKOIL Croatia d.o.o.', 48)]],
            [9.6, [('Crno Zlato d o o', 4)]],
            [9.22, [('Konzum d.d.', 4)]],
            [9.3, [('Tifon d.o.o.', 4)]],
            [9.38, [('Crodux Derivati Dva d.o.o.', 9)]],
            [9.42, [('INA \xe2\x80\x93 Industrija nafte d.d.', 8)]]
            ]

        i = 0
        for (cijena, lista_vlasnika) in cijene_sa_vlasnicima[vrsta_goriva].iteritems():
            if filter(lambda (vlasnik, broj_postaja): broj_postaja >= limit, lista_vlasnika.iteritems()):
                vlasnik_brojpostaja = map(lambda (vlasnik, broj_postaja): (vlasnik.ime(), broj_postaja), lista_vlasnika.iteritems())
                vlasnik_brojpostaja_filtrirano = filter(lambda (ime, broj_postaja): broj_postaja >= limit, vlasnik_brojpostaja)
                vlasnik_brojpostaja_sortirano = sorted(vlasnik_brojpostaja_filtrirano, key = lambda x: x[0])
                self.assertEqual([cijena, vlasnik_brojpostaja_sortirano], ocekivani_rezultati[i])
                i += 1

    def test_vrijeme_zadnjeg_upisa(self):
        self.assertEqual(self.baza.vrijeme_zadnjeg_upisa(), u'2015-02-23 11:23:45')
        
        self.assertEqual(self.baza.vrijeme_zadnjeg_upisa(vrsta_goriva = 2), u'2015-02-23 11:23:45')
        self.assertEqual(self.baza.vrijeme_zadnjeg_upisa(vrsta_goriva = 3), u'2015-02-23 11:23:45')
        
if __name__ == '__main__':
    unittest.main()
