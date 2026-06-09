# forex-signal
Forex Signals
import streamlit as st
from twelvedata import TDClient
import pandas as pd

# ================================
# SETTINGS
# ================================

API_KEY = "cac2d68358814abc8583a4616da9ac4d"  # Replace with your API key
td = TDClient(apikey=API_KEY)

symbols = [
    "XAU/USD",
    "EUR/USD",
    "GBP/USD",
    "USD/JPY",
    "AUD/USD",
    "NZD/USD"
]

st.set_page_config(page_title="H1 Forex Signal Scanner", layout="wide")
st.title("H1 Forex Signal Scanner - Twelve Data")

# ================================
# FUNCTION TO GENERATE SIGNALS
# ================================

def fetch_signals():
    results = []
    for symbol in symbols:
        try:
            ts = td.time_series(
                symbol=symbol,
                interval="1h",
                outputsize=300
            )
            df = ts.as_pandas()
            if df.empty or len(df) < 3:
                results.append({"Pair": symbol, "Signal": "No Data", "Entry": "-", "SL": "-", "TP": "-"})
                continue

            df = df.sort_index()
            for col in ["open", "high", "low", "close"]:
                df[col] = pd.to_numeric(df[col])

            c1 = df.iloc[-2]  # Last closed candle
            c2 = df.iloc[-3]  # Previous candle

            signal = "NO TRADE"
            entry = "-"
            sl = "-"
            tp = "-"

            # BUY
            if c1["close"] > c1["open"] and c1["high"] > c2["high"]:
                signal = "BUY"
                entry = round(c1["close"], 5)
                sl = round(c1["low"], 5)
                risk = entry - sl
                tp = round(entry + risk * 2, 5)

            # SELL
            elif c1["close"] < c1["open"] and c1["low"] < c2["low"]:
                signal = "SELL"
                entry = round(c1["close"], 5)
                sl = round(c1["high"], 5)
                risk = sl - entry
                tp = round(entry - risk * 2, 5)

            results.append({
                "Pair": symbol,
                "Signal": signal,
                "Entry": entry,
                "SL": sl,
                "TP": tp
            })

        except Exception as e:
            results.append({"Pair": symbol, "Signal": f"Error: {e}", "Entry": "-", "SL": "-", "TP": "-"})

    return pd.DataFrame(results)

# ================================
# MAIN UI
# ================================

if st.button("Scan Signals"):
    with st.spinner("Fetching live data..."):
        df_signals = fetch_signals()

        # Color coding
        def color_signal(val):
            if val == "BUY":
                return 'background-color: #b6fcb6'  # green
            elif val == "SELL":
                return 'background-color: #fcb6b6'  # red
            elif val == "NO TRADE":
                return 'background-color: #e0e0e0'  # gray
            else:
                return ''

        st.dataframe(df_signals.style.applymap(color_signal, subset=["Signal"]), height=400)

st.info("Press 'Scan Signals' to fetch the latest H1 signals.")
