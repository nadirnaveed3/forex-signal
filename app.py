import streamlit as st
import requests
import pandas as pd

API_KEY = "YOUR_TWELVEDATA_API_KEY"

symbols = [
    "XAU/USD",
    "EUR/USD",
    "GBP/USD",
    "USD/JPY",
    "AUD/USD",
    "NZD/USD"
]

st.set_page_config(page_title="Forex Signal Scanner", layout="wide")
st.title("📊 H1 Forex Signal Scanner (Stable Version)")

# ================================
# FETCH DATA FROM TWELVE DATA API
# ================================

def get_data(symbol):
    url = f"https://api.twelvedata.com/time_series"
    params = {
        "symbol": symbol,
        "interval": "1h",
        "outputsize": 100,
        "apikey": API_KEY
    }

    r = requests.get(url, params=params)
    data = r.json()

    if "values" not in data:
        return None

    df = pd.DataFrame(data["values"])
    df = df.iloc[::-1]  # reverse order

    for col in ["open", "high", "low", "close"]:
        df[col] = pd.to_numeric(df[col])

    return df


# ================================
# SIGNAL LOGIC
# ================================

def signal_logic(df):
    c1 = df.iloc[-2]
    c2 = df.iloc[-3]

    signal = "NO TRADE"
    entry = sl = tp = "-"

    if c1["close"] > c1["open"] and c1["high"] > c2["high"]:
        signal = "BUY"
        entry = c1["close"]
        sl = c1["low"]
        tp = entry + (entry - sl) * 2

    elif c1["close"] < c1["open"] and c1["low"] < c2["low"]:
        signal = "SELL"
        entry = c1["close"]
        sl = c1["high"]
        tp = entry - (sl - entry) * 2

    return signal, entry, sl, tp


# ================================
# MAIN APP
# ================================

if st.button("🔄 Scan Signals"):
    results = []

    for symbol in symbols:
        df = get_data(symbol)

        if df is None or len(df) < 3:
            results.append([symbol, "NO DATA", "-", "-", "-"])
            continue

        signal, entry, sl, tp = signal_logic(df)

        results.append([symbol, signal, entry, sl, tp])

    final_df = pd.DataFrame(results, columns=["Pair", "Signal", "Entry", "SL", "TP"])

    st.dataframe(final_df)