import sqlite3
import json
from pathlib import Path

BASE = Path(__file__).parent.parent

DATA = BASE / "data"
CONFIG = BASE / "config/portfolio.json"

DB = DATA / "market.db"
OUT = DATA / "dashboard.json"


def build_dashboard():

    with open(CONFIG) as f:
        portfolio = json.load(f)

    conn = sqlite3.connect(DB)

    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        p1.ticker,
        p1.price,
        ((p1.price - p2.price) / p2.price) * 100 as change_percent
    FROM prices p1
    LEFT JOIN prices p2
    ON p1.ticker = p2.ticker
    AND p2.timestamp = (
        SELECT MAX(timestamp)
        FROM prices
        WHERE ticker = p1.ticker
        AND timestamp < p1.timestamp
    )
    WHERE p1.timestamp = (
        SELECT MAX(timestamp)
        FROM prices p3
        WHERE p3.ticker = p1.ticker
    )
    """)

    rows = [r for r in cursor.fetchall() if r[2] is not None]

    conn.close()

    gainers = sorted([r for r in rows if r[2] > 0], key=lambda x: x[2], reverse=True)
    losers = sorted([r for r in rows if r[2] < 0], key=lambda x: x[2])
    biggest = sorted(rows, key=lambda x: abs(x[2]), reverse=True)

    portfolio_table = []
    total_value = 0

    for ticker, price, change in rows:

        shares = portfolio.get(ticker, 0)

        value = shares * price

        total_value += value

        portfolio_table.append({
            "ticker": ticker,
            "shares": shares,
            "price": price,
            "value": value,
            "change_percent": change
        })

    dashboard = {
        "gainers": gainers[:10],
        "losers": losers[:10],
        "biggest_moves": biggest[:10],
        "portfolio": portfolio_table,
        "total_value": total_value
    }

    with open(OUT, "w") as f:
        json.dump(dashboard, f, indent=2)


if __name__ == "__main__":
    build_dashboard()