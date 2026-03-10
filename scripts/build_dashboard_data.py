import sqlite3
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
DB_PATH = DATA_DIR / "market.db"
DASHBOARD_PATH = DATA_DIR / "dashboard.json"


def build_dashboard():

    if not DB_PATH.exists():
        print("Database not found")
        return

    conn = sqlite3.connect(DB_PATH)
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

    rows = cursor.fetchall()
    conn.close()

    rows = [r for r in rows if r[2] is not None]

    rows_sorted = sorted(rows, key=lambda x: x[2], reverse=True)

    gainers = [
        {"ticker": r[0], "last_price": r[1], "change_percent": r[2]}
        for r in rows_sorted[:10]
    ]

    losers = [
        {"ticker": r[0], "last_price": r[1], "change_percent": r[2]}
        for r in sorted(rows_sorted, key=lambda x: x[2])[:10]
    ]

    dashboard = {
        "gainers": gainers,
        "losers": losers
    }

    DATA_DIR.mkdir(exist_ok=True)

    with open(DASHBOARD_PATH, "w") as f:
        json.dump(dashboard, f, indent=2)


if __name__ == "__main__":
    build_dashboard()