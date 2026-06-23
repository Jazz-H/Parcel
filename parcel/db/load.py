"""Create the schema and load frames into SQLite. Idempotent."""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

SCHEMA = Path(__file__).resolve().parent / "schema.sql"


def build_dim_date(dates: pd.Series) -> pd.DataFrame:
    rng = pd.date_range(dates.min(), dates.max(), freq="MS")
    d = pd.DataFrame({"date": rng})
    d["year"] = d["date"].dt.year
    d["quarter"] = d["date"].dt.quarter
    d["month"] = d["date"].dt.month
    d["month_name"] = d["date"].dt.strftime("%B")
    d["year_month"] = d["date"].dt.strftime("%Y-%m")
    d["date"] = d["date"].dt.strftime("%Y-%m-%d")
    return d


def load(
    db_path: Path | str,
    fact_market: pd.DataFrame,
    dim_region: pd.DataFrame,
    *,
    sources: int = 1,
) -> None:
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    fm = fact_market.copy()
    fm["date"] = pd.to_datetime(fm["date"]).dt.strftime("%Y-%m-%d")
    dim_date = build_dim_date(pd.to_datetime(fact_market["date"]))

    with sqlite3.connect(db_path) as conn:
        conn.executescript(SCHEMA.read_text())
        dim_region.to_sql("dim_region", conn, if_exists="append", index=False)
        dim_date.to_sql("dim_date", conn, if_exists="append", index=False)
        fm.to_sql("fact_market", conn, if_exists="append", index=False)

        meta = {
            "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "regions_tracked": str(dim_region["region_id"].nunique()),
            "date_min": dim_date["date"].min(),
            "date_max": dim_date["date"].max(),
            "data_sources": str(sources),
            "rows_fact_market": str(len(fm)),
        }
        conn.executemany("INSERT INTO meta(key, value) VALUES (?, ?)", list(meta.items()))
        conn.commit()

    print(f"[load] {db_path} — {len(fm):,} fact rows, {len(dim_region)} regions, "
          f"{len(dim_date)} dates")
