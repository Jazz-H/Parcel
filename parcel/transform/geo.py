"""Build dim_region from config + the regions actually present in the data.

region_id is the CBSA code (shared across Redfin/Realtor; Zillow joined by name).
Census-sourced attributes (population, income, vacancy) are stretch — left null for now.
"""

from __future__ import annotations

import pandas as pd

from ..config import Config

# Declared explicitly, and in schema.sql order, so an empty result is still a
# frame with the right shape. pd.DataFrame([]) yields (0, 0) with no columns at
# all, and db.load reads dim_region["region_id"], which would then raise a bare
# KeyError. Unreachable today — redfin.load_raw raises first when no CBSA
# matches — but it is defensive code that should fail legibly if it ever runs.
# fmt: off
DIM_REGION_COLUMNS = [
    "region_id", "metro", "city", "state",
    "is_anchor", "population", "median_household_income", "vacancy_rate",
]
# fmt: on


def build_dim_region(cfg: Config, present_ids: set[str]) -> pd.DataFrame:
    rows = []
    for m in cfg.markets:
        if m.region_id not in present_ids:
            continue
        city = m.name.split(",")[0].strip()
        rows.append(
            {
                "region_id": m.region_id,
                "metro": m.name,
                "city": city,
                "state": m.state,
                "is_anchor": bool(m.anchor),
                "population": pd.NA,
                "median_household_income": pd.NA,
                "vacancy_rate": pd.NA,
            }
        )
    return pd.DataFrame(rows, columns=DIM_REGION_COLUMNS)
