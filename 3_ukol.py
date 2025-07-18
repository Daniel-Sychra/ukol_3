"""
main.py: třetí projekt do Engeto Online Python Akademie
author: Daniel Sychra
email: daniel.sychra@gmail.com
"""

import sys
import requests
import csv

from bs4 import BeautifulSoup


def scraper():
    """

    Ukázka: #  python3 scraper.py "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2107" "vysledky_mlada_boleslav.csv"
    :return:
    """
    if len(sys.argv) != 3:
        print("Nebyly zadány všechny potřebné parametry.\nUkončuji program.")
        print("Prosím přečtěte si přiloženou dokumentaci a akci opakujte.")
        sys.exit(1)

    web_page = sys.argv[1]
    name_file = sys.argv[2]

    print(f"STAHUJI DATA Z VYBRANÉHO CÍLE: {sys.argv[1]}")

    soup = bs_soup(web_page)
    city_code_numbers_new = city_code_numbers(soup)
    city_names_new = city_names(soup)
    city_links = city_urls(soup)
    scraped_city_data, parties_all = city_scraper(city_links, city_code_numbers_new, city_names_new)
    header = header_maker(parties_all)
    output_to_csv(scraped_city_data, header, name_file)


def bs_soup(web_page):
    req = requests.get(web_page)

    if req.status_code == 200:
        soup = BeautifulSoup(req.content, "html.parser")
        return soup


def city_urls(soup):
    """Since other locations can have other links, we have to generate complete links for all possibilities."""
    city_urls = []
    tables = soup.find_all("td", class_="cislo")
    for table in tables:
        link = table.find("a")
        url = link["href"]
        city_urls.append(url)

    return city_urls


def city_code_numbers(soup) -> list[int]:
    """Vytvoří list s kódy jednotlivých obcí"""
    city_numbers = soup.find_all("td", class_="cislo")
    city_code_numbers_new = [int(number.getText(strip=True)) for number in city_numbers]
    return city_code_numbers_new


def city_names(soup) -> list[str]:
    """Vytvoř list se jmény jednotlivých obcí."""
    names = soup.find_all("td", class_="overflow_name")
    city_names_new = [name.get_text(strip=True) for name in names]
    return city_names_new


def city_scraper(city_links, city_code_numbers_new,
                 city_names_new) -> 'tuple[list[dict[str | str, str | list[str] | str]], list[str]]':
    """funkce stáhne data pro každý okrsek. Tato data přidá postupně do slovníku. Pokračuje dalším odkazem.
     Po vyčerpání všech okrsků vrátí tento slovník."""
    print("Stahuji data z jednotlivých obcí...")
    scraped_city_data = []

    for index, link in enumerate(city_links):
        city_part_scraper = requests.get(
            f"https://volby.cz/pls/ps2017nss/{link}")

        city_part_soup: BeautifulSoup = BeautifulSoup(city_part_scraper.content, "html.parser")

        city_name = city_names_new[index]
        number = city_code_numbers_new[index]

        registered = city_part_soup.find("td").find_next().find_next().find_next().get_text()
        envelopes = city_part_soup.find(
            "td", class_="cislo").find_next().find_next().find_next().find_next().get_text()
        valid = city_part_soup.find(
            "td",
            class_="cislo").find_next_sibling().find_next().find_next().find_next().find_next().find_next().find_next().get_text()

        voices_data = city_part_soup.select("td:nth-child(3)")
        voices_parties = [voice.getText(strip=True) for voice in voices_data[1:]]

        parties_data = city_part_soup.find_all("td", class_="overflow_name")
        parties_all = ([party.getText(strip=True) for party in parties_data])

        elect_parties_with_voices = dict()

        for i, name in enumerate(parties_all):
            elect_parties_with_voices[name] = voices_parties[i]

        data_city = {
            'codes': number,
            'location': city_name,
            'registered': registered,
            'envelopes': envelopes,
            'valid': valid
        }
        for key, value in elect_parties_with_voices.items():
            data_city[key] = value

        scraped_city_data.append(data_city)

    return scraped_city_data, parties_all


def header_maker(parties_all) -> list[str]:
    """Funkce iteruje seznamem jednotlivých volebních stran a přidává je do listu jako budoucí hlavičku"""
    header = ["codes", "location", "registered", "envelopes", "valid"]
    for party in parties_all:
        header.append(party)
    return header


def output_to_csv(scraped_city_data, header, name_file) -> csv:
    """zapisuje získaná data do souboru se jménem uvedeném ve spouštěcím argumentu scriptu scrapera"""
    print("Zapisuji do souboru:", name_file)
    with open(name_file, mode="w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=header, dialect="excel")
        writer.writeheader()
        for city in scraped_city_data:
            if city == 0:
                continue
            else:
                writer.writerow(city)
    print("HOTOVO, ukončuji election scraper.")


if __name__ == "__main__":
    scraper()
