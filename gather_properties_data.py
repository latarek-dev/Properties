import random
import requests
from bs4 import BeautifulSoup as bs
import json
import re
import pandas as pd
import time


def get_info_box(url):
    # Function grabs a single link, does request, scrap and transform information and return single dict

    try:
        flats_info_dict = {}

        req = requests.get(url, timeout=10)  # Request to link
        flat = bs(req.content, features="html.parser")
        price = flat.find(class_="priceInfo__value").get_text(" ",
                                                              strip=True)  # Check is there a price. Omits "Ask a price"
        if price != "Zapytaj o cenę":

            price = price.replace(" ", "")
            price = re.findall('[0-9]+', price)  # Transform price to int format
            flats_info_dict['price'] = price[0]

            title = flat.find(class_="sticker__title").get_text(" ", strip=True)
            flats_info_dict['title'] = title

            location = flat.find(class_="parameters__locationLink").get_text(" ", strip=True)
            flats_info_dict['location'] = location

            parameters = flat.find(class_="parameters__singleParameters")  # Grab class of different parameters
            lis_param = []
            for parameter in parameters.find_all(class_="parameters__value"):
                lis_param.append(parameter.get_text(" ",
                                                    strip=True))  # Convert parameters to list so we can extract specific information

            if "m" in lis_param[1]:  # Parameters sometimes are in weird order. We check if surface is second
                place_var = 1
            else:
                place_var = 2  # This is alternative index for surface

            surface = lis_param[place_var]
            surface = re.findall('[0-9]{1,5},?[0-9]{0,2}', surface)
            surface = float(surface[0].replace(",", "."))  # Transform surface to float format
            flats_info_dict['surface'] = surface

            rooms = lis_param[place_var + 1]  # Rooms are always after surface
            rooms = re.findall('[0-9]{1,3}', rooms)
            flats_info_dict['rooms'] = rooms[0]

        return flats_info_dict

    except (requests.exceptions.ConnectTimeout, Exception) as e:
        print("Exception is :", e)
        if e is Exception:
            return None
        elif e is requests.exceptions.ConnectTimeout:
            time.sleep(300)


def save_data(title, data):
    # Function to save our final data to json
    with open(title, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_data(title):
    # Function to load our data from json
    with open(title, encoding='utf-8') as f:
        return json.load(f)


if __name__ == '__main__':

    url_base_page = "https://gratka.pl/nieruchomosci/mieszkania/warszawa?page=1&promien=5"
    base_request = requests.get(url_base_page).text
    doc = bs(base_request, features="html.parser")
    pagination = doc.find(class_="pagination container").get_text(" ", strip=True)
    pag = list(pagination)[10:13]
    pages = int(''.join(pag))

    flats_info_links = []  # List where are stored links
    for number_page in range(0, pages + 1):
        url = f"https://gratka.pl/nieruchomosci/mieszkania/warszawa?page={number_page}&promien=5"
        page = requests.get(url).text
        soup = bs(page, features="html.parser")

        div = soup.find(class_="listing__content")  # Find div with sales
        container_div = soup.find_all('article', class_='teaserUnified')  # Finds all sales
        for article in container_div:
            el = article.find(href=True)
            link = el['href']  # Extract link to auction
            flats_info_links.append(link)  # Adds link to list

    random.shuffle(flats_info_links)  # Shuffle list of links to imitate humans actions
    print(flats_info_links)

    final_info_flats = []
    for i, flat_link in enumerate(flats_info_links):
        if i % 10 == 0:
            print(i)
        if i % 200 == 0 and i > 0:
            print("Temporary stop. Wait 2 minutes.")
            time.sleep(120)

        flat_info = get_info_box(flat_link)  # We use function to do request and scrape data

        if flat_info is not None:
            final_info_flats.append(flat_info)
        else:
            continue
        time.sleep(random.uniform(0, 2))

    save_data("properties_saved.json", final_info_flats)

    df = pd.DataFrame(final_info_flats)
    print(df.head())
    df.to_csv("properties.csv", index=False, encoding='utf-8', header=True,
              columns=["price", "title", "location", "surface", "rooms"])  # Save data to csv
