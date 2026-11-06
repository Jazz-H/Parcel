"""Ingest Redfin Data Center metro housing-market data.

Redfin rebuilt the Data Center and moved these files from
`redfin_market_tracker/` to `redfin_data_center/` on 2026-11-02 — the same day
the scheduled refresh began failing with AccessDenied on the old path. Three
things changed with the move:

* plain CSV instead of gzipped TSV;
* column names are now space-separated and carry their units, e.g.
  ``MEDIAN SALE PRICE NSA ($)``;
* there is no ``PROPERTY_TYPE`` column, so there is nothing to filter on — the
  metro file is already one row per metro per month.

`price_cut_share` moved to a sibling price-drops file, which carries no
``REGION ID``. It is joined on ``(REGION NAME, PERIOD BEGIN)``; the region
names are byte-identical between the two files.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from ..config import Config, load_config
from .base import download

RAW_NAME = "redfin_metros_monthly.csv"
PRICE_DROPS_NAME = "redfin_price_drops_monthly.csv"

# Grouped to mirror the schema's logical sections; keep the grouping.
# fmt: off
USECOLS = [
    "PERIOD BEGIN", "REGION ID", "REGION TYPE", "REGION NAME",
    "MEDIAN SALE PRICE NSA ($)", "MEDIAN SALE PRICE PER SQ.FT. ($)",
    "HOMES SOLD", "NEW LISTINGS",
    "INVENTORY", "MONTHS OF SUPPLY", "MEDIAN DAYS ON MARKET (DAYS)",
    "AVERAGE SALE TO LIST RATIO (%)", "SHARE SOLD ABOVE ORIGINAL LIST (%)",
]
# The share of active listings that dropped their price — NOT "PRICE DROPS",
# which is a raw count of drops (26, 212, ...) rather than a share.
PRICE_DROPS_USECOLS = [
    "PERIOD BEGIN", "REGION TYPE", "REGION NAME",
    "PERCENT ACTIVE WITH PRICE DROPS (%)",
]
# fmt: on

PRICE_DROP_SHARE = "PERCENT ACTIVE WITH PRICE DROPS (%)"


def fetch(cfg: Config | None = None, *, force: bool = False) -> Path:
    cfg = cfg or load_config()
    url = cfg.sources["redfin"]["metro_url"]
    dest = cfg.path("raw_dir") / RAW_NAME
    return download(url, dest, force=force)


def fetch_price_drops(cfg: Config | None = None, *, force: bool = False) -> Path:
    cfg = cfg or load_config()
    url = cfg.sources["redfin"]["price_drops_url"]
    dest = cfg.path("raw_dir") / PRICE_DROPS_NAME
    return download(url, dest, force=force)


def _read_metros(
    path: Path, usecols: list[str], names: set[str] | None
) -> pd.DataFrame:
    """Read a Data Center metro CSV in chunks, keeping only the rows we need.

    These files are tens of megabytes and cover every US metro, so the filter
    runs per chunk rather than after a full load. ``names`` filters on
    REGION NAME; pass None to keep every metro row.
    """
    frames = []
    reader = pd.read_csv(
        path,
        usecols=usecols,
        dtype={"REGION ID": "string"},
        chunksize=200_000,
        low_memory=False,
    )
    for chunk in reader:
        mask = chunk["REGION TYPE"] == "Metro"
        if names is not None:
            mask &= chunk["REGION NAME"].isin(names)
        if mask.any():
            frames.append(chunk.loc[mask])
    if not frames:
        return pd.DataFrame(columns=usecols)
    return pd.concat(frames, ignore_index=True)


def load_raw(cfg: Config | None = None, *, force: bool = False) -> pd.DataFrame:
    """Return Redfin metro rows for the target markets, price drops joined on."""
    cfg = cfg or load_config()
    codes = cfg.cbsa_codes

    market = _read_metros(fetch(cfg, force=force), USECOLS, names=None)
    market = market.loc[market["REGION ID"].isin(codes)].reset_index(drop=True)
    if market.empty:
        raise RuntimeError(
            "No Redfin rows matched the target CBSAs — check config.markets "
            "against the REGION ID column in the metro file."
        )

    # Only the regions we kept, so the second file is filtered by name rather
    # than loaded in full.
    drops = _read_metros(
        fetch_price_drops(cfg, force=force),
        PRICE_DROPS_USECOLS,
        names=set(market["REGION NAME"].unique()),
    )

    df = market.merge(
        drops.drop(columns=["REGION TYPE"]),
        on=["REGION NAME", "PERIOD BEGIN"],
        how="left",
    )
    matched = int(df[PRICE_DROP_SHARE].notna().sum()) if PRICE_DROP_SHARE in df else 0
    print(
        f"[redfin] {len(df):,} rows for {df['REGION ID'].nunique()} metros "
        f"({matched:,} with price-drop data)"
    )
    return df


if __name__ == "__main__":
    load_raw().to_parquet("data/raw/redfin_targets.parquet")
