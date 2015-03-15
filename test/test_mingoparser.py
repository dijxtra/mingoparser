# -*- coding: utf-8 -*-
import unittest
from mingoparser import *


class SQLTest(unittest.TestCase):
    """Testiranje upisa u bazu i čitanja iz baze."""

    def setUp(self):
        self.database_file = 'db.test.sqlite3'

        init_sql(self.database_file)

        pisi_sve_u_sql(self.database_file)

        self.vlasnici = gen_vlasnici_full()

        saver = Saver()
        self.vlasnici_sql = saver.citaj_vlasnike_sql(self.database_file)
        self.vlasnici_sql = saver.citaj_indekse_sql(self.vlasnici_sql, self.database_file)
        self.vlasnici_sql = saver.citaj_cijene_s_postajama_sql(self.vlasnici_sql, self.database_file)

    def test_cijene_sa_brojem_postaja(self):
        vlasnik_sql = self.vlasnici_sql[5]
        vlasnik = self.vlasnici[vlasnik_sql.id()]

        vrsta_goriva = 1
        self.assertEqual(vlasnik_sql.cijene_sa_brojem_postaja(vrsta_goriva), vlasnik.cijene_sa_brojem_postaja(vrsta_goriva))

    def test_broj_postaja(self):
        vlasnik_sql = self.vlasnici_sql[5]
        vlasnik = self.vlasnici[vlasnik_sql.id()]

        vrsta_goriva = 1
        self.assertEqual(vlasnik_sql.broj_postaja(vrsta_goriva), vlasnik.broj_postaja(vrsta_goriva))

    def test_main(self):
        for vlasnik in self.vlasnici.values():
            self.assertTrue(vlasnik.id() in self.vlasnici_sql)

        for vlasnik_sql in self.vlasnici_sql.values():
            self.assertTrue(vlasnik_sql.id() in self.vlasnici)

        for vlasnik_sql in self.vlasnici_sql.values():
            vlasnik = self.vlasnici[vlasnik_sql.id()]
            
            self.assertEqual(vlasnik_sql.ime(), vlasnik.ime())
            self.assertEqual(vlasnik_sql.vrste_goriva().sort(), vlasnik.vrste_goriva().sort())
            self.assertEqual(vlasnik_sql.broj_postaja(), vlasnik.broj_postaja())
            for vrsta_goriva in vlasnik.vrste_goriva():
                self.assertEqual(vlasnik_sql.indeks(vrsta_goriva), vlasnik.indeks(vrsta_goriva))
                self.assertEqual(vlasnik_sql.broj_postaja(vrsta_goriva), vlasnik.broj_postaja(vrsta_goriva))
                self.assertEqual(vlasnik_sql.cijene_sa_brojem_postaja(vrsta_goriva), vlasnik.cijene_sa_brojem_postaja(vrsta_goriva))

    def test_visestruko_pisanje(self):
        pisi_sve_u_sql(self.database_file)
        pisi_sve_u_sql(self.database_file)
        pisi_sve_u_sql(self.database_file)

        saver = Saver()
        self.vlasnici_sql = saver.citaj_vlasnike_sql(self.database_file)
        self.vlasnici_sql = saver.citaj_indekse_sql(self.vlasnici_sql, self.database_file)
        self.vlasnici_sql = saver.citaj_cijene_s_postajama_sql(self.vlasnici_sql, self.database_file)

        self.test_main()

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

        
if __name__ == '__main__':
    unittest.main()
