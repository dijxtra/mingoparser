# -*- coding: utf-8 -*-
import unittest
from mingoparser import *


class DvaSetaPodataka(unittest.TestCase):
    """Testiranje aplikacije sa dva različita seta podataka odjednom."""

    def setUp(self):
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

if __name__ == '__main__':
    unittest.main()
