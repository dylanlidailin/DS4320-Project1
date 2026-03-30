import csv
import os

import pandas as pd


SP500_CSV = "data/sp500_universe_stooq_candidates.csv"
OUT_CSV = "Data/sp500_bulk_report.csv"
BULK_ROOTS = [
    "Data/data/daily/us/nasdaq stocks",
    "Data/data/daily/us/nyse stocks",
]


def main() -> None:
    sp500 = pd.read_csv(SP500_CSV, dtype=str)
    provider_symbols = (
        sp500["provider_symbol"].fillna("").astype(str).str.strip().str.lower().tolist()
    )

    file_map: dict[str, str] = {}
    for root in BULK_ROOTS:
        for dirpath, _dirnames, filenames in os.walk(root):
            for fn in filenames:
                if not fn.endswith(".txt"):
                    continue
                base = fn[:-4].strip().lower()
                if base:
                    file_map[base] = os.path.join(dirpath, fn)

    rows = []
    for ps in provider_symbols:
        path = file_map.get(ps, "")
        found = 1 if path else 0
        size = os.path.getsize(path) if path else 0
        rows.append(
            {
                "provider_symbol": ps,
                "found": found,
                "path": path,
                "bytes": size,
            }
        )

    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["provider_symbol", "found", "path", "bytes"])
        w.writeheader()
        w.writerows(rows)

    found_n = sum(r["found"] for r in rows)
    print(f"Wrote {len(rows)} rows ({found_n} found) -> {OUT_CSV}")


if __name__ == "__main__":
    main()