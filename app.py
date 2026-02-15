from flask import Flask, request, jsonify
import yfinance as yf
import pandas as pd

app = Flask(__name__)

def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def get_bias(df):
    if df is None or df.empty or len(df) < 60:
        return "Data insufficient"

    close = df["Close"]
    e20 = ema(close, 20).iloc[-1]
    e50 = ema(close, 50).iloc[-1]
    last = close.iloc[-1]

    if last > e20 > e50:
        return "Bullish"
    elif last < e20 < e50:
        return "Bearish"
    else:
        return "Neutral"

@app.route("/analyze")
def analyze():
    symbol = request.args.get("symbol", "").upper()

    if "." not in symbol:
        symbol = symbol + ".NS"

    stock = yf.Ticker(symbol)
    info = stock.info

    intraday = stock.history(period="5d", interval="15m")
    daily = stock.history(period="6mo", interval="1d")
    weekly = stock.history(period="2y", interval="1wk")

    data = {
        "symbol": symbol,
        "fundamentals": {
            "name": info.get("shortName"),
            "sector": info.get("sector"),
            "marketCap": info.get("marketCap"),
            "pe": info.get("trailingPE"),
            "pb": info.get("priceToBook"),
            "roe": info.get("returnOnEquity"),
            "debtToEquity": info.get("debtToEquity"),
        },
        "bias": {
            "intraday": get_bias(intraday),
            "swing": get_bias(daily),
            "positional": get_bias(weekly)
        }
    }

    return jsonify(data)

@app.route("/")
def home():
    return "Running", 200
