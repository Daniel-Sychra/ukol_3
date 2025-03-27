# Volební výsledky - Web Scraper

Python skript pro stahování výsledků parlamentních voleb 2017 z oficiálních stránek volby.cz.

# Skript vyžaduje 2 povinné argumenty:
"URL_územního_celku" a "výstupní_soubor.csv"

# Program generuje CSV soubor s následující strukturou:
Kód obce
Název obce
Voliči v seznamu
Vydané obálky
Platné hlasy
Hlasy pro jednotlivé politické strany (každá strana v samostatném sloupci)

# Ukázka výstupu

Výstupní CSV soubor obsahuje následující data:

| kód_obce | název_obce       | voliči | obálky | platné hlasy | ANO | ODS | SPD | Piráti | STAN | KDU-ČSL | TOP 09 |
|----------|------------------|--------|--------|--------------|-----|-----|-----|--------|------|---------|--------|
| 589268   | Prostějov        | 15234  | 9876   | 9654         | 3245| 1876| 987 | 654    | 321  | 543     | 210    |
| 589276   | Kostelec na Hané | 4231   | 3210   | 3154         | 987 | 654 | 321 | 210    | 98   | 154     | 87     |
| 589284   | Drahany          | 857    | 643    | 621          | 210 | 87  | 65  | 43     | 21   | 54      | 32     |


# Požadavky

Python 3.6+
Knihovny (automaticky nainstalovány z requirements.txt):
requests
beautifulsoup4
pandas
