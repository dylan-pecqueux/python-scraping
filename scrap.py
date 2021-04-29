import requests
from bs4 import BeautifulSoup

url = 'http://books.toscrape.com/catalogue/category/books/mystery_3/index.html'

response = requests.get(url)

links = []

if response.ok:
    soup = BeautifulSoup(response.text, 'html.parser')
    ol = soup.select('ol li h3 a')
    for a in ol:
        link = a['href']
        links.append(
            'http://books.toscrape.com/catalogue/category/books/mystery_3/' + link)

with open('mistery.csv', 'w') as outf:
    outf.write('title,product_page_url,universal_ product_code (upc),price_including_tax,price_excluding_tax,number_available,product_description,category,review_rating,image_url')
    for l in links:
        response = requests.get(l)
        if response.ok:
            soup = BeautifulSoup(response.text, 'html.parser')
            title =


print(links)
