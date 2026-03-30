#!/usr/bin/env python3
"""Fetch S&P 500 constituent symbols from Stooq's S&P500 Stocks list and write a candidate universe CSV.

Columns: provider_symbol, symbol, company_name, sector (fixed ``SP500``).

Stooq paginates ~100 names per page (``t/?i=579&v=0&l=<page>``). Session is primed like other Stooq scripts.

Usage:
  python build_sp500_universe_candidates.py [-o sp500_universe_stooq_candidates.csv]
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import requests
from bs4 import BeautifulSoup

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
SECTOR = "SP500"
STOOQ_BASE = "https://stooq.com/t/?i=579&v=0&l={page}"


def provider_to_display_symbol(provider_base: str) -> str:
    """Stooq uses hyphens for class shares (e.g. brk-b); normalize to BRK.B style."""
    return provider_base.upper().replace("-", ".")


def fetch_stooq_sp500_rows(session: requests.Session) -> list[tuple[str, str, str]]:
    """Return list of (provider_symbol, symbol, company_name)."""
    rows: list[tuple[str, str, str]] = []
    seen: set[str] = set()
    page = 1
    while True:
        url = STOOQ_BASE.format(page=page)
        r = session.get(url, timeout=30)
        r.raise_for_status()
        batch = _parse_listing_page(r.text)
        if not batch:
            break
        for ps, sym, name in batch:
            if ps in seen:
                continue
            seen.add(ps)
            rows.append((ps, sym, name))
        if len(batch) < 100:
            break
        page += 1
        if page > 20:
            break
    return rows


def _parse_listing_page(html: str) -> list[tuple[str, str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    out: list[tuple[str, str, str]] = []
    for tr in soup.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) < 2:
            continue
        a = tds[0].find("a", href=True)
        if not a:
            continue
        href = a.get("href", "")
        if "s=" not in href:
            continue
        full = href if href.startswith("http") else "https://stooq.com" + href
        q = parse_qs(urlparse(full).query)
        if "s" not in q:
            continue
        ps = q["s"][0].strip().lower()
        if not ps.endswith(".us"):
            continue
        name = tds[1].get_text(strip=True)
        if not name:
            continue
        base = ps[:-3]
        sym = provider_to_display_symbol(base)
        out.append((ps, sym, name))
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Build S&P 500 Stooq candidate CSV from Stooq listing.")
    ap.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent / "sp500_universe_stooq_candidates.csv",
        help="Output CSV path",
    )
    args = ap.parse_args()

    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    session.get("https://stooq.com/", timeout=15)

    try:
        rows = fetch_stooq_sp500_rows(session)
    except Exception as exc:
        print(f"Failed to fetch Stooq S&P 500 list: {exc}", file=sys.stderr)
        sys.exit(1)

    if not rows:
        print("No symbols parsed from Stooq.", file=sys.stderr)
        sys.exit(1)

    rows.sort(key=lambda x: x[1])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["provider_symbol", "symbol", "company_name", "sector"],
        )
        w.writeheader()
        for ps, sym, name in rows:
            w.writerow(
                {
                    "provider_symbol": ps,
                    "symbol": sym,
                    "company_name": name,
                    "sector": SECTOR,
                }
            )

    print(f"Wrote {len(rows)} rows → {args.output}")


if __name__ == "__main__":
    main()
