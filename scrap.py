import requests
from bs4 import BeautifulSoup
import csv
import io
from PIL import Image
import os.path
import hashlib


def save_img(url):
    try:
        image_content = requests.get(url).content

    except Exception as e:
        print(f"ERROR - Could not download {url} - {e}")

    try:
        image_file = io.BytesIO(image_content)
        image = Image.open(image_file).convert('RGB')
        file_path = os.path.join('./images', hashlib.sha1(
            image_content).hexdigest()[:10] + '.jpg')
        with open(file_path, 'wb') as f:
            image.save(f, "JPEG", quality=85)
        print(f"SUCCESS - saved {url} - as {file_path}")
    except Exception as e:
        print(f"ERROR - Could not save {url} - {e}")


def get_books(category_name, links):
    file_name = './csv/' + category_name.strip().replace(' ', '-') + '.csv'
    with open(file_name, 'w') as outf:
        writer = csv.writer(outf, delimiter=",", quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['title', 'product_page_url', 'universal_ product_code (upc)', 'price_including_tax',
                        'price_excluding_tax', 'number_available', 'product_description', 'category', 'review_rating', 'image_url'])

        for l in links:
            response = requests.get(l)

            if response.ok:
                soup = BeautifulSoup(response.text, 'html.parser')
                title = soup.find('h1')
                print(title.text)
                tr = soup.find_all('td')

                try:
                    description = soup.find(
                        'div', id='product_description').next_sibling.next_sibling.text
                except:
                    description = "None"

                rating = soup.select_one('.star-rating')['class'][1]
                img_url = 'http://books.toscrape.com/' + \
                    soup.select_one('.item img')['src'].replace('../../', '')

                save_img(img_url)

                outf.write(title.text.replace(',', ' - ') + ',' + l + ',' +
                           tr[0].text + ',' + tr[3].text + ',' + tr[2].text + ',' + tr[5].text + ',' + description.replace(',', ' ').replace(';', ' ') + ',' + category_name + ',' + rating + ',' + img_url + '\n')


def get_links(url, category_name):
    links = []
    base_page_url = url.replace('index.html', '')

    def pages(url):
        print(url)
        response = requests.get(url)
        print(response)

        if response.ok:
            soup = BeautifulSoup(response.text, 'html.parser')
            ol = soup.select('ol li h3 a')

            for a in ol:
                link = a['href'].replace('../../../', '')
                links.append('http://books.toscrape.com/catalogue/' + link)
            next_page = soup.select_one('.next a')
            if next_page != None:
                next_page_url = base_page_url + next_page['href']
                pages(next_page_url)
            else:
                get_books(category_name, links)
    pages(url)


def get_categories():
    response = requests.get('http://books.toscrape.com/index.html')
    if response.ok:
        soup = BeautifulSoup(response.text, 'html.parser')
        ul = soup.select('.nav-list li ul li a')

        for l in ul:
            links = 'http://books.toscrape.com/' + l['href']
            category_name = l.text
            get_links(links, category_name)


get_categories()
