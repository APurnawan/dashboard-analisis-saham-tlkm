import streamlit as st
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh

import yfinance as yf
import pandas as pd
import numpy as np
import json

from prophet import Prophet

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Dashboard Analisis Saham TLKM",
    layout="wide"
)

# =========================================================
# AUTO REFRESH
# =========================================================

st_autorefresh(
    interval=60000,
    key="refresh"
)

# =========================================================
# TITLE
# =========================================================

st.title("Realtime Dashboard Analisis Saham TLKM")

st.caption(
    "Realtime Market Data • Auto Refresh 1 Menit"
)

# =========================================================
# PERIOD SELECTOR
# =========================================================

period_option = st.selectbox(

    "Pilih Periode",

    [
        "7 Hari",
        "1 Bulan",
        "6 Bulan",
        "1 Tahun",
        "2 Tahun",
        "6 Tahun",
        "10 Tahun",
        "Max"
    ]

)

# =========================================================
# PERIOD MAP
# =========================================================

if period_option == "7 Hari":

    period = "7d"
    interval = "5m"

elif period_option == "1 Bulan":

    period = "1mo"
    interval = "30m"

elif period_option == "6 Bulan":

    period = "6mo"
    interval = "1d"

elif period_option == "1 Tahun":

    period = "1y"
    interval = "1d"

elif period_option == "2 Tahun":

    period = "2y"
    interval = "1d"

elif period_option == "6 Tahun":

    period = "6y"
    interval = "1wk"

elif period_option == "10 Tahun":

    period = "10y"
    interval = "1wk"

else:

    period = "max"
    interval = "1mo"
# =========================================================
# LOAD DATA REALTIME
# =========================================================

with st.spinner("Mengambil data realtime..."):

    df = yf.download(

        "TLKM.JK",

        period=period,

        interval=interval,

        auto_adjust=True,

        progress=False
    )

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
# HANDLE EMPTY DATA
# =========================================================

if len(df) < 30:

    st.error("Data tidak cukup untuk analisis")
    st.stop()

# =========================================================
# FEATURE ENGINEERING
# =========================================================

df['Return'] = df['Close'].pct_change()

df['MA7'] = df['Close'].rolling(7).mean()

df['MA30'] = df['Close'].rolling(30).mean()

df['Volatility'] = (
    df['Return']
    .rolling(30)
    .std()
)

# =========================================================
# RSI
# =========================================================

delta = df['Close'].diff()

gain = (
    delta
    .where(delta > 0, 0)
)

loss = (
    -delta
    .where(delta < 0, 0)
)

avg_gain = gain.rolling(14).mean()

avg_loss = loss.rolling(14).mean()

rs = avg_gain / avg_loss

df['RSI'] = 100 - (
    100 / (1 + rs)
)

# =========================================================
# MACD
# =========================================================

exp1 = df['Close'].ewm(
    span=12,
    adjust=False
).mean()

exp2 = df['Close'].ewm(
    span=26,
    adjust=False
).mean()

df['MACD'] = exp1 - exp2

df['Signal_Line'] = (
    df['MACD']
    .ewm(span=9, adjust=False)
    .mean()
)

# =========================================================
# LAST DATA
# =========================================================

last_close = round(
    df['Close'].iloc[-1],
    2
)

prev_close = round(
    df['Close'].iloc[-2],
    2
)

change_value = round(
    last_close - prev_close,
    2
)

pct = round(
    (change_value / prev_close) * 100,
    2
)

change = f"{change_value} ({pct}%)"

volume = int(df['Volume'].iloc[-1])

open_price = round(
    df['Open'].iloc[-1],
    2
)

high_price = round(
    df['High'].iloc[-1],
    2
)

low_price = round(
    df['Low'].iloc[-1],
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

# =========================================================
# VOLATILITY
# =========================================================

volatility = round(
    df['Volatility'].iloc[-1],
    4
)

# =========================================================
# SIGNAL ANALYSIS
# =========================================================

latest_rsi = df['RSI'].iloc[-1]

latest_macd = df['MACD'].iloc[-1]

latest_signal_line = df['Signal_Line'].iloc[-1]

if (

    latest_rsi > 50

    and

    latest_macd > latest_signal_line

):

    latest_signal = "BULLISH"

    sentiment_score = 82

else:

    latest_signal = "BEARISH"

    sentiment_score = 34

# =========================================================
# PROPHET FORECAST
# =========================================================

forecast_df = df[['Date', 'Close']].copy()

# rename kolom
forecast_df.columns = ['ds', 'y']

# hapus timezone
forecast_df['ds'] = (
    pd.to_datetime(
        forecast_df['ds']
    ).dt.tz_localize(None)
)

# pastikan numeric
forecast_df['y'] = pd.to_numeric(
    forecast_df['y'],
    errors='coerce'
)

# hapus NaN
forecast_df = forecast_df.dropna()

# reset index
forecast_df = forecast_df.reset_index(drop=True)

# model prophet
model = Prophet(

    daily_seasonality=True,

    yearly_seasonality=True

)

model.fit(forecast_df)

# future dataframe
future = model.make_future_dataframe(
    periods=30
)

forecast = model.predict(future)

forecast_future = forecast.tail(30)
# =========================================================
# CHART DATA
# =========================================================

labels = (

    df['Date']
    .dt.strftime('%d %b %H:%M')
    .tolist()

)

close_data = (
    df['Close']
    .fillna(0)
    .round(2)
    .tolist()
)

ma7_data = [

    None if pd.isna(x)
    else round(x,2)

    for x in df['MA7']
]

ma30_data = [

    None if pd.isna(x)
    else round(x,2)

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
    .round(4)
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
    f"Rp {last_close:,.0f}"
)

html = html.replace(
    "{{pct}}",
    f"{pct}%"
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

# =========================================================
# REPLACE CHART DATA
# =========================================================

html = html.replace(
    "{{labels}}",
    json.dumps(labels)
)

html = html.replace(
    "{{close_data}}",
    json.dumps(close_data)
)

html = html.replace(
    "{{ma7_data}}",
    json.dumps(ma7_data)
)

html = html.replace(
    "{{ma30_data}}",
    json.dumps(ma30_data)
)

html = html.replace(
    "{{volume_data}}",
    json.dumps(volume_data)
)

html = html.replace(
    "{{volatility_data}}",
    json.dumps(volatility_data)
)

html = html.replace(
    "{{forecast_labels}}",
    json.dumps(forecast_labels)
)

html = html.replace(
    "{{forecast_data}}",
    json.dumps(forecast_values)
)

# =========================================================
# DISPLAY DASHBOARD
# =========================================================

components.html(

    html,

    height=1200,

    scrolling=True

)

# =========================================================
# FOOTER
# =========================================================

st.caption(

    f"""
    Last Update :
    {df['Date'].iloc[-1]}

    | Data Source :
    Yahoo Finance

    | Interval :
    {interval}
    """

)
