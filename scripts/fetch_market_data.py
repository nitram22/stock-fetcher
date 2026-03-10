import sqlite3
import json
import os
import http.client
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).parent.parent

CONFIG = BASE / "config/portfolio.json"
DATA = BASE / "data"
DB = DATA / "market.db"

DATA.mkdir(exist_ok=True)

API_KEY = os.environ["RAPIDAPI_KEY"]

def load_tickers():
    with open(CONFIG) as f:
        portfolio = json.load(f)
    return list(portfolio.keys())


def init_db():

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

    conn.close()


def fetch_prices():

    tickers = load_tickers()

    symbols = ",".join(tickers)

    conn_http = http.client.HTTPSConnection("yahoo-finance166.p.rapidapi.com")

    headers = {
        'x-rapidapi-key': API_KEY,
        'x-rapidapi-host': "yahoo-finance166.p.rapidapi.com"
    }

    endpoint = f"/api/market/get-quote?symbols={symbols}"

    conn_http.request("GET", endpoint, headers=headers)

    res = conn_http.getresponse()

    data = json.loads(res.read().decode())

    rows = []

    ts = datetime.utcnow().isoformat()

    for q in data["quoteResponse"]["result"]:

        rows.append((
            ts,
            q["symbol"],
            q.get("regularMarketPrice"),
            q.get("regularMarketDayHigh"),
            q.get("regularMarketDayLow"),
            q.get("regularMarketOpen")
        ))

    db = sqlite3.connect(DB)

    db.executemany(
        "INSERT INTO prices VALUES (?,?,?,?,?,?)",
        rows
    )

    db.commit()
    db.close()


if __name__ == "__main__":
    init_db()
    fetch_prices()