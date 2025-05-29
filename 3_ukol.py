"""

Tento skript stahuje volební výsledky z volby.cz pro zadaný územní celek.
"""

import sys
import requests
from bs4 import BeautifulSoup
import csv
import time

# Hlavičky pro simulaci webového prohlížeče
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def validate_arguments():
    """Ověří správnost vstupních argumentů"""
    if len(sys.argv) != 3:
        print("Chyba: Zadejte prosím 2 argumenty - URL a název výstupního souboru.")
        print("Příklad: python script.py 'https://example.com' 'vysledky.csv'")
        sys.exit(1)
    
    url = sys.argv[1]
    if not url.startswith('https://www.volby.cz/pls/ps2017nss/'):
        print("Chyba: Neplatná URL. Zadejte platnou URL volebních výsledků z volby.cz.")
        sys.exit(1)
    
    return url, sys.argv[2]

def get_municipalities_links(main_url):
    """Získá seznam obcí a odkazů na jejich výsledky"""
    try:
        response = requests.get(main_url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        municipalities = []
        table = soup.find('table', {'class': 'table'})
        
        if not table:
            print("Chyba: Nepodařilo se najít tabulku s obcemi.")
            return []
        
        rows = table.find_all('tr')[2:]  # První 2 řádky jsou hlavička
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                code = cols[0].text.strip()
                name = cols[1].text.strip()
                
                # Najdeme první dostupný odkaz
                link = cols[0].find('a') or cols[2].find('a')
                if link and link.has_attr('href'):
                    full_link = f"https://www.volby.cz/pls/ps2017nss/{link['href']}"
                    municipalities.append({
                        'code': code,
                        'name': name,
                        'link': full_link
                    })
        
        return municipalities
    
    except Exception as e:
        print(f"Chyba při získávání seznamu obcí: {e}")
        return []

def scrape_municipality_data(municipality):
    """Získá volební výsledky pro jednu obec"""
    try:
        response = requests.get(municipality['link'], headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Hledání základních údajů
        voters = soup.find('td', headers='sa2').text.replace('\xa0', ' ')
        envelopes = soup.find('td', headers='sa3').text.replace('\xa0', ' ')
        valid = soup.find('td', headers='sa6').text.replace('\xa0', ' ')
        
        # Hledání výsledků stran
        parties_table = soup.find('table', {'id': 'inner'})
        parties_data = {}
        
        if parties_table:
            for row in parties_table.find_all('tr')[2:]:  # Přeskočení hlavičky
                cols = row.find_all('td')
                if len(cols) >= 3:
                    party_name = cols[1].text.strip()
                    votes = cols[2].text.replace('\xa0', ' ').strip()
                    parties_data[party_name] = votes
        
        return {
            'code': municipality['code'],
            'name': municipality['name'],
            'voters': voters,
            'envelopes': envelopes,
            'valid': valid,
            **parties_data
        }
    
    except Exception as e:
        print(f"Chyba při zpracování obce {municipality['name']}: {e}")
        return None

def write_to_csv(data, filename):
    """Uloží data do CSV souboru"""
    if not data:
        print("Chyba: Žádná data k uložení.")
        return
    
    # Získání všech názvů stran pro hlavičku
    all_parties = set()
    for item in data:
        all_parties.update(item.keys())
    
    standard_fields = ['code', 'name', 'voters', 'envelopes', 'valid']
    party_fields = sorted([p for p in all_parties if p not in standard_fields])
    fieldnames = standard_fields + party_fields
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        print(f"Data úspěšně uložena do souboru {filename}")
    except Exception as e:
        print(f"Chyba při ukládání do CSV: {e}")

def main():
    """Hlavní funkce pro řízení scrapování"""
    url, output_file = validate_arguments()
    
    print(f"Stahuji data z: {url}")
    municipalities = get_municipalities_links(url)
    
    if not municipalities:
        print("Chyba: Nebyly nalezeny žádné obce.")
        sys.exit(1)
    
    print(f"Nalezeno {len(municipalities)} obcí. Zahajuji stahování...")
    
    all_data = []
    for i, mun in enumerate(municipalities, 1):
        print(f"Zpracovávám {i}/{len(municipalities)}: {mun['name']}...", end='\r')
        data = scrape_municipality_data(mun)
        if data:
            all_data.append(data)
        time.sleep(0.5)  # Pauza mezi požadavky
    
    if all_data:
        write_to_csv(all_data, output_file)
    else:
        print("\nChyba: Nepodařilo se získat žádná data.")

if __name__ == "__main__":
    main()
