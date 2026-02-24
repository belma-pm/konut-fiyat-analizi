import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import re

st.set_page_config(page_title="İlçe Kira Dashboard", layout="wide")

st.title("🏙 İstanbul İlçe Kira Karşılaştırma Dashboard")

# ---------------------------------------
# VERİ YÜKLEME
# ---------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("ilanlar_multi_ilce.csv")
    return df

df = load_data()

# ---------------------------------------
# OUTLIER TEMİZLEME (GLOBAL IQR)
# ---------------------------------------
Q1 = df["Price"].quantile(0.25)
Q3 = df["Price"].quantile(0.75)
IQR = Q3 - Q1

lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR

df = df[(df["Price"] >= lower) & (df["Price"] <= upper)]

# ---------------------------------------
# m² PARSE
# ---------------------------------------
def extract_m2(detail):
    if pd.isna(detail):
        return None
    match = re.search(r'(\d+)\s*(?:m²|m2)', detail)
    if match:
        return int(match.group(1))
    return None

df["m2"] = df["Details"].apply(extract_m2)
df = df[df["m2"].notna()]
df["price_per_m2"] = df["Price"] / df["m2"]

# ---------------------------------------
# SIDEBAR FİLTRE
# ---------------------------------------
st.sidebar.header("Filtreler")

selected_districts = st.sidebar.multiselect(
    "İlçe Seç",
    options=df["District"].unique(),
    default=df["District"].unique()
)

df_filtered = df[df["District"].isin(selected_districts)]

# ---------------------------------------
# KPI METRİKLER
# ---------------------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Toplam İlan", len(df_filtered))
col2.metric("Ortalama Kira", f"{int(df_filtered['Price'].mean()):,} TL")
col3.metric("Median Kira", f"{int(df_filtered['Price'].median()):,} TL")
col4.metric("Ortalama m² Fiyat", f"{int(df_filtered['price_per_m2'].mean())} TL")

# ---------------------------------------
# İLÇE BAZLI ANALİZ TABLOSU
# ---------------------------------------
st.subheader("İlçe Bazlı Ortalama Kira")

district_stats = (
    df_filtered
    .groupby("District")["Price"]
    .mean()
    .sort_values(ascending=False)
)

st.dataframe(district_stats)

# ---------------------------------------
# BAR CHART
# ---------------------------------------
st.subheader("İlçe Bazlı Ortalama Kira Grafiği")

fig = plt.figure()
district_stats.plot(kind="bar")
plt.ylabel("Ortalama Kira")
plt.xticks(rotation=45)
plt.tight_layout()

st.pyplot(fig)

# ---------------------------------------
# m² BAŞINA KİRA GRAFİĞİ
# ---------------------------------------
st.subheader("İlçe Bazlı m² Başına Kira")

m2_stats = (
    df_filtered
    .groupby("District")["price_per_m2"]
    .mean()
    .sort_values(ascending=False)
)

fig2 = plt.figure()
m2_stats.plot(kind="bar")
plt.ylabel("Ortalama m² Fiyat")
plt.xticks(rotation=45)
plt.tight_layout()

st.pyplot(fig2)
