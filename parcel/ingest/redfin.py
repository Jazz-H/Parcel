"""Ingest Redfin Data Center metro market tracker.

Downloads the gzipped TSV, filters early to the target CBSAs and the configured
property type, and returns a tidy raw DataFrame.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from ..config import Config, load_config
from .base import download

RAW_NAME = "redfin_metro_market_tracker.tsv.gz"


def fetch(cfg: Config | None = None, *, force: bool = False) -> Path:
    cfg = cfg or load_config()
    url = cfg.sources["redfin"]["metro_url"]
    dest = cfg.path("raw_dir") / RAW_NAME
    return download(url, dest, force=force)


def load_raw(cfg: Config | None = None, *, force: bool = False) -> pd.DataFrame:
    """Return Redfin metro rows for the target markets only."""
    cfg = cfg or load_config()
    path = fetch(cfg, force=force)
    prop_type = cfg.sources["redfin"]["property_type"]
    codes = cfg.cbsa_codes

    usecols = [
        "PERIOD_BEGIN", "REGION", "STATE_CODE", "PROPERTY_TYPE",
        "MEDIAN_SALE_PRICE", "MEDIAN_PPSF", "HOMES_SOLD", "NEW_LISTINGS",
        "INVENTORY", "MONTHS_OF_SUPPLY", "MEDIAN_DOM", "AVG_SALE_TO_LIST",
        "PRICE_DROPS", "SOLD_ABOVE_LIST",
        "PARENT_METRO_REGION_METRO_CODE", "LAST_UPDATED",
    ]

    frames = []
    reader = pd.read_csv(
        path, sep="\t", compression="gzip", usecols=usecols,
        dtype={"PARENT_METRO_REGION_METRO_CODE": "string"},
        chunksize=200_000, low_memory=False,
    )
    for chunk in reader:
        mask = (chunk["PROPERTY_TYPE"] == prop_type) & (
            chunk["PARENT_METRO_REGION_METRO_CODE"].isin(codes)
        )
        if mask.any():
            frames.append(chunk.loc[mask])

    if not frames:
        raise RuntimeError("No Redfin rows matched the target CBSAs — check config.markets.")
    df = pd.concat(frames, ignore_index=True)
    print(f"[redfin] {len(df):,} rows for {df['PARENT_METRO_REGION_METRO_CODE'].nunique()} metros")
    return df


if __name__ == "__main__":
    load_raw().to_parquet("data/raw/redfin_targets.parquet")
