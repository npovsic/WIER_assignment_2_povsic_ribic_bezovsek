# IEPS: drugi seminar

### Potrebne knjižnice

Za delovanje parserja potrebujemo Python (v našem primeru je bil to Python 3.5.2) in naslednje knjižnice:

* BeautifulSoup (bs4)

* lxml


### Opis

Za drugi seminar smo imeli nalogo izluščiti podatke iz dveh že podanih strani (Overstock in Rtvslo.si) in iz 
poljubne strani, ki smo si jo izbrali sami (Avto.net).

Implementirali smo tri rešitve:

1. Parsanje z regularnim izrazom (regex)
2. Parsanje z XPath
3. Ustvarjanje ovojnice z algoritmom Roadrunner

Parser zaženemo s skripto start.py, ki prebere vse spletne strani iz direktorija "input", jih avtomatsko razčleni z uporabo 
vseh treh metod in shrani v direktorij "output" (če še ne obstaja, ga moramo ustvariti).

Repozitorij vsebuje poročilo o nalogi, direktorij "implementation", kjer se nahajajo skripte, in direktorija "input" in "output".

##### Sodelavci na projektu: Nejc Povšič, Vid Ribič, Luka Bezovšek