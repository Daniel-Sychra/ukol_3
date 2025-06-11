"""
main.py: třetí projekt do Engeto Online Python Akademie
author: Daniel Sychra
email: daniel.sychra@gmail.com
"""

import requests
from bs4 import BeautifulSoup
import csv
import time

def nacti_parametry_z_csv(cesta_souboru):
    """
    Načte parametry z CSV souboru s očekávanou strukturou:
    nazev_obce,kraj,obec_kod,xnumnuts
    """
    obce = []
    with open(cesta_souboru, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            obce.append({
                'nazev': row['nazev_obce'],
                'kraj': row['kraj'],
                'obec_kod': row['obec_kod'],
                'vyber': row['xnumnuts']
            })
    return obce

def vytvor_spravne_url(obec):
    """Vytvoří platnou URL adresu pro danou obec"""
    base_url = 'https://www.volby.cz/pls/ps2017nss/ps32'
    return (f"{base_url}?xjazyk=CZ&xkraj={obec['kraj']}"
            f"&xobec={obec['obec_kod']}&xvyber={obec['vyber']}")

def ziskej_html(url):
    """Získá HTML obsah s ošetřením chyb a hlavičkami"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Chyba při stahování {url}: {str(e)}")
        return None

def zpracuj_data(html, obec_info):
    """Zpracuje HTML a extrahuje požadovaná data"""
    soup = BeautifulSoup(html, 'html.parser')
    
    # Získání základních informací
    data = {
        'Obec': obec_info['nazev'],
        'Voliči': soup.find('td', {'headers': 'sa2'}).text.replace('\xa0', ''),
        'Vydané obálky': soup.find('td', {'headers': 'sa3'}).text.replace('\xa0', ''),
        'Platné hlasy': soup.find('td', {'headers': 'sa6'}).text.replace('\xa0', '')
    }
    
    # Získání výsledků stran
    for row in soup.select('table.tableres ttr_header + tr'):
        cells = row.find_all('td')
        if len(cells) >= 3:
            nazev_strany = cells[1].text
            hlasy = cells[2].text.replace('\xa0', '')
            data[nazev_strany] = hlasy
    
    return data

def main():
    # Konfigurace
    vstupni_soubor = 'obce.csv'
    vystupni_soubor = 'vysledky.csv'
    zpozdeni = 3  # Sekundy mezi requesty
    
    # Načtení dat
    obce = nacti_parametry_z_csv(vstupni_soubor)
    
    # Zpracování každé obce
    with open(vystupni_soubor, 'w', newline='', encoding='utf-8') as csvfile:
        writer = None
        
        for obec in obce:
            url = vytvor_spravne_url(obec)
            print(f"Zpracovávám: {obec['nazev']} ({url})")
            
            html = ziskej_html(url)
            if not html:
                continue
            
            data = zpracuj_data(html, obec)
            
            # Inicializace CSV writeru s hlavičkou
            if not writer:
                hlavicka = list(data.keys())
                writer = csv.DictWriter(csvfile, fieldnames=hlavicka)
                writer.writeheader()
            
            writer.writerow(data)
            
            time.sleep(zpozdeni)

if __name__ == "__main__":
    main()
