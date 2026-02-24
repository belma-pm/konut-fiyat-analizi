import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://books.toscrape.com/"
headers = {"User-Agent": "Mozilla/5.0"}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

books = soup.find_all("article", class_="product_pod")

data = []

for book in books:
    title = book.h3.a["title"]
    price = book.find("p", class_="price_color").text
    
    data.append({
        "title": title,
        "price": price
    })

df = pd.DataFrame(data)
print(df.head())

df.to_csv("books.csv", index=False)
