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
                
if __name__ == '__main__':
    unittest.main()


