import sqlite3
import json
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB = DATA_DIR / "market.db"
CONFIG = Path(__file__).parent.parent / "config" / "portfolio.json"
OUT = "../data/web_data.json"


def load_portfolio():

    with open(CONFIG) as f:
        return json.load(f)["stocks"]


def main():

    conn = sqlite3.connect(DB)

    df = pd.read_sql("SELECT * FROM prices", conn)

    portfolio = load_portfolio()

    result = {
        "stocks": [],
        "total_value": 0,
        "total_profit": 0
    }

    for stock in portfolio:

        ticker = stock["ticker"]
        shares = stock["shares"]
        buy_price = stock["buy_price"]

        d = df[df["ticker"] == ticker]

        if len(d) < 2:
            continue

        last = d.iloc[-1]
        prev = d.iloc[-2]

        price = last["price"]

        diff = price - prev["price"]

        value = price * shares

        invested = buy_price * shares

        profit = value - invested

        result["total_value"] += value
        result["total_profit"] += profit

        chart = d.tail(60)["price"].tolist()

        result["stocks"].append({

            "ticker": ticker,
            "price": price,
            "high": last["high"],
            "low": last["low"],
            "diff": diff,
            "shares": shares,
            "value": value,
            "profit": profit,
            "chart": chart
        })

    with open(OUT, "w") as f:

        json.dump(result, f, indent=2)


if __name__ == "__main__":
    main()