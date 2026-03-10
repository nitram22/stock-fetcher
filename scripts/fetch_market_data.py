import http.client
import json
import sqlite3
import os
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB = str(DATA_DIR / "market.db")
CONFIG = Path(__file__).parent.parent / "config" / "portfolio.json"

API_HOST = "yahoo-finance166.p.rapidapi.com"
API_KEY = os.environ["RAPIDAPI_KEY"]


def load_tickers():

    with open(CONFIG) as f:
        data = json.load(f)

    return [s["ticker"] for s in data["stocks"]]


def init_db():
    from pathlib import Path
    import sqlite3

    Path("data").mkdir(parents=True, exist_ok=True)  # <- hier

    conn = sqlite3.connect(DB)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS prices(
        timestamp TEXT,
        ticker TEXT,
        price REAL,
        high REAL,
        low REAL,
        open REAL
    )
    """)
    conn.commit()
    conn.close()


def fetch_prices():

    tickers = load_tickers()
    symbols = ",".join(tickers)
    conn = http.client.HTTPSConnection(API_HOST)

    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": API_HOST
    }

    endpoint = f"/api/market/get-quote?symbols={symbols}"

    conn.request("GET", endpoint, headers=headers)

    res = conn.getresponse()
    data = json.loads(res.read().decode("utf-8"))
    now = datetime.utcnow().isoformat()

    rows = []

    for q in data["quoteResponse"]["result"]:
        rows.append((
            now,
            q.get("symbol", "N/A"),
            q.get("regularMarketPrice") if q.get("regularMarketPrice") is not None else 0,
            q.get("regularMarketDayHigh") if q.get("regularMarketDayHigh") is not None else 0,
            q.get("regularMarketDayLow") if q.get("regularMarketDayLow") is not None else 0,
            q.get("regularMarketOpen") if q.get("regularMarketOpen") is not None else 0
        ))

    db = sqlite3.connect(DB)

    for r in rows:
        print(r, len(r))

    db.executemany(
        "INSERT INTO prices (timestamp, ticker, price, high, low, open) VALUES (?,?,?,?,?,?)",
        rows
    )

    db.commit()
    db.close()


if __name__ == "__main__":

    Path("data").mkdir(exist_ok=True)
    init_db()
    fetch_prices()