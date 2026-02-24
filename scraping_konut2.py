import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

base_url = "https://www.emlakjet.com/kiralik-konut/istanbul-bahcelievler"

headers = {
    "User-Agent": "Mozilla/5.0"
}

all_data = []

for page in range(1, 11):   # ilk 10 sayfa
    print(f"Sayfa çekiliyor: {page}")

    url = f"{base_url}/?page={page}"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print("Hata:", response.status_code)
        continue

    soup = BeautifulSoup(response.text, "html.parser")
    cards = soup.find_all("div", class_="styles_contentWrapper___jenb")

    print("Bulunan ilan:", len(cards))

    for card in cards:
        title = card.select_one("h3[class^='styles_title']")
        price = card.select_one("span[class^='styles_price']")
        location = card.select_one("span[class^='styles_location']")
        details = card.select_one("div[class^='styles_quickinfoWrapper']")

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

        all_data.append([title_text, price_numeric, location_text, details_text])

    time.sleep(1)   # siteyi yormamak için

df = pd.DataFrame(all_data, columns=["Title", "Price", "Location", "Details"])

df.to_csv("ilanlar_tum_sayfalar.csv", index=False, encoding="utf-8-sig")

print("Toplam ilan:", len(df))
print("Tamamlandı ✅")

print("Ortalama:", df["Price"].mean())
print("Median:", df["Price"].median())
print("Min:", df["Price"].min())
print("Max:", df["Price"].max())
print("Skewness:", df["Price"].skew())

Q1 = df["Price"].quantile(0.25)
Q3 = df["Price"].quantile(0.75)
IQR = Q3 - Q1

lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

print("Alt sınır:", lower_bound)
print("Üst sınır:", upper_bound)

df_clean = df[(df["Price"] >= lower_bound) & (df["Price"] <= upper_bound)]

print("Temizlenmiş veri sayısı:", len(df_clean))

print("Yeni Ortalama:", df_clean["Price"].mean())
print("Yeni Median:", df_clean["Price"].median())
print("Yeni Skewness:", df_clean["Price"].skew())
print(df_clean["Location"].head(10))

df_clean["District"] = df_clean["Location"].str.split(" - ").str[0]
district_stats = df_clean.groupby("District")["Price"].agg(["mean", "median", "count"]).sort_values(by="mean", ascending=False)

print(district_stats)



import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# ---------------------------------------------
# 1) İLÇELERİ LİSTE OLARAK VER
# ---------------------------------------------
districts = [
    "bahcelievler",
    "kadikoy",
    "besiktas",
    "sisli",
    "bakirkoy"
]

base = "https://www.emlakjet.com/kiralik-konut/istanbul-{}"

headers = {
    "User-Agent": "Mozilla/5.0"
}

all_data = []

# ---------------------------------------------
# 2) HER İLÇE İÇİN SCRAPING
# ---------------------------------------------
for district in districts:
    print(f"\n--- {district.upper()} için çekiliyor ---")

    for page in range(1, 11):  # 1–10 sayfa
        url = base.format(district) + f"?page={page}"

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print("Hata:", response.status_code, "→", url)
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        cards = soup.find_all("div", class_="styles_contentWrapper___jenb")

        print(f"{district} Sayfa {page} → {len(cards)} ilan")

        for card in cards:
            title = card.select_one("h3[class^='styles_title']")
            price = card.select_one("span[class^='styles_price']")
            location = card.select_one("span[class^='styles_location']")
            details = card.select_one("div[class^='styles_quickinfoWrapper']")

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

            all_data.append([
                district,
                title_text,
                price_numeric,
                location_text,
                details_text
            ])

        time.sleep(1)  # siteye yük bindirmemek için

# ---------------------------------------------
# 3) DATAFRAME & CSV
# ---------------------------------------------
df = pd.DataFrame(
    all_data,
    columns=["District", "Title", "Price", "Location", "Details"]
)

df.to_csv("ilanlar_multi_ilce.csv", index=False, encoding="utf-8-sig")

print("\nToplam ilan sayısı:", len(df))
print("Tamamlandı ✅")

import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------------------
# 1) CSV YÜKLE
# ---------------------------------------
df = pd.read_csv("ilanlar_multi_ilce.csv")

print("Toplam veri:", len(df))

# ---------------------------------------
# 2) GLOBAL IQR OUTLIER TEMİZLEME
# ---------------------------------------
Q1 = df["Price"].quantile(0.25)
Q3 = df["Price"].quantile(0.75)
IQR = Q3 - Q1

lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR

df_clean = df[(df["Price"] >= lower) & (df["Price"] <= upper)]

print("\nTemiz veri:", len(df_clean))
print("Silinen outlier:", len(df) - len(df_clean))

# ---------------------------------------
# 3) GENEL İSTATİSTİKLER
# ---------------------------------------
print("\n--- GENEL İSTATİSTİK ---")
print("Ortalama:", round(df_clean["Price"].mean(), 2))
print("Median:", df_clean["Price"].median())
print("Min:", df_clean["Price"].min())
print("Max:", df_clean["Price"].max())
print("Skewness:", round(df_clean["Price"].skew(), 2))

# ---------------------------------------
# 4) İLÇE BAZLI ANALİZ
# ---------------------------------------
district_stats = (
    df_clean
    .groupby("District")["Price"]
    .agg(["mean", "median", "count"])
    .sort_values(by="mean", ascending=False)
)

print("\n--- İLÇE BAZLI ANALİZ ---")
print(district_stats)

# ---------------------------------------
# 5) EN PAHALI & EN UCUZ İLÇE
# ---------------------------------------
most_expensive = district_stats.index[0]
cheapest = district_stats.index[-1]

print("\nEn pahalı ilçe:", most_expensive)
print("En ucuz ilçe:", cheapest)

# ---------------------------------------
# 6) BAR CHART
# ---------------------------------------
plt.figure()
district_stats["mean"].plot(kind="bar")
plt.title("İlçe Bazlı Ortalama Kira")
plt.xlabel("District")
plt.ylabel("Ortalama Kira")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()


import re

# ---------------------------------------
# 1) m² PARSE ETME
# ---------------------------------------

def extract_m2(detail):
    if pd.isna(detail):
        return None
    
    match = re.search(r'(\d+)\s*m²', detail)
    if match:
        return int(match.group(1))
    return None

df_clean["m2"] = df_clean["Details"].apply(extract_m2)

# m² olmayanları çıkar
df_clean = df_clean[df_clean["m2"].notna()]

print("\nm² bilgisi olan veri:", len(df_clean))

# ---------------------------------------
# 2) m² BAŞINA KİRA HESAPLAMA
# ---------------------------------------

df_clean["price_per_m2"] = df_clean["Price"] / df_clean["m2"]

print("\n--- m² BAŞINA GENEL İSTATİSTİK ---")
print("Ortalama m² kira:", round(df_clean["price_per_m2"].mean(), 2))
print("Median m² kira:", round(df_clean["price_per_m2"].median(), 2))

# ---------------------------------------
# 3) İLÇE BAZLI m² ANALİZ
# ---------------------------------------

m2_stats = (
    df_clean
    .groupby("District")["price_per_m2"]
    .mean()
    .sort_values(ascending=False)
)

print("\n--- İLÇE BAZLI m² BAŞINA KİRA ---")
print(m2_stats)
