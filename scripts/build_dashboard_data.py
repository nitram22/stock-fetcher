import sqlite3
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
CONFIG = Path(__file__).parent.parent / "config" / "portfolio.json"

DB_PATH = DATA_DIR / "market.db"
DASHBOARD_PATH = DATA_DIR / "dashboard.json"


def load_portfolio():
    with open(CONFIG) as f:
        return json.load(f)


def build_dashboard():

    portfolio_config = load_portfolio()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        ticker,
        price,
        ((price - prev_price) / prev_price) * 100 as change_percent
    FROM (
        SELECT
            ticker,
            price,
            LAG(price) OVER (PARTITION BY ticker ORDER BY timestamp) as prev_price,
            ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY timestamp DESC) as rn
        FROM prices
    )
    WHERE rn = 1
    """)

    rows = cursor.fetchall()
    conn.close()

    rows = [r for r in rows if r[2] is not None]

    # -----------------------
    # Gainers
    # -----------------------

    gainers = [
        {
            "ticker": r[0],
            "price": r[1],
            "change_percent": r[2]
        }
        for r in sorted(
            [r for r in rows if r[2] > 0],
            key=lambda x: x[2],
            reverse=True
        )
    ][:10]

    # -----------------------
    # Losers
    # -----------------------

    losers = [
        {
            "ticker": r[0],
            "price": r[1],
            "change_percent": r[2]
        }
        for r in sorted(
            [r for r in rows if r[2] < 0],
            key=lambda x: x[2]
        )
    ][:10]

    # -----------------------
    # Biggest moves
    # -----------------------

    biggest_moves = [
        {
            "ticker": r[0],
            "price": r[1],
            "change_percent": r[2]
        }
        for r in sorted(
            rows,
            key=lambda x: abs(x[2]),
            reverse=True
        )
    ][:10]

    # -----------------------
    # Portfolio
    # -----------------------

    portfolio = []
    total_value = 0

    for ticker, shares in portfolio_config.items():

        match = next((r for r in rows if r[0] == ticker), None)

        if match:

            price = match[1]
            change = match[2]

            value = price * shares
            total_value += value

            portfolio.append({
                "ticker": ticker,
                "shares": shares,
                "price": price,
                "value": value,
                "change_percent": change
            })

    # -----------------------
    # Dashboard JSON
    # -----------------------

    dashboard = {
        "gainers": gainers,
        "losers": losers,
        "biggest_moves": biggest_moves,
        "portfolio": portfolio,
        "total_value": total_value
    }

    DATA_DIR.mkdir(exist_ok=True)

    with open(DASHBOARD_PATH, "w") as f:
        json.dump(dashboard, f, indent=2)


if __name__ == "__main__":
    build_dashboard()