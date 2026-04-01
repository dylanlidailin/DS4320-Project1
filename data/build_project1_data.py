"""Build D1 (four relational tables) from Stooq bulk daily files.

Writes CSV and Parquet for each table. Upload generated files to UVA OneDrive (see README).

Requires: pandas, pyarrow, tqdm
"""

from __future__ import annotations

import logging
import sys
import time
from pathlib import Path

import pandas as pd
from tqdm import tqdm

# ---------------------------------------------------------------------------
# Configuration constants
# ---------------------------------------------------------------------------

OUT_DIR = Path(__file__).resolve().parent
UNIVERSE_CSV = OUT_DIR / "sp500_universe_stooq_candidates.csv"
# Separate log so runs do not overwrite ``build_project1_data.log``
LOG_FILE = OUT_DIR / "build_project1_data.log"

# Limiting the data to a specific date range
START_DATE = pd.Timestamp("1995-01-01")
END_DATE = pd.Timestamp("2024-12-31")
MIN_TOTAL_BYTES = 1_000_000_000

SLEEP_SEC = 0.5

# Creating four tables

OUTPUT_TABLES = ("tickers", "daily_prices", "daily_features", "calendar")

# ---------------------------------------------------------------------------
# Logging — rubric: log to file and echo to console
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Bulk input helpers
# ---------------------------------------------------------------------------


PROJECT_ROOT = OUT_DIR.parent
BULK_ROOTS = (
    PROJECT_ROOT / "Data" / "data" / "daily" / "us" / "nasdaq stocks",
    PROJECT_ROOT / "Data" / "data" / "daily" / "us" / "nyse stocks",
)


def build_file_map() -> dict[str, Path]:
    """Map Stooq provider symbol (lowercase stem) to bulk daily .txt path under BULK_ROOTS."""
    m: dict[str, Path] = {}
    for root in BULK_ROOTS:
        for path in root.rglob("*.txt"):
            key = path.stem.strip().lower()
            if key:
                m[key] = path
    return m


def load_bulk_daily(provider_symbol: str, file_map: dict[str, Path]) -> pd.DataFrame:
    """Load one symbol's Stooq daily OHLCV table from disk via file_map; fail if missing or empty."""
    path = file_map.get(provider_symbol.strip().lower())
    # Error handling for missing bulk file
    if not path:
        raise FileNotFoundError("missing bulk file")
    if path.stat().st_size == 0:
        raise ValueError("empty bulk file (0 bytes)")
    df = pd.read_csv(path)
    if df.empty:
        raise ValueError("empty bulk table (0 rows)")
    return df


def main() -> None:
    """Load universe, load bulk daily OHLCV, build D1, write CSV+Parquet.

    Exits with code 1 if the universe file is missing, no price rows are produced,
    or combined output size is below ``MIN_TOTAL_BYTES``.
    """
    logger.info("Starting build_project1_data pipeline")

    if not UNIVERSE_CSV.is_file():
        logger.error("Missing universe file: %s", UNIVERSE_CSV)
        sys.exit(1)

    universe = pd.read_csv(UNIVERSE_CSV, dtype=str)
    for col in ("provider_symbol", "symbol"):
        if col not in universe.columns:
            logger.error("Universe CSV must include column: %s", col)
            sys.exit(1)

    if "company_name" not in universe.columns:
        universe["company_name"] = universe["symbol"]
    if "sector" not in universe.columns:
        universe["sector"] = "Unknown"

    logger.info("Universe loaded: %d symbols", len(universe))
    file_map = build_file_map()
    logger.info("Bulk file map built: %d files", len(file_map))

    price_frames: list[pd.DataFrame] = []
    successful_rows: list[pd.Series] = []
    failed: list[tuple[str, str]] = []

    pbar = tqdm(
        universe.iterrows(),
        total=len(universe),
        desc="Stooq downloads",
        unit="sym",
        smoothing=0.05,
    )
    for _idx, row in pbar:
        provider_symbol = str(row["provider_symbol"]).strip()
        if not provider_symbol:
            continue
        pbar.set_postfix_str(provider_symbol, refresh=False)
        try:
            raw = load_bulk_daily(provider_symbol, file_map)
        except Exception as exc:
            failed.append((provider_symbol, str(exc)))
            logger.info("FAILED %s — %s", provider_symbol, exc)
            time.sleep(SLEEP_SEC)
            continue

        required = ["<PER>", "<DATE>", "<OPEN>", "<HIGH>", "<LOW>", "<CLOSE>", "<VOL>"]
        missing = [c for c in required if c not in raw.columns]
        if missing:
            failed.append((provider_symbol, f"missing columns {missing}"))
            logger.info("SKIPPED %s — missing columns: %s", provider_symbol, missing)
            time.sleep(SLEEP_SEC)
            continue

        raw = raw[raw["<PER>"] == "D"].copy()
        if raw.empty:
            failed.append((provider_symbol, "no daily rows (<PER> != D)"))
            logger.info("SKIPPED %s — no daily rows", provider_symbol)
            time.sleep(SLEEP_SEC)
            continue

        prices = raw[["<DATE>", "<OPEN>", "<HIGH>", "<LOW>", "<CLOSE>", "<VOL>"]].copy()
        prices.columns = [
            "trade_date",
            "open_price",
            "high_price",
            "low_price",
            "close_price",
            "volume",
        ]
        prices["trade_date"] = pd.to_datetime(prices["trade_date"], format="%Y%m%d")
        prices = prices[
            (prices["trade_date"] >= START_DATE) & (prices["trade_date"] <= END_DATE)
        ].copy()
        if prices.empty:
            failed.append((provider_symbol, "no rows in date window"))
            logger.info(
                "SKIPPED %s — no rows in date window %s–%s",
                provider_symbol,
                START_DATE.date(),
                END_DATE.date(),
            )
            time.sleep(SLEEP_SEC)
            continue

        sym = str(row["symbol"]).strip().upper()
        prices["adj_close_price"] = prices["close_price"]
        prices["symbol"] = sym
        price_frames.append(prices)
        successful_rows.append(row)
        logger.info("OK %s — %d rows", provider_symbol, len(prices))
        time.sleep(SLEEP_SEC)

    if not price_frames:
        logger.error("No symbols produced price data — aborting.")
        sys.exit(1)

    tickers = pd.DataFrame(
        [
            {
                "ticker_id": i + 1,
                "symbol": str(r["symbol"]).strip().upper(),
                "provider_symbol": str(r["provider_symbol"]).strip(),
                "company_name": str(r["company_name"]).strip(),
                "sector": str(r["sector"]).strip(),
            }
            for i, r in enumerate(successful_rows)
        ]
    )
    ticker_id_by_provider = dict(zip(tickers["provider_symbol"], tickers["ticker_id"]))

    for frame, r in zip(price_frames, successful_rows):
        frame["ticker_id"] = ticker_id_by_provider[str(r["provider_symbol"]).strip()]

    daily_prices = pd.concat(price_frames, ignore_index=True)
    daily_prices = daily_prices.sort_values(["ticker_id", "trade_date"]).reset_index(
        drop=True
    )
    daily_prices.insert(0, "price_id", range(1, len(daily_prices) + 1))

    # Creating the daily_features table
    daily_features = daily_prices[
        [
            "price_id",
            "ticker_id",
            "trade_date",
            "adj_close_price",
            "close_price",
            "high_price",
            "low_price",
            "volume",
        ]
    ].copy()
    daily_features = daily_features.sort_values(["ticker_id", "trade_date"])
    by_ticker = daily_features.groupby("ticker_id")

    daily_features["return_1d"] = by_ticker["adj_close_price"].pct_change()
    daily_features["return_2d"] = by_ticker["adj_close_price"].pct_change(periods=2)
    daily_features["return_3d"] = by_ticker["adj_close_price"].pct_change(periods=3)
    daily_features["return_5d"] = by_ticker["adj_close_price"].pct_change(periods=5)

    daily_features["hl_range"] = (
        daily_features["high_price"] - daily_features["low_price"]
    ) / daily_features["close_price"]

    daily_features["volatility_5d"] = (
        by_ticker["return_1d"].rolling(5)
        .std()
        .reset_index(level=0, drop=True)
    )
    daily_features["volatility_20d"] = (
        by_ticker["return_1d"].rolling(20)
        .std()
        .reset_index(level=0, drop=True)
    )

    daily_features["ma_5"] = (
        by_ticker["adj_close_price"].rolling(5)
        .mean()
        .reset_index(level=0, drop=True)
    )
    daily_features["ma_20"] = (
        by_ticker["adj_close_price"].rolling(20)
        .mean()
        .reset_index(level=0, drop=True)
    )
    daily_features["ma_50"] = (
        by_ticker["adj_close_price"].rolling(50)
        .mean()
        .reset_index(level=0, drop=True)
    )
    daily_features["ma_200"] = (
        by_ticker["adj_close_price"].rolling(200)
        .mean()
        .reset_index(level=0, drop=True)
    )

    daily_features["momentum_20d"] = daily_features["adj_close_price"] / daily_features[
        "ma_20"
    ] - 1
    # Calculating the deviation of the close price from the moving averages
    daily_features["ma_5_dev"] = (
        daily_features["adj_close_price"] - daily_features["ma_5"]
    ) / daily_features["ma_5"]
    daily_features["ma_20_dev"] = (
        daily_features["adj_close_price"] - daily_features["ma_20"]
    ) / daily_features["ma_20"]
    daily_features["ma_50_dev"] = (
        daily_features["adj_close_price"] - daily_features["ma_50"]
    ) / daily_features["ma_50"]
    daily_features["ma_200_dev"] = (
        daily_features["adj_close_price"] - daily_features["ma_200"]
    ) / daily_features["ma_200"]
    # Calculating the percentage change in volume
    daily_features["volume_pct_change"] = daily_features.groupby("ticker_id")[
        "volume"
    ].pct_change()
    # Calculating the z-score of the volume
    vol_mean_20 = by_ticker["volume"].rolling(20).mean().reset_index(level=0, drop=True)
    vol_std_20 = by_ticker["volume"].rolling(20).std().reset_index(level=0, drop=True)
    daily_features["volume_zscore_20d"] = (daily_features["volume"] - vol_mean_20) / vol_std_20
    # Calculating the target return for the next day
    daily_features["target_return_next_day"] = by_ticker["return_1d"].shift(-1)

    daily_features = daily_features.replace([float("inf"), float("-inf")], pd.NA)
    # Selecting the columns we want to keep
    daily_features = daily_features[
        [
            "price_id",
            "ticker_id",
            "trade_date",
            "return_1d",
            "return_2d",
            "return_3d",
            "return_5d",
            "hl_range",
            "volatility_5d",
            "volatility_20d",
            "ma_5",
            "ma_20",
            "ma_50",
            "ma_200",
            "momentum_20d",
            "ma_5_dev",
            "ma_20_dev",
            "ma_50_dev",
            "ma_200_dev",
            "volume_pct_change",
            "volume_zscore_20d",
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

    for name, df in (
        ("tickers", tickers),
        ("daily_prices", daily_prices),
        ("daily_features", daily_features),
        ("calendar", calendar),
    ):
        csv_path = OUT_DIR / f"{name}.csv"
        pq_path = OUT_DIR / f"{name}.parquet"
        df.to_csv(csv_path, index=False)
        df.to_parquet(pq_path, engine="pyarrow", index=False)
        logger.info(
            "Wrote %s (%d bytes CSV, %d bytes Parquet)",
            name,
            csv_path.stat().st_size,
            pq_path.stat().st_size,
        )

    total = sum(
        (OUT_DIR / f"{base}.{ext}").stat().st_size
        for ext in ("csv", "parquet")
        for base in OUTPUT_TABLES
    )
    logger.info(
        "Total (8 files): %s bytes (%.3f GB)",
        f"{total:,}",
        total / 1e9,
    )
    logger.info("Successful symbols: %d / %d", len(tickers), len(universe))
    if failed:
        logger.info("Failed / skipped symbols: %d (showing up to 15)", len(failed))
        for p, msg in failed[:15]:
            logger.info("  - %s: %s", p, msg[:120])

    if total < MIN_TOTAL_BYTES:
        logger.error(
            "Combined size %d is below %d (1 GB). "
            "Add more symbols or widen the date window.",
            total,
            MIN_TOTAL_BYTES,
        )
        sys.exit(1)

    logger.info("Pipeline complete. Log file: %s", LOG_FILE)


if __name__ == "__main__":
    main()
