# -*- coding: utf-8 -*-
import unittest
from mingoparser import *


class DvaSetaPodataka(unittest.TestCase):
    """Testiranje aplikacije sa dva različita seta podataka odjednom."""

    def setUp(self):
        self.baza = DatabaseConnection('db.test.sqlite3')
        self.baza.kreiraj_tablice()

        citac = CitacVrijednostiOffline('inputs2/')
        self.baza.pisi_nove_vrijednosti(citac, datum = '2015-03-10 10:03:13')

        citac = CitacVrijednostiOffline('inputs/')
        self.baza.pisi_nove_vrijednosti(citac, datum = '2015-03-17 17:53:41')
        
        self.vlasnici = self.baza.citaj_vrijednosti()


    def test_indeks_hrvatska(self):
        hrvatska = gen_hrvatska(self.vlasnici)

        self.assertEqual(hrvatska.ime(), "Hrvatska")
        self.assertEqual(round(hrvatska.indeks(2), 4), 9.3217)
        self.assertEqual(hrvatska.vrste_goriva(), [1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 20, 21, 22])
        self.assertEqual(map(lambda vrsta_goriva: round(hrvatska.indeks(vrsta_goriva), 4), hrvatska.vrste_goriva()), [9.4173, 9.3217, 9.6834, 9.7303, 9.9977, 8.9497, 8.8261, 4.4002, 5.3122, 5.1605, 70.1884, 86.5159, 3.4232])

    def test_indeksi(self):
        vrsta_goriva = 2
        limit = 4
        
        sortirani_vlasnici = sorted(self.vlasnici.values(), key=lambda v: v.indeks(vrsta_goriva))

        ocekivani_rezultati = [
            ['Konzum d.d.', {9.59: 4, 9.22: 4}, 8, 9.22, u'2015-03-17 17:53:41'],
            ['HIDRO VING D.O.O.', {9.27: 2, 9.67: 2}, 4, 9.27, u'2015-03-17 17:53:41'],
            ['Antunovi\xc4\x87 TA d.o.o.', {9.27: 1, 9.67: 1, 9.29: 1, 9.62: 1}, 4, 9.28, u'2015-03-17 17:53:41'],
            ['Mikol d.o.o.', {9.32: 1, 9.27: 2, 9.67: 1, 9.62: 2}, 6, 9.29, u'2015-03-17 17:53:41'],
            ['Crodux Derivati Dva d.o.o.', {9.77: 9, 9.28: 53, 9.62: 1, 9.38: 9, 9.67: 54, 9.23: 2}, 128, 9.29, u'2015-03-17 17:53:41'],
            ['Interpetrol d.o.o.', {9.32: 2, 9.27: 2, 9.65: 1, 9.67: 2, 9.62: 1}, 8, 9.29, u'2015-03-17 17:53:41'],
            ['Cro-Can Center d.o.o.', {9.66: 3, 9.3: 3}, 6, 9.3, u'2015-03-17 17:53:41'],
            ['KTC d.d.', {9.32: 4, 9.27: 1, 9.67: 5, 9.62: 2}, 12, 9.31, u'2015-03-17 17:53:41'],
            ['LUKOIL Croatia d.o.o.', {9.81: 3, 9.66: 45, 9.31: 48}, 96, 9.31, u'2015-03-17 17:53:41'],
            ['B.P. Jozinovi\xc4\x87', {9.66: 2, 9.31: 2}, 4, 9.31, u'2015-03-17 17:53:41'],
            ['Tifon d.o.o.', {9.27: 4, 9.3: 4, 9.32: 28, 9.61: 1, 9.62: 6, 9.67: 29}, 72, 9.31, u'2015-03-17 17:53:41'],
            ['Adria Oil d.o.o.', {9.32: 10, 9.27: 1, 9.66: 6, 9.67: 4, 9.62: 1}, 22, 9.32, u'2015-03-17 17:53:41'],
            ['INA \xe2\x80\x93 Industrija nafte d.d.', {9.27: 21, 9.64: 2, 9.32: 265, 9.59: 1, 9.77: 8, 9.62: 20, 9.57: 1, 9.66: 5, 9.42: 8, 8.23: 1, 9.67: 258}, 590, 9.32, u'2015-03-17 17:53:41'],
            ['Apios d.o.o.', {9.32: 5, 9.66: 5}, 10, 9.32, u'2015-03-17 17:53:41'],
            ['INA - Osijek Petrol d.d.', {9.32: 10, 9.67: 10}, 20, 9.32, u'2015-03-17 17:53:41'],
            ['Tri Bartola d.o.o.', {9.32: 2, 9.67: 2}, 4, 9.32, u'2015-03-17 17:53:41'],
            ['Tuhelj Gorivo d.o.o.', {9.32: 2, 9.67: 2}, 4, 9.32, u'2015-03-17 17:53:41'],
            ['Etradex d.o.o.', {9.32: 2, 9.67: 2}, 4, 9.32, u'2015-03-17 17:53:41'],
            ['Dirus Projekt d.o.o.', {9.5: 2, 9.75: 8, 9.4: 9, 9.85: 2}, 21, 9.42, u'2015-03-17 17:53:41'],
            ['Crno Zlato d o o', {9.6: 4, 9.98: 4}, 8, 9.6, u'2015-03-17 17:53:41']
            ]

        i = 0
        for vlasnik in sortirani_vlasnici:
            if vlasnik.nudi_gorivo(vrsta_goriva):
                if vlasnik.broj_postaja(vrsta_goriva) >= limit:
                    self.assertEqual([
                        vlasnik.ime(),
                        vlasnik.cijene_sa_brojem_postaja(vrsta_goriva),
                        vlasnik.broj_postaja(vrsta_goriva),
                        round(vlasnik.indeks(vrsta_goriva), 2),
                        vlasnik.vrijeme_zadnjeg_upisa(vrsta_goriva)
                    ],ocekivani_rezultati[i])
                    i += 1

    def test_nepromijenjeni_indeksi(self):
        vrsta_goriva = 2
        
        sortirani_vlasnici = sorted(self.vlasnici.values(), key=lambda v: v.indeks(vrsta_goriva))

        ocekivani_rezultati = [
            ["Benzinska postaja Draž, PZ Topolje"],
            ["MARP-PROMET d.o.o."],
            ["Čukelj d.o.o."],
            ["Hodak d.o.o."],
            ["Šola d.o.o."],
            ["SIROVINA BENZ TRANSPORT d.o.o."],
            ["Metalmineral d.d."],
            ["TURBO BENZ"],
            ["ATTENDO CENTAR d.o.o."],
            ["Tromilja benzin d.o.o."],
            ["Repromaterijal d.o.o."],
            ["KRIVAČA PETROL d.o.o."],
        ]

        i = 0
        for vlasnik in sortirani_vlasnici:
            if vlasnik.nudi_gorivo(vrsta_goriva):
                if (vlasnik.vrijeme_zadnjeg_upisa(vrsta_goriva) == '2015-03-10 10:03:13'):
                    self.assertEqual([vlasnik.ime()], ocekivani_rezultati[i])
                    i += 1

    def test_cijene(self):
        vrsta_goriva = 2
        limit = 4
        
        cijene_sa_vlasnicima = gen_cijene_sa_vlasnicima(self.vlasnici)

        ocekivani_rezultati = [
            [9.75, [('Dirus Projekt d.o.o.', 8)]],
            [9.77, [('Crodux Derivati Dva d.o.o.', 9), ('INA \xe2\x80\x93 Industrija nafte d.d.', 8)]],
            [9.62, [('INA \xe2\x80\x93 Industrija nafte d.d.', 20), ('Tifon d.o.o.', 6)]],
            [9.66, [('Adria Oil d.o.o.', 6), ('Apios d.o.o.', 5), ('INA \xe2\x80\x93 Industrija nafte d.d.', 5), ('LUKOIL Croatia d.o.o.', 45)]],
            [9.28, [('Crodux Derivati Dva d.o.o.', 53)]],
            [9.32, [('Adria Oil d.o.o.', 10), ('Apios d.o.o.', 5), ('INA - Osijek Petrol d.d.', 10), ('INA \xe2\x80\x93 Industrija nafte d.d.', 265), ('KTC d.d.', 4), ('Tifon d.o.o.', 28)]],
            [9.31, [('LUKOIL Croatia d.o.o.', 48)]],
            [9.42, [('INA \xe2\x80\x93 Industrija nafte d.d.', 8)]],
            [9.27, [('INA \xe2\x80\x93 Industrija nafte d.d.', 21), ('Tifon d.o.o.', 4)]],
            [9.6, [('Crno Zlato d o o', 4)]],
            [9.22, [('Konzum d.d.', 4)]],
            [9.98, [('Crno Zlato d o o', 4)]],
            [9.3, [('Tifon d.o.o.', 4)]],
            [9.4, [('Dirus Projekt d.o.o.', 9)]],
            [9.59, [('Konzum d.d.', 4)]],
            [9.38, [('Crodux Derivati Dva d.o.o.', 9)]],
            [9.67, [('Adria Oil d.o.o.', 4), ('Crodux Derivati Dva d.o.o.', 54), ('INA - Osijek Petrol d.d.', 10), ('INA \xe2\x80\x93 Industrija nafte d.d.', 258), ('KTC d.d.', 5), ('Tifon d.o.o.', 29)]]
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
        self.assertEqual(round(vlasnik.indeks(vrsta_goriva), 2), 9.22)
        self.assertEqual(vlasnik.vrijeme_zadnjeg_upisa(vrsta_goriva), u'2015-03-17 17:53:41')
        self.assertEqual(vlasnik.vrijeme_zadnje_promjene_cijene(vrsta_goriva), u'2015-03-17 17:53:41')

if __name__ == '__main__':
    unittest.main()
