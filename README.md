# Volební výsledky - Web Scraper

Python skript pro stahování výsledků parlamentních voleb 2017 z oficiálních stránek volby.cz.

Skript vyžaduje 2 povinné argumenty:
"URL_územního_celku" "výstupní_soubor.csv"

Příklad spuštění:
python 3_ukol.py "https://www.volby.cz/pls/ps2017/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2107" "vysledky_prostejov.csv"

Program generuje CSV soubor s následující strukturou:
Kód obce
Název obce
Voliči v seznamu
Vydané obálky
Platné hlasy
Hlasy pro jednotlivé politické strany (každá strana v samostatném sloupci)

Požadavky:
Python 3.6+
Knihovny (automaticky nainstalovány z requirements.txt):
requests
beautifulsoup4
pandas
