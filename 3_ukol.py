import sys
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin

def check_arguments():
    """Ověří správnost zadaných argumentů"""
    if len(sys.argv) != 3:
        print("Chyba: Program vyžaduje 2 argumenty - URL a výstupní soubor.")
        print("Příklad použití: python election_scraper.py 'URL' 'vysledky.csv'")
        sys.exit(1)
        
    url = sys.argv[1]
    if not url.startswith('https://www.volby.cz/pls/ps2017/'):
        print("Chyba: Neplatná URL. Očekává se URL výsledků voleb.")
        sys.exit(1)
        
    return url, sys.argv[2]

def get_municipalities_links(main_url):
    """Získá odkazy na výsledky pro jednotlivé obce"""
    try:
        response = requests.get(main_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Najde tabulku s obcemi
        table = soup.find('table', {'class': 'table'})
        if not table:
            raise ValueError("Tabulka s obcemi nebyla nalezena.")
            
        links = []
        for row in table.find_all('tr')[2:]:  # Přeskočí hlavičku
            cols = row.find_all('td')
            if len(cols) >= 3:
                link = cols[0].find('a') or cols[1].find('a')
                if link and 'href' in link.attrs:
                    full_url = urljoin(main_url, link['href'])
                    code = cols[0].get_text(strip=True)
                    name = cols[1].get_text(strip=True)
                    links.append((code, name, full_url))
                    
        return links
    except Exception as e:
        print(f"Chyba při získávání odkazů na obce: {e}")
        sys.exit(1)

def scrape_election_data(url):
    """Získá volební data pro konkrétní obec"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Základní údaje
        headers = soup.find_all('h3')
        voters = headers[2].find_next('td').get_text(strip=True).replace('\xa0', '')
        envelopes = headers[3].find_next('td').get_text(strip=True).replace('\xa0', '')
        valid = headers[4].find_next('td').get_text(strip=True).replace('\xa0', '')
        
        # Výsledky stran
        parties_data = {}
        tables = soup.find_all('table', {'class': 'table'})
        if len(tables) > 1:
            parties_table = tables[1]
            for row in parties_table.find_all('tr')[2:]:  # Přeskočí hlavičky
                cols = row.find_all('td')
                if len(cols) >= 3:
                    party_name = cols[1].get_text(strip=True)
                    votes = cols[2].get_text(strip=True).replace('\xa0', '')
                    parties_data[party_name] = votes
                    
        return {
            'voliči_v_seznamu': voters,
            'vydané_obálky': envelopes,
            'platné_hlasy': valid,
            **parties_data
        }
    except Exception as e:
        print(f"Chyba při scrapování dat pro URL {url}: {e}")
        return None

def main():
    # Hlavička skriptu
    print("="*50)
    print("Scraper volebních výsledků - Parlamentní volby 2017")
    print("Autor: [Vaše jméno]")
    print("="*50)
    
    # Kontrola argumentů
    main_url, output_file = check_arguments()
    
    # Získání odkazů na obce
    print(f"Získávání seznamu obcí z URL: {main_url}")
    municipalities = get_municipalities_links(main_url)
    print(f"Nalezeno {len(municipalities)} obcí ke zpracování.")
    
    # Scrapování dat pro každou obec
    results = []
    for idx, (code, name, url) in enumerate(municipalities, 1):
        print(f"Zpracovávám {idx}/{len(municipalities)}: {name} ({code})")
        data = scrape_election_data(url)
        if data:
            results.append({
                'kód_obce': code,
                'název_obce': name,
                **data
            })
    
    # Uložení výsledků
    if results:
        df = pd.DataFrame(results)
        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"Data úspěšně uložena do souboru {output_file}")
    else:
        print("Nebyla získána žádná data k uložení.")

if __name__ == "__main__":
    main()
