import requests
from bs4 import BeautifulSoup
import csv
import io
from PIL import Image
import os.path


def save_img(url, name):
    response = requests.get(url)

    if response.ok:
        try:
            image_file = io.BytesIO(response.content)
            image = Image.open(image_file).convert("RGB")
            file_path = os.path.join("./images", name.replace(" ", "-") + ".jpg")
            with open(file_path, "wb") as f:
                image.save(f, "JPEG", quality=85)
        except Exception as e:
            print(f"ERROR - Could not save {url} - {e}")
    else:
        print("ERROR - Can not get the url")


def transform_rating(rating):
    if rating == "One":
        return "1/5"
    elif rating == "Two":
        return "2/5"
    elif rating == "Three":
        return "3/5"
    elif rating == "Four":
        return "4/5"
    else:
        return "5/5"


def get_book_info(link):
    response = requests.get(link)
    if response.ok:
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.find("h1").text.replace(",", " - ")
        tr = soup.find_all("td")
        upc = tr[0].text
        price_including_tax = tr[3].text.replace("Â", "")
        price_excluding_tax = tr[2].text.replace("Â", "")
        number_available = tr[5].text.split()
        try:
            description = soup.find(
                "div", id="product_description"
            ).next_sibling.next_sibling.text
        except Exception as e:
            print(f"Error - {e}")
            description = "None"
        get_rating = soup.select_one(".star-rating")["class"][1]
        rating = transform_rating(get_rating)
        img_url = "http://books.toscrape.com/" + soup.select_one(".item img")[
            "src"
        ].replace("../../", "")

        return {
            "title": title,
            "upc": upc,
            "price_including_tax": price_including_tax,
            "price_excluding_tax": price_excluding_tax,
            "number_available": number_available,
            "description": description,
            "rating": rating,
            "img_url": img_url,
        }


def get_books(category_name, links):
    file_name = "./csv/" + category_name.strip().replace(" ", "-") + ".csv"
    with open(file_name, "w") as outf:
        writer = csv.writer(outf, delimiter=",", quoting=csv.QUOTE_MINIMAL)
        writer.writerow(
            [
                "title",
                "product_page_url",
                "universal_ product_code (upc)",
                "price_including_tax",
                "price_excluding_tax",
                "number_available",
                "product_description",
                "category",
                "review_rating",
                "image_url",
            ]
        )

        for link in links:
            book_info = get_book_info(link)
            print(book_info["title"])

            outf.write(
                f"{book_info['title']},{link},{book_info['upc']},{book_info['price_including_tax']},{book_info['price_excluding_tax']},{book_info['number_available'][2].replace('(', '')},{book_info['description'].replace(',', ' ').replace(';', ' ')},{category_name},{book_info['rating']},{book_info['img_url']} \n"
            )

            save_img(book_info["img_url"], book_info["title"])


def get_links(url, category_name):
    links = []
    base_page_url = url.replace("index.html", "")

    def pages(url):
        response = requests.get(url)

        if response.ok:
            soup = BeautifulSoup(response.text, "html.parser")
            ol = soup.select("ol li h3 a")

            for a in ol:
                link = a["href"].replace("../../../", "")
                links.append("http://books.toscrape.com/catalogue/" + link)
            next_page = soup.select_one(".next a")
            if next_page != None:
                next_page_url = base_page_url + next_page["href"]
                pages(next_page_url)
            else:
                get_books(category_name, links)
        else:
            print("ERROR - Can not get the url")

    pages(url)


def get_categories():
    response = requests.get("http://books.toscrape.com/index.html")
    if response.ok:
        soup = BeautifulSoup(response.text, "html.parser")
        ul = soup.select(".nav-list li ul li a")

        for link in ul:
            links = "http://books.toscrape.com/" + link["href"]
            category_name = link.text.strip()
            get_links(links, category_name)
    else:
        print("ERROR - Can not get the url")


def main():
    get_categories()


if __name__ == "__main__":
    main()
