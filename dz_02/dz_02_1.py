#!/usr/bin/python3
import requests
import re
import json
import sys
import os


def get_iata_page_link(town):
    return "https://www.nationsonline.org/oneworld/IATA_Codes/airport_code_%s.htm" % (town[0].lower())


def parse_all_letter_iata_codes(town):
    link = get_iata_page_link(town)
    req = requests.get(link)
    html = req.text
    pattern = r"<tr>\n<td class=\"border1\">.+</td>\n<td class=\"border1\">.+</td>\n<td class=\"border1\">.+</td>\n<td class=\"border1\">.+</td>\n</tr>"
    all_letter_iatas = re.findall(pattern, html)
    return all_letter_iatas


def get_rec_city(rec):
    dirty_city_pattern = r"<tr>\n<td class=\"border1\">.+</td>"
    dirty_city = re.findall(dirty_city_pattern, rec)[0]
    clean_pattern1 = "\n+"
    clean_pattern2 = r"<[^>]+>"
    clean_pattern3 = r"\([^\)]+\)"
    clean_pattern4 = r"[ ]+$"
    city_clean = re.sub(clean_pattern1, "", dirty_city)
    city_clean = re.sub(clean_pattern2, "", city_clean)
    city_clean = re.sub(clean_pattern3, "", city_clean)
    city_clean = re.sub(clean_pattern4, "", city_clean)
    return city_clean


def get_rec_iata(rec):
    dirty_iata_pattern = r"<td class=\"border1\">.+</td>\n</tr>"
    dirty_iata = re.findall(dirty_iata_pattern, rec)[0]
    clean_pattern1 = "\n+"
    clean_pattern2 = r"<[^>]+>"
    clean_pattern3 = r"\([^\)]+\)"
    clean_pattern4 = r"[ ]+$"
    iata_clean = re.sub(clean_pattern1, "", dirty_iata)
    iata_clean = re.sub(clean_pattern2, "", iata_clean)
    iata_clean = re.sub(clean_pattern3, "", iata_clean)
    iata_clean = re.sub(clean_pattern4, "", iata_clean)
    return iata_clean


def get_town_iata(town):
    town = town.capitalize()
    all_letter_data = parse_all_letter_iata_codes(town)
    letter_cities_iatas_dict = {}
    for rec in all_letter_data:
        city = get_rec_city(rec).capitalize()
        if city.startswith(town[0]):
            if city not in letter_cities_iatas_dict:
                letter_cities_iatas_dict[city] = [get_rec_iata(rec)]
            else:
                letter_cities_iatas_dict[city].append(get_rec_iata(rec))
    if town in letter_cities_iatas_dict:
        return letter_cities_iatas_dict[town]
    else:
        print("There is no \'%s\' in list, but all \'%s\'-letter towns list are:" % (
            town.capitalize(), town[0].capitalize()))
        for city_name in sorted(list(letter_cities_iatas_dict.keys())):
            print("\t", city_name)
        exit()


def get_best_price_two_directions(from_iata, to_iata):
    req = requests.get(
        "http://min-prices.aviasales.ru/calendar_preload?origin=%s&destination=%s" % (from_iata, to_iata))
    data = json.loads(req.text)
    if "best_prices" in data:
        return data['best_prices'][0]
    else:
        return None


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage:\n\t", "python3", os.path.basename(__file__), "from_town", "to_town\nExample:\n\t", "python3",
              os.path.basename(__file__), '\"St. petersburg\"', "Moscow")
        exit()
    else:
        from_town = sys.argv[1]
        to_town = sys.argv[2]

        from_town_iata = get_town_iata(from_town)
        to_town_iata = get_town_iata(to_town)

        print(from_town.capitalize(), "iata:", from_town_iata)
        print(to_town.capitalize(), "iata:", to_town_iata)
        print()

        for from_iata in from_town_iata:
            for to_iata in to_town_iata:
                tmp_data = get_best_price_two_directions(from_iata, to_iata)
                print("From", from_town.capitalize() + "(" + from_iata + ")", "to",
                      to_town.capitalize() + "(" + to_iata + "):")
                if tmp_data is not None:
                    print("\t\tDepart date:", tmp_data["depart_date"])
                    print("\t\tReturn date:", tmp_data["return_date"])
                    print("\t\tTicket price:", tmp_data["value"])
                    print("\t\tGate:", tmp_data["gate"])
                else:
                    print("\t\tNo variants")
                print()
