# Election Scraper 2017

Skript pro stahování výsledků parlamentních voleb 2017 z volby.cz

## Instalace

1. **Vytvoření virtuálního prostředí** (doporučeno):

python -m venv venv

venv\Scripts\activate.bat # Windows

source venv/bin/activate # Linux/Mac

2. **Instalace závislostí**:

pip install -r requirements.txt

## Použití

**Syntax spuštění**:

python main.py <URL> <VÝSTUPNÍ_SOUBOR>

**Příklad**:

python main.py "https://https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2107" "vysledky_mlada_boleslav.csv"

**Požadovaný formát URL**:
- Musí obsahovat kompletní parametrizovaný odkaz z volby.cz
- Příklad platného URL:  
  "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2107"

## Výstup

Soubor CSV s následující strukturou:
- Kód obce
- Název obce
- Voliči v seznamu
- Vydané obálky
- Platné hlasy
- Počty hlasů pro jednotlivé strany (sloupce se dynamicky přizpůsobí)

## Ukázka zápisu v CSV formátu

Výstupní soubor ve formátu CSV obsahuje následující sloupce:

| kód_obce | název_obce           | voliči | obálky | platné hlasy | ANO 2011 | ODS | SPD | Piráti | STAN | KDU-ČSL | TOP 09 |
|----------|----------------------|--------|--------|--------------|----------|-----|-----|--------|------|---------|--------|
| 535427   | Bakov nad Jizerou    | 3571   | 2391   | 2375         | 748      | 344 | 267 | 224    | 224  | 76      | 71     |
| 535443   | Bělá pod Bezdězem    | 3370   | 2229   | 2213         | 601      | 264 | 265 | 199    | 194  | 66      | 61     |
| 535451   | Benátky nad Jizerou  | 5885   | 3800   | 3776         | 1203     | 510 | 393 | 372    | 291  | 138     | 113    |

### Popis sloupců:

- **kód_obce**: Oficiální kód obce dle volby.cz
- **název_obce**: Název obce
- **voliči**: Počet voličů zapsaných v seznamu
- **obálky**: Počet vydaných obálek
- **platné hlasy**: Počet platných hlasů
- **ANO 2011, ODS, SPD, Piráti, STAN, KDU-ČSL, TOP 09**: Počet hlasů pro jednotlivé kandidující strany v dané obci



