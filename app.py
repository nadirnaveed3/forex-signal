import streamlit as st
import requests
import pandas as pd

# =========================
# API KEY
# =========================
API_KEY = "cac2d68358814abc8583a4616da9ac4d"

# =========================
# SYMBOLS
# =========================
symbols = ["XAU/USD", "EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "NZD/USD"]

# =========================
# UI
# =========================
st.set_page_config(page_title="Forex Signal Scanner", layout="wide")
st.title("📊 H1 Forex Signal Scanner (Clean Version)")

# =========================
# FETCH DATA
# =========================
def get_data(symbol):
    url = "https://api.twelvedata.com/time_series"

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
    df = df.iloc[::-1]

    for col in ["open", "high", "low", "close"]:
        df[col] = pd.to_numeric(df[col])

    return df

# =========================
# SIGNAL LOGIC
# =========================
def signal(df):
    c1 = df.iloc[-2]
    c2 = df.iloc[-3]

    entry = sl = tp = "-"
    sig = "NO TRADE"

    if c1["close"] > c1["open"] and c1["high"] > c2["high"]:
        sig = "BUY"
        entry = c1["close"]
        sl = c1["low"]
        tp = entry + (entry - sl) * 2

    elif c1["close"] < c1["open"] and c1["low"] < c2["low"]:
        sig = "SELL"
        entry = c1["close"]
        sl = c1["high"]
        tp = entry - (sl - entry) * 2

    return sig, entry, sl, tp

# =========================
# MAIN
# =========================
if st.button("🔄 Scan Signals"):
    results = []

    for s in symbols:
        df = get_data(s)

        if df is None or len(df) < 3:
            results.append([s, "NO DATA", "-", "-", "-"])
            continue

        sig, entry, sl, tp = signal(df)

        results.append([s, sig, entry, sl, tp])

    final = pd.DataFrame(results, columns=["Pair", "Signal", "Entry", "SL", "TP"])

    st.dataframe(final)