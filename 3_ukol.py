"""
main.py: třetí projekt do Engeto Online Python Akademie
author: Petr Svetr
email: petr.svetr@gmail.com
"""

import sys
import requests
import csv
from typing import List, Tuple, Dict
from bs4 import BeautifulSoup, Tag

def check_arguments() -> None:
    """Kontrola správného počtu a formátu vstupních argumentů"""
    if len(sys.argv) != 3:
        print("Chyba: Zadejte právě dva argumenty - URL a výstupní soubor")
        print("Příklad použití: python main.py 'https://www.volby.cz/...' 'vysledky.csv'")
        sys.exit(1)
        
    if not sys.argv[1].startswith('https://www.volby.cz/pls/ps2017nss/'):
        print("Chyba: Neplatný formát URL. Musí začínat 'https://www.volby.cz/pls/ps2017nss/'")
        sys.exit(1)

def fetch_page(url: str) -> BeautifulSoup:
    """Stažení a parsování HTML stránky"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except requests.RequestException as e:
        print(f"Chyba při načítání stránky: {e}")
        sys.exit(1)

def extract_municipality_links(soup: BeautifulSoup) -> List[Tuple[str, str, str]]:
    """
    Extrakce odkazů na výsledky obcí ze všech tabulek
    Vrací seznam n-tic (kód, název, relativní URL)
    """
    municipalities = []
    
    for table in soup.find_all('table', {'class': 'table'}):
        for row in table.find_all('tr')[2:]:  # Přeskočení hlavičkových řádků
            cols = row.find_all('td')
            if len(cols) >= 3 and cols[0].find('a'):
                code = cols[0].get_text(strip=True)
                name = cols[1].get_text(strip=True)
                link = cols[0].find('a')['href']
                municipalities.append((code, name, link))
    
    return municipalities

def extract_basic_stats(soup: BeautifulSoup) -> Tuple[str, str, str]:
    """Extrakce základních statistických údajů z detailní stránky"""
    return (
        soup.find('td', {'headers': 'sa2'}).get_text().replace('\xa0', ''),
        soup.find('td', {'headers': 'sa3'}).get_text().replace('\xa0', ''),
        soup.find('td', {'headers': 'sa6'}).get_text().replace('\xa0', '')
    )

def extract_party_votes(soup: BeautifulSoup) -> Dict[str, str]:
    """Extrakce výsledků politických stran z výsledkové tabulky"""
    votes = {}
    results_table = soup.find('table', {'id': 'ps311_t1'})
    
    for row in results_table.find_all('tr')[2:]:  # Přeskočení hlavičky
        cells = row.find_all('td')
        if len(cells) >= 3:
            party = cells[1].get_text(strip=True)
            votes[party] = cells[2].get_text().replace('\xa0', '')
    
    return votes

def process_municipality(base_url: str, code: str, name: str, link: str) -> tuple:
    """Zpracování jednoho záznamu obce a získání všech relevantních dat"""
    full_url = f"{base_url}/{link}"
    soup = fetch_page(full_url)
    
    voters, envelopes, valid = extract_basic_stats(soup)
    party_votes = extract_party_votes(soup)
    
    return (code, name, voters, envelopes, valid, *party_votes.values())

def write_results(filename: str, data: List[tuple], parties: List[str]) -> None:
    """Uložení výsledků do CSV souboru s hlavičkou"""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Kód', 'Obec', 'Voliči', 'Obálky', 'Platné hlasy', *parties])
        writer.writerows(data)

def main() -> None:
    check_arguments()
    base_url = sys.argv[1].split('?')[0]
    
    # Získání seznamu všech obcí
    main_page = fetch_page(sys.argv[1])
    municipalities = extract_municipality_links(main_page)
    
    if not municipalities:
        print("Nebyly nalezeny žádné výsledky pro zadané URL")
        sys.exit(1)
    
    # Získání seznamu stran z první obce
    sample_data = process_municipality(base_url, *municipalities[0])
    parties = list(extract_party_votes(fetch_page(f"{base_url}/{municipalities[0][2]}")).keys())
    
    # Zpracování všech obcí
    results = []
    for idx, (code, name, link) in enumerate(municipalities, 1):
        print(f"Zpracovávám: {idx:3}/{len(municipalities)} | {name}")
        results.append(process_municipality(base_url, code, name, link))
    
    write_results(sys.argv[2], results, parties)
    print(f"Úspěšně uloženo do {sys.argv[2]}\nCelkem záznamů: {len(results)}")

if __name__ == "__main__":
    main()
