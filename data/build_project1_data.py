import io
from pathlib import Path

import pandas as pd
import requests


OUT_DIR = Path(__file__).resolve().parent
SYMBOLS = ["meta.us", "aapl.us", "amzn.us", "nflx.us", "googl.us"]
NAME_MAP = {
    "meta.us": ("META", "Meta Platforms", "Communication Services"),
    "aapl.us": ("AAPL", "Apple", "Technology"),
    "amzn.us": ("AMZN", "Amazon", "Consumer Discretionary"),
    "nflx.us": ("NFLX", "Netflix", "Communication Services"),
    "googl.us": ("GOOGL", "Alphabet", "Communication Services"),
}
START_DATE = pd.Timestamp("2019-01-01")
END_DATE = pd.Timestamp("2024-12-31")


def download_stooq_daily_csv(provider_symbol: str) -> pd.DataFrame:
    url = f"https://stooq.com/q/d/l/?s={provider_symbol}&i=d"
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    df = pd.read_csv(io.StringIO(response.text))
    if df.empty:
        raise RuntimeError(f"No rows returned for {provider_symbol}")
    return df


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    tickers = pd.DataFrame(
        [
            {
                "ticker_id": i + 1,
                "symbol": NAME_MAP[s][0],
                "provider_symbol": s,
                "company_name": NAME_MAP[s][1],
                "sector": NAME_MAP[s][2],
            }
            for i, s in enumerate(SYMBOLS)
        ]
    )
    ticker_id_by_provider_symbol = dict(
        zip(tickers["provider_symbol"], tickers["ticker_id"])
    )

    price_frames = []
    for provider_symbol in SYMBOLS:
        raw = download_stooq_daily_csv(provider_symbol)
        columns = {c.lower(): c for c in raw.columns}
        required = ["date", "open", "high", "low", "close", "volume"]
        missing = [col for col in required if col not in columns]
        if missing:
            raise RuntimeError(
                f"{provider_symbol} missing columns {missing}; got {list(raw.columns)}"
            )

        prices = raw[
            [
                columns["date"],
                columns["open"],
                columns["high"],
                columns["low"],
                columns["close"],
                columns["volume"],
            ]
        ].copy()
        prices.columns = [
            "trade_date",
            "open_price",
            "high_price",
            "low_price",
            "close_price",
            "volume",
        ]
        prices["trade_date"] = pd.to_datetime(prices["trade_date"])
        prices = prices[
            (prices["trade_date"] >= START_DATE) & (prices["trade_date"] <= END_DATE)
        ].copy()
        prices["adj_close_price"] = prices["close_price"]
        prices["symbol"] = NAME_MAP[provider_symbol][0]
        prices["ticker_id"] = ticker_id_by_provider_symbol[provider_symbol]
        price_frames.append(prices)

    daily_prices = pd.concat(price_frames, ignore_index=True)
    daily_prices = daily_prices.sort_values(["ticker_id", "trade_date"]).reset_index(
        drop=True
    )
    daily_prices.insert(0, "price_id", range(1, len(daily_prices) + 1))

    daily_features = daily_prices[
        ["price_id", "ticker_id", "trade_date", "adj_close_price", "volume"]
    ].copy()
    daily_features = daily_features.sort_values(["ticker_id", "trade_date"])
    daily_features["return_1d"] = daily_features.groupby("ticker_id")[
        "adj_close_price"
    ].pct_change()
    daily_features["volatility_5d"] = (
        daily_features.groupby("ticker_id")["return_1d"]
        .rolling(5)
        .std()
        .reset_index(level=0, drop=True)
    )
    daily_features["ma_5"] = (
        daily_features.groupby("ticker_id")["adj_close_price"]
        .rolling(5)
        .mean()
        .reset_index(level=0, drop=True)
    )
    daily_features["ma_20"] = (
        daily_features.groupby("ticker_id")["adj_close_price"]
        .rolling(20)
        .mean()
        .reset_index(level=0, drop=True)
    )
    daily_features["ma_5_dev"] = (
        (daily_features["adj_close_price"] - daily_features["ma_5"])
        / daily_features["ma_5"]
    )
    daily_features["ma_20_dev"] = (
        (daily_features["adj_close_price"] - daily_features["ma_20"])
        / daily_features["ma_20"]
    )
    daily_features["volume_pct_change"] = daily_features.groupby("ticker_id")[
        "volume"
    ].pct_change()
    daily_features["target_return_next_day"] = daily_features.groupby("ticker_id")[
        "return_1d"
    ].shift(-1)
    daily_features = daily_features[
        [
            "price_id",
            "ticker_id",
            "trade_date",
            "return_1d",
            "volatility_5d",
            "ma_5",
            "ma_20",
            "ma_5_dev",
            "ma_20_dev",
            "volume_pct_change",
            "target_return_next_day",
        ]
    ]

    calendar = pd.DataFrame({"trade_date": sorted(daily_prices["trade_date"].unique())})
    calendar["trade_date"] = pd.to_datetime(calendar["trade_date"])
    calendar["calendar_id"] = range(1, len(calendar) + 1)
    calendar["year"] = calendar["trade_date"].dt.year
    calendar["month"] = calendar["trade_date"].dt.month
    calendar["day"] = calendar["trade_date"].dt.day
    calendar["day_of_week"] = calendar["trade_date"].dt.day_name()
    calendar["quarter"] = calendar["trade_date"].dt.quarter
    calendar["is_month_end"] = calendar["trade_date"].dt.is_month_end
    calendar = calendar[
        [
            "calendar_id",
            "trade_date",
            "year",
            "month",
            "day",
            "day_of_week",
            "quarter",
            "is_month_end",
        ]
    ]

    tickers.to_csv(OUT_DIR / "tickers.csv", index=False)
    daily_prices.to_csv(OUT_DIR / "daily_prices.csv", index=False)
    daily_features.to_csv(OUT_DIR / "daily_features.csv", index=False)
    calendar.to_csv(OUT_DIR / "calendar.csv", index=False)

    print("Created:")
    for file_name in ["tickers.csv", "daily_prices.csv", "daily_features.csv", "calendar.csv"]:
        path = OUT_DIR / file_name
        row_count = sum(1 for _ in open(path, "r", encoding="utf-8")) - 1
        print(f"- {file_name}: {row_count} rows")


if __name__ == "__main__":
    main()
