# mingoparser
A python library consuming min-go.hr API.

[min-go.hr](http://min-go.hr/) je portal koji na osnovi lokacije korisnika određuje benzinske postaje sa najjeftinijim gorivom.

mingoparser je python biblioteka koja dohvaća i obrađuje podatke sa portala min-go.hr, te omogućava korištenje tih podataka u python aplikacijama, kao što je, primjerice, projekt [indexgoriva](https://github.com/dijxtra/indexgoriva).

Projekt je započet na [Code for Croatia](http://codeforcroatia.org/) hackatronu 21.2.2015.

### Status projekta
mingoparser je u pre-alpha fazi

### Roadmap
1. pisanje unit testova za postojeći kod
1. implementiranje klase Tvrtka koja će sadrži sve cijene pojedine vrste goriva za jednu tvrtku
1. izračun indexa cijene goriva: izračun ponderirane prosječne cijene pojedine vrste goriva za svaku tvrtku i hrvatsku u cijelini
1. upisivanje vrijednosti indexa u SQL bazu (za praćenje trendova)
1. ispis postaja pojedine tvrtke koje imaju istu cijenu

### Licenca
Biblioteka je licencirana sa GPLv3.
