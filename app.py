import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import pandas as pd
import numpy as np

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Dashboard Analisis Saham TLKM V2",
    layout="wide"
)

# =========================================================
# PERIOD SELECTOR
# =========================================================

period_option = st.selectbox(

    "Pilih Periode",

    [

        "1 Tahun",
        "6 Bulan",
        "3 Bulan",
        "1 Bulan"

    ]

)

period_map = {

    "1 Tahun":"1y",
    "6 Bulan":"6mo",
    "3 Bulan":"3mo",
    "1 Bulan":"1mo"

}

selected_period = period_map[period_option]

# =========================================================
# LOAD DATA
# =========================================================

def load_data(period):

    df = yf.download(

        'TLKM.JK',

        period=period,

        auto_adjust=True,

        progress=False
    )

    return df

df = load_data(selected_period)

# =========================================================
# FIX DATAFRAME
# =========================================================

if isinstance(df.columns, pd.MultiIndex):

    df.columns = df.columns.get_level_values(0)

df.reset_index(inplace=True)

df.rename(
    columns={df.columns[0]:'Date'},
    inplace=True
)

# =========================================================
# FEATURE ENGINEERING
# =========================================================

# Return saham
df['Return'] = df['Close'].pct_change()

# Moving Average
df['MA7'] = df['Close'].rolling(7).mean()

df['MA30'] = df['Close'].rolling(30).mean()

# Volatility
window_size = min(30, len(df))

df['Volatility'] = (
    df['Return']
    .rolling(window_size)
    .std()
)

# =========================================================
# METRIC ANALYSIS
# =========================================================

# Harga terakhir
last_close = round(
    df['Close'].iloc[-1],
    2
)

# Harga awal periode
first_close = round(
    df['Close'].iloc[0],
    2
)

# Return periode
change_value = round(
    last_close-first_close,
    2
)

pct = round(
    (change_value/first_close)*100,
    2
)

change = f"{change_value} ({pct}%)"

# Total volume
volume = int(df['Volume'].sum())

# Ringkasan harga
open_price = round(
    df['Open'].iloc[0],
    2
)

high_price = round(
    df['High'].max(),
    2
)

low_price = round(
    df['Low'].min(),
    2
)

close_price = round(
    df['Close'].iloc[-1],
    2
)

high52 = round(
    df['High'].max(),
    2
)

low52 = round(
    df['Low'].min(),
    2
)

# Volatility value
if pd.isna(df['Volatility'].iloc[-1]):

    volatility = 0

else:

    volatility = round(
        df['Volatility'].iloc[-1],
        4
    )

# =========================================================
# SIGNAL ANALYSIS
# =========================================================

if df['MA7'].iloc[-1] > df['MA30'].iloc[-1]:

    latest_signal = "BULLISH"

    sentiment_score = 78

else:

    latest_signal = "BEARISH"

    sentiment_score = 25

# =========================================================
# STATISTIK DESKRIPTIF
# =========================================================

mean_return = round(
    df['Return'].mean()*100,
    2
)

max_return = round(
    df['Return'].max()*100,
    2
)

min_return = round(
    df['Return'].min()*100,
    2
)

# =========================================================
# CHART DATA
# =========================================================

labels = (
    df['Date']
    .dt.strftime('%b')
    .tolist()
)

close_data = (
    df['Close']
    .fillna(0)
    .tolist()
)

ma7_data = [
    None if pd.isna(x) else round(x,2)
    for x in df['MA7']
]

ma30_data = [
    None if pd.isna(x) else round(x,2)
    for x in df['MA30']
]

volume_data = (
    df['Volume']
    .fillna(0)
    .tolist()
)

volatility_data = (
    df['Volatility']
    .fillna(0)
    .tolist()
)

# =========================================================
# LOAD HTML TEMPLATE
# =========================================================

with open(
    "template.html",
    "r",
    encoding="utf-8"
) as f:

    html = f.read()

# =========================================================
# REPLACE METRIC
# =========================================================

html = html.replace(
    "{{last_close}}",
    str(last_close)
)

html = html.replace(
    "{{pct}}",
    str(pct)+"%"
)

html = html.replace(
    "{{change}}",
    change
)

html = html.replace(
    "{{volume}}",
    f"{volume:,}"
)

html = html.replace(
    "{{open}}",
    str(open_price)
)

html = html.replace(
    "{{high}}",
    str(high_price)
)

html = html.replace(
    "{{low}}",
    str(low_price)
)

html = html.replace(
    "{{close}}",
    str(close_price)
)

html = html.replace(
    "{{high52}}",
    str(high52)
)

html = html.replace(
    "{{low52}}",
    str(low52)
)

html = html.replace(
    "{{volatility}}",
    str(volatility)
)

html = html.replace(
    "{{signal}}",
    latest_signal
)

html = html.replace(
    "{{sentiment_score}}",
    str(sentiment_score)
)

html = html.replace(
    "{{mean_return}}",
    str(mean_return)
)

html = html.replace(
    "{{max_return}}",
    str(max_return)
)

html = html.replace(
    "{{min_return}}",
    str(min_return)
)

# =========================================================
# REPLACE CHART DATA
# =========================================================

html = html.replace(
    "{{labels}}",
    str(labels)
)

html = html.replace(
    "{{close_data}}",
    str(close_data)
)

html = html.replace(
    "{{ma7_data}}",
    str(ma7_data)
)

html = html.replace(
    "{{ma30_data}}",
    str(ma30_data)
)

html = html.replace(
    "{{volume_data}}",
    str(volume_data)
)

html = html.replace(
    "{{volatility_data}}",
    str(volatility_data)
)

# =========================================================
# DISPLAY DASHBOARD
# =========================================================

components.html(

    html,

    height=1050,

    scrolling=False
)
