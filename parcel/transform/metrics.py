"""Derive ETL-side investor metrics and assemble fact_market.

Simple ratios are computed here; time-intelligence (YoY) and the z-score
market-temperature blend are specced as DAX in powerbi/MEASURES.md so the BI layer
controls them. Rent-derived metrics are only populated when Zillow rent is available.
"""
from __future__ import annotations

import pandas as pd


def build_fact_market(
    redfin: pd.DataFrame,
    zillow: pd.DataFrame | None,
    expense_ratio: float = 0.45,
) -> pd.DataFrame:
    df = redfin.copy()

    if zillow is not None and not zillow.empty:
        df = df.merge(zillow, on=["region_id", "date"], how="left")
    else:
        df["median_rent"] = pd.NA
        df["zhvi"] = pd.NA

    rent = pd.to_numeric(df.get("median_rent"), errors="coerce")
    price = pd.to_numeric(df["median_sale_price"], errors="coerce")
    annual_rent = rent * 12

    # Rent-to-price ("1% rule"): monthly rent / sale price
    df["rent_to_price"] = rent / price
    # Gross Rent Multiplier: sale price / annual rent
    df["gross_rent_multiplier"] = price / annual_rent
    # Estimated cap rate: NOI (rent net of expenses) / price
    df["est_cap_rate"] = (annual_rent * (1 - expense_ratio)) / price

    cols = [
        "region_id", "date",
        "median_sale_price", "price_per_sqft", "median_rent",
        "days_on_market", "inventory", "months_of_supply",
        "price_cut_share", "list_to_sale_ratio",
        "rent_to_price", "gross_rent_multiplier", "est_cap_rate",
        "homes_sold", "new_listings", "sold_above_list",
    ]
    for c in cols:
        if c not in df.columns:
            df[c] = pd.NA
    return df[cols].sort_values(["region_id", "date"]).reset_index(drop=True)
