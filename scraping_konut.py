import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://www.emlakjet.com/kiralik-konut/istanbul-bahcelievler"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

response = requests.get(url, headers=headers)

print("Status Code:", response.status_code)

soup = BeautifulSoup(response.text, "html.parser")

cards = soup.find_all("div", class_="styles_contentWrapper___jenb")

print("Bulunan ilan sayısı:", len(cards))

data = []

for card in cards:
    title = card.find("h3", class_="styles_title__aKEGQ")
    price = card.find("span", class_="styles_price__F3pMQ")
    location = card.find("span", class_="styles_location__OwJiQ")
    details = card.find("div", class_="styles_quickinfoWrapper__Vsnk5")

    title_text = title.get_text(strip=True) if title else None
    location_text = location.get_text(strip=True) if location else None
    details_text = details.get_text(strip=True) if details else None

    if price:
        price_text = price.get_text(strip=True)
        price_numeric = (
            price_text
            .replace("TL", "")
            .replace(".", "")
            .strip()
        )
        try:
            price_numeric = int(price_numeric)
        except:
            price_numeric = None
    else:
        price_numeric = None

    data.append([title_text, price_numeric, location_text, details_text])


df = pd.DataFrame(data, columns=["Title", "Price", "Location", "Details"])

df.to_csv("ilanlar.csv", index=False, encoding="utf-8-sig")

print("CSV oluşturuldu ")

print("Ortalama Kira:", df["Price"].mean())
print("En Yüksek Kira:", df["Price"].max())
print("En Düşük Kira:", df["Price"].min())
print(df.sort_values("Price", ascending=False).head())
print(df["Price"].median())
df_filtered = df[df["Price"] < 80000]

print("Yeni Ortalama:", df_filtered["Price"].mean())
print("Yeni Median:", df_filtered["Price"].median())
