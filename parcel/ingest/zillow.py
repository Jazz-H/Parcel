"""Ingest Zillow Research metro indices: ZHVI (home values) and ZORI (rents).

Zillow publishes wide CSVs (one column per month). We filter to the target metros by
RegionName, melt to long form, and map to our CBSA-based region_id by market name
(Zillow CSVs do not carry CBSA codes).

NOTE: requires the environment network allowlist to include files.zillowstatic.com.
Until then these fetches will fail; run.py degrades gracefully to a price-side load.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from ..config import Config, load_config
from .base import download

ID_COLS = ["RegionID", "SizeRank", "RegionName", "RegionType", "StateName"]


def _name_to_region_id(cfg: Config) -> dict[str, str]:
    """Map Zillow RegionName (e.g. 'Charlotte, NC') -> our region_id (CBSA)."""
    return {m.name: m.region_id for m in cfg.markets}


def _load_wide(url: str, dest: Path, *, force: bool) -> pd.DataFrame:
    path = download(url, dest, force=force)
    return pd.read_csv(path)


def _melt(df: pd.DataFrame, cfg: Config, value_name: str) -> pd.DataFrame:
    name_map = _name_to_region_id(cfg)
    df = df[df["RegionName"].isin(name_map)].copy()
    date_cols = [c for c in df.columns if c not in ID_COLS]
    long = df.melt(
        id_vars=["RegionName"], value_vars=date_cols,
        var_name="date", value_name=value_name,
    )
    long["region_id"] = long["RegionName"].map(name_map)
    long["date"] = pd.to_datetime(long["date"]).dt.to_period("M").dt.to_timestamp()
    return long[["region_id", "date", value_name]].dropna(subset=[value_name])


def load_raw(cfg: Config | None = None, *, force: bool = False) -> pd.DataFrame:
    """Return monthly region_id x date with `zhvi` (home value) and `median_rent` (ZORI)."""
    cfg = cfg or load_config()
    z = cfg.sources["zillow"]
    raw = cfg.path("raw_dir")

    zhvi = _melt(_load_wide(z["zhvi_metro_url"], raw / "zillow_zhvi_metro.csv", force=force),
                 cfg, "zhvi")
    zori = _melt(_load_wide(z["zori_metro_url"], raw / "zillow_zori_metro.csv", force=force),
                 cfg, "median_rent")

    df = zhvi.merge(zori, on=["region_id", "date"], how="outer")
    print(f"[zillow] {len(df):,} rows for {df['region_id'].nunique()} metros")
    return df


if __name__ == "__main__":
    load_raw().to_parquet("data/raw/zillow_targets.parquet")
