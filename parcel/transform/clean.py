"""Clean + standardize the raw Redfin frame into tidy fact_market columns."""
from __future__ import annotations

import pandas as pd

# Redfin source column -> canonical fact_market column
REDFIN_MAP = {
    "PERIOD_BEGIN": "date",
    "PARENT_METRO_REGION_METRO_CODE": "region_id",
    "MEDIAN_SALE_PRICE": "median_sale_price",
    "MEDIAN_PPSF": "price_per_sqft",
    "INVENTORY": "inventory",
    "MONTHS_OF_SUPPLY": "months_of_supply",
    "MEDIAN_DOM": "days_on_market",
    "AVG_SALE_TO_LIST": "list_to_sale_ratio",
    "PRICE_DROPS": "price_cut_share",
    "HOMES_SOLD": "homes_sold",
    "NEW_LISTINGS": "new_listings",
    "SOLD_ABOVE_LIST": "sold_above_list",
}

NUMERIC = [
    "median_sale_price", "price_per_sqft", "inventory", "months_of_supply",
    "days_on_market", "list_to_sale_ratio", "price_cut_share",
    "homes_sold", "new_listings", "sold_above_list",
]


def clean_redfin(df: pd.DataFrame) -> pd.DataFrame:
    out = df.rename(columns=REDFIN_MAP)[list(REDFIN_MAP.values())].copy()
    out["date"] = pd.to_datetime(out["date"]).dt.to_period("M").dt.to_timestamp()
    out["region_id"] = out["region_id"].astype("string")
    for col in NUMERIC:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    # one row per region x month
    out = out.drop_duplicates(subset=["region_id", "date"]).sort_values(["region_id", "date"])
    return out.reset_index(drop=True)
