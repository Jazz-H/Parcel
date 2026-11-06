"""Clean + standardize the raw Redfin frame into tidy fact_market columns."""

from __future__ import annotations

import pandas as pd

# Redfin source column -> canonical fact_market column.
#
# These are the rebuilt Data Center names, space-separated and carrying their
# units. The old market-tracker names (PERIOD_BEGIN, MEDIAN_PPSF, ...) went
# away with the 2026-11-02 move; see parcel/ingest/redfin.py.
REDFIN_MAP = {
    "PERIOD BEGIN": "date",
    "REGION ID": "region_id",
    "MEDIAN SALE PRICE NSA ($)": "median_sale_price",
    "MEDIAN SALE PRICE PER SQ.FT. ($)": "price_per_sqft",
    "INVENTORY": "inventory",
    "MONTHS OF SUPPLY": "months_of_supply",
    "MEDIAN DAYS ON MARKET (DAYS)": "days_on_market",
    "AVERAGE SALE TO LIST RATIO (%)": "list_to_sale_ratio",
    "PERCENT ACTIVE WITH PRICE DROPS (%)": "price_cut_share",
    "HOMES SOLD": "homes_sold",
    "NEW LISTINGS": "new_listings",
    "SHARE SOLD ABOVE ORIGINAL LIST (%)": "sold_above_list",
}

# Grouped to mirror the schema's logical sections; keep the grouping.
# fmt: off
NUMERIC = [
    "median_sale_price", "price_per_sqft", "inventory", "months_of_supply",
    "days_on_market", "list_to_sale_ratio", "price_cut_share",
    "homes_sold", "new_listings", "sold_above_list",
]
# fmt: on

# The rebuilt Data Center publishes these three as percentages (99.17, 19.57,
# 13.55) where the old market tracker gave fractions (0.9917, 0.1957, 0.1355).
# fact_market, the committed sample and the Power BI measures were all built on
# fractions, so they are divided by 100 here. Mapping them straight through
# would leave the columns 100x out and nothing would complain.
PERCENT_TO_FRACTION = [
    "list_to_sale_ratio",
    "price_cut_share",
    "sold_above_list",
]


def clean_redfin(df: pd.DataFrame) -> pd.DataFrame:
    out = df.rename(columns=REDFIN_MAP)[list(REDFIN_MAP.values())].copy()
    out["date"] = pd.to_datetime(out["date"]).dt.to_period("M").dt.to_timestamp()
    out["region_id"] = out["region_id"].astype("string")
    for col in NUMERIC:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    for col in PERCENT_TO_FRACTION:
        out[col] = out[col] / 100.0
    # one row per region x month. The metro file is already one row per metro
    # per month, so this is a guard rather than a filter — but it is the only
    # thing standing between a duplicated upstream row and a double-counted
    # month, now that there is no PROPERTY_TYPE filter narrowing the input.
    out = out.drop_duplicates(subset=["region_id", "date"]).sort_values(
        ["region_id", "date"]
    )
    return out.reset_index(drop=True)
