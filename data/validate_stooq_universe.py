#!/usr/bin/env python3
"""Validate Stooq symbols from a candidate universe CSV (same fetch pattern as build_project1_data.py).

Usage:
  python validate_stooq_universe.py path/to/candidates.csv -o tech_universe_stooq_validated.csv

Input CSV must have columns: provider_symbol, symbol (optional: company_name, sector).
"""

from __future__ import annotations

import argparse
import csv
import io
import sys
import time

import pandas as pd
import requests

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
SLEEP_SEC = 0.2  # be polite between checks


def prime_session(session: requests.Session) -> None:
    session.get("https://stooq.com/", timeout=(5, 15))


def symbol_has_data(session: requests.Session, provider_symbol: str) -> tuple[bool, str]:
    """Return (ok, reason). ok True if CSV parses with >= 1 row."""
    ps = provider_symbol.strip()
    page_url = f"https://stooq.com/q/d/?s={ps}"
    csv_url = f"https://stooq.com/q/d/l/?s={ps}&i=d"
    try:
        session.get(page_url, timeout=(5, 15))
        r = session.get(csv_url, timeout=(5, 30))
        r.raise_for_status()
        if len(r.text.strip()) == 0:
            return False, "empty body"
        df = pd.read_csv(io.StringIO(r.text))
        if df.empty:
            return False, "empty table (0 rows)"
        return True, f"ok ({len(df)} rows)"
    except Exception as e:
        return False, str(e)[:200]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("input_csv", help="Candidate universe CSV")
    ap.add_argument("-o", "--output", required=True, help="Write validated rows here")
    ap.add_argument("--limit", type=int, default=0, help="Only check first N rows (0=all)")
    args = ap.parse_args()

    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    prime_session(session)

    with open(args.input_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if args.limit:
        rows = rows[: args.limit]

    fieldnames = reader.fieldnames if reader.fieldnames else ["provider_symbol", "symbol"]
    ok_rows: list[dict] = []
    fail: list[tuple[str, str]] = []

    for i, row in enumerate(rows):
        ps = (row.get("provider_symbol") or "").strip()
        if not ps:
            continue
        ok, reason = symbol_has_data(session, ps)
        print(f"[{i+1}/{len(rows)}] {ps}: {reason}", flush=True)
        if ok:
            ok_rows.append(row)
        else:
            fail.append((ps, reason))
        time.sleep(SLEEP_SEC)

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(ok_rows)

    print(f"\nValidated: {len(ok_rows)} / {len(rows)} → {args.output}")
    print(f"Rejected: {len(fail)}")
    if fail[:20]:
        print("Sample rejects:")
        for ps, r in fail[:20]:
            print(f"  {ps}: {r}")


if __name__ == "__main__":
    main()