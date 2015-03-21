# -*- coding: utf-8 -*-
import unittest
from mingoparser import *


class CetiriSetaPodataka(unittest.TestCase):
    """Testiranje aplikacije sa dva različita seta podataka odjednom."""

    @classmethod
    def setUpClass(self):
        self.baza = DatabaseConnection('db.test.sqlite3')
        self.baza.kreiraj_tablice()

        citac = CitacVrijednostiOffline('inputs2/')
        self.baza.pisi_nove_vrijednosti(citac, '2015-03-10 10:03:13')

        citac = CitacVrijednostiOffline('inputs/')
        self.baza.pisi_nove_vrijednosti(citac, '2015-03-12 7:03:43')

        citac = CitacVrijednostiOffline('inputs2/')
        self.baza.pisi_nove_vrijednosti(citac, '2015-03-14 08:26:34')

        citac = CitacVrijednostiOffline('inputs2/')
        self.baza.pisi_nove_vrijednosti(citac, '2015-03-17 17:53:41')

    def setUp(self):
        self.baza = DatabaseConnection('db.test.sqlite3')
        self.vlasnici = self.baza.citaj_vrijednosti()


    def test_vrijeme_zadnjeg_upisa(self):
        self.assertEqual(self.baza.vrijeme_zadnjeg_upisa(), u'2015-03-17 17:53:41')
        
        self.assertEqual(self.baza.vrijeme_zadnjeg_upisa(vrsta_goriva = 2), u'2015-03-17 17:53:41')
        self.assertEqual(self.baza.vrijeme_zadnjeg_upisa(vrsta_goriva = 3), u'2015-03-17 17:53:41')
        
    def test_jedan_indeks(self):
        vrsta_goriva = 2
        limit = 4
        
        vlasnik = self.vlasnici[88]

        self.assertEqual(vlasnik.ime(), 'Konzum d.d.')
        self.assertEqual(vlasnik.cijene_sa_brojem_postaja(vrsta_goriva), {9.59: 4, 9.22: 4})
        self.assertEqual(vlasnik.broj_postaja(vrsta_goriva), 8)
        self.assertEqual(round(vlasnik.indeks(vrsta_goriva), 2), 9.59)
        self.assertEqual(vlasnik.vrijeme_zadnjeg_upisa(vrsta_goriva), u'2015-03-17 17:53:41')
        self.assertEqual(vlasnik.vrijeme_zadnje_promjene_cijene(vrsta_goriva), u'2015-03-14 08:26:34')

    def test_promijene_vrijednosti(self):
        vrsta_goriva = 2
        ina = self.vlasnici[6]

        ocekivane_vrijednosti = [
            [9.6683, u'2015-03-14 08:26:34', u'2015-03-17 17:53:41'],
            [9.3155, u'2015-03-12 7:03:43', u'2015-03-12 7:03:43'],
            [9.6683, u'2015-03-10 10:03:13', u'2015-03-10 10:03:13'],
        ]

        i = 0
        for (indeks, start, end) in ina.promjene_vrijednosti(vrsta_goriva):
            self.assertEqual([round(indeks, 4), start, end], ocekivane_vrijednosti[i])
            i += 1
        self.assertEqual(i, 3)

    def test_promijene_vrijednosti_jedna(self):
        vrsta_goriva = 8
        ina = self.vlasnici[153]

        ocekivane_vrijednosti = [8.99, u'2015-03-10 10:03:13', u'2015-03-17 17:53:41']

        dobivena_vrijednost = ina.promjene_vrijednosti(vrsta_goriva)
        self.assertTrue(dobivena_vrijednost)
        print dobivena_vrijednost
        self.assertEqual(len(dobivena_vrijednost), 1)
        self.assertEqual(len(dobivena_vrijednost[0]), 3)
        (indeks, start, end) = dobivena_vrijednost[0]
        self.assertEqual([round(indeks, 4), start, end], ocekivane_vrijednosti)

if __name__ == '__main__':
    unittest.main()
