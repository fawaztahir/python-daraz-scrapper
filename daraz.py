import sys
import time
import csv

from selenium import webdriver
from bs4 import BeautifulSoup
import urllib.parse

CHROME_DRIVER = '/Users/fawaztahir/Desktop/chromedriver/chromedriver'

ITEM_CLASS = 'c2prKC'
TITLE_CLASS = 'c16H9d'
PRICE_CLASS = 'c13VH6'
NO_OF_RATING_CLASS = 'c3XbGJ'
STARS_CLASS = 'c3dn4k'

FULL_STAR_CLASS = 'c3EEAg'
HALF_STAR_CLASS = 'c1e2gb'
NO_STAR_CLASS = 'c1dtTC'

def calculate_rating_from_stars(stars):
    rating = 0

    if len(stars) > 0:
        for star in stars:
            if FULL_STAR_CLASS in star['class']:
                rating += 1
            elif HALF_STAR_CLASS in star['class']:
                rating += 0.5

    return rating;


def convert_price_integer(price):
    price = int(''.join(price.lower().lstrip('rs. ').split(',')))
    return price


args = sys.argv
keyword = ''
print(args)

if len(args) > 0 and len(args) != 2:
    exit('Scrapping accepts only one argument. Please wrap your keyword in ""')
else:
    keyword = args[1].lower()

while True and keyword == '':
    keyword = input("What items you want to search on Daraz.pk? ")

    if keyword != '':
        break;

    print("Please provide a keyword")

url = f'https://www.daraz.pk/catalog/?q={urllib.parse.quote(keyword.lower())}'

print(f'Requesting: {url}')

options = webdriver.ChromeOptions()
options.add_argument('--headless')

driver = webdriver.Chrome(CHROME_DRIVER, options=options)
driver.get(url)

print("Request complete. Waiting for 5 seconds. This will complete any ajax requests found on page.")
time.sleep(5)

soup = BeautifulSoup(driver.page_source, 'html.parser')

items_list = soup.find_all('div', class_ = ITEM_CLASS)

if items_list:
    print(f"Found {len(items_list)} items")
    data = []

    for item in items_list:
        anchor = item.select(f"div.{TITLE_CLASS} a")[0]
        title = anchor.get_text()
        price = item.select(f"span.{PRICE_CLASS}")[0].get_text()
        url = anchor['href']

        rating_reviews_no = item.select('div.c2JB4x')
        if len(rating_reviews_no) > 0:
            no_of_ratings = int(rating_reviews_no[0].find('span', class_ = NO_OF_RATING_CLASS).get_text().lstrip('(').rstrip(')'))
            stars = rating_reviews_no[0].find_all('i', class_ = STARS_CLASS)
            rating = calculate_rating_from_stars(stars)
        else:
            no_of_ratings = 0
            rating = 0

        available_for_installment = None is not item.find('div', class_ = "c3ubLI")

        dictx = {
            'Title': title,
            'Price': convert_price_integer(price),
            'Permalink': url,
            'No of ratings': no_of_ratings,
            'Rating': rating,
            'Installment': available_for_installment
        }

        data.append(dictx)
    
    with open('data.csv', mode='w') as csv_file:
        headers = ['Title', 'Price', 'No of ratings', 'Rating', 'Installment', 'Permalink']
        writer = csv.DictWriter(csv_file, fieldnames=headers)

        writer.writeheader()

        for d in data:
            writer.writerow(d)

        csv_file.close()


    from pandas import read_csv as prcsv

    dataframe = prcsv('data.csv', index_col='Title')
    dataframe.sort_values("Price", ascending=False, inplace=True)

    print(dataframe)


print("Finished")