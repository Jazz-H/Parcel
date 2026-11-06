"""build_fact_market: the investor metrics, and the shape of what it returns."""

from __future__ import annotations

import math

import pandas as pd
import pytest

from parcel.transform.metrics import build_fact_market

DATE = pd.Timestamp("2026-03-01")
PRICE = 400_000.0
RENT = 2_000.0


def redfin(price: float = PRICE) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "region_id": ["16740"],
            "date": [DATE],
            "median_sale_price": [price],
            "price_per_sqft": [210.5],
            "days_on_market": [31.0],
            "inventory": [1200.0],
            "months_of_supply": [2.4],
            "price_cut_share": [0.14],
            "list_to_sale_ratio": [0.987],
            "homes_sold": [512.0],
            "new_listings": [680.0],
            "sold_above_list": [0.28],
        }
    )


def zillow(rent: float = RENT) -> pd.DataFrame:
    return pd.DataFrame({"region_id": ["16740"], "date": [DATE], "median_rent": [rent]})


# ---- the three derived metrics ------------------------------------------------


def test_rent_to_price_is_monthly_rent_over_price() -> None:
    # The "1% rule": 2000 / 400000 = 0.005, i.e. 0.5% — half the rule of thumb.
    out = build_fact_market(redfin(), zillow(), 0.45)
    assert out["rent_to_price"][0] == pytest.approx(0.005)


def test_gross_rent_multiplier_is_price_over_annual_rent() -> None:
    # 400000 / (2000 * 12) = 16.67
    out = build_fact_market(redfin(), zillow(), 0.45)
    assert out["gross_rent_multiplier"][0] == pytest.approx(400_000 / 24_000)


def test_est_cap_rate_is_noi_over_price() -> None:
    # NOI = annual rent net of expenses: 24000 * (1 - 0.45) = 13200
    # cap  = 13200 / 400000 = 0.033
    out = build_fact_market(redfin(), zillow(), 0.45)
    assert out["est_cap_rate"][0] == pytest.approx(0.033)


def test_a_higher_expense_ratio_lowers_the_cap_rate() -> None:
    low = build_fact_market(redfin(), zillow(), 0.25)["est_cap_rate"][0]
    high = build_fact_market(redfin(), zillow(), 0.65)["est_cap_rate"][0]
    assert low > high
    # and the ratio is the only thing moving it
    assert low == pytest.approx(24_000 * 0.75 / PRICE)


def test_expense_ratio_does_not_touch_the_rent_ratios() -> None:
    a = build_fact_market(redfin(), zillow(), 0.25)
    b = build_fact_market(redfin(), zillow(), 0.65)
    assert a["rent_to_price"][0] == b["rent_to_price"][0]
    assert a["gross_rent_multiplier"][0] == b["gross_rent_multiplier"][0]


# ---- the no-rent path --------------------------------------------------------


def test_without_zillow_the_rent_metrics_are_null_and_prices_survive() -> None:
    out = build_fact_market(redfin(), None, 0.45)
    for col in (
        "median_rent",
        "rent_to_price",
        "gross_rent_multiplier",
        "est_cap_rate",
    ):
        assert pd.isna(out[col][0]), col
    assert out["median_sale_price"][0] == PRICE
    assert out["days_on_market"][0] == 31.0


def test_an_empty_zillow_frame_behaves_like_no_zillow() -> None:
    out = build_fact_market(redfin(), pd.DataFrame(), 0.45)
    assert pd.isna(out["rent_to_price"][0])
    assert out["median_sale_price"][0] == PRICE


# ---- shape -------------------------------------------------------------------


def test_missing_input_columns_are_filled_rather_than_raising() -> None:
    bare = pd.DataFrame(
        {"region_id": ["16740"], "date": [DATE], "median_sale_price": [PRICE]}
    )
    out = build_fact_market(bare, None, 0.45)
    assert pd.isna(out["inventory"][0])
    assert out["median_sale_price"][0] == PRICE


def test_columns_match_the_fact_market_schema_in_order() -> None:
    # fact_market in parcel/db/schema.sql, minus its PRIMARY KEY line.
    expected = [
        "region_id",
        "date",
        "median_sale_price",
        "price_per_sqft",
        "median_rent",
        "days_on_market",
        "inventory",
        "months_of_supply",
        "price_cut_share",
        "list_to_sale_ratio",
        "rent_to_price",
        "gross_rent_multiplier",
        "est_cap_rate",
        "homes_sold",
        "new_listings",
        "sold_above_list",
    ]
    out = build_fact_market(redfin(), zillow(), 0.45)
    assert list(out.columns) == expected


def test_zhvi_is_not_carried_through_even_if_zillow_supplies_it() -> None:
    # ZHVI ingest was removed in 41c2182; this keeps a stray column from
    # leaking into fact_market if one ever reappears upstream.
    zil = zillow()
    zil["zhvi"] = 350_000.0
    out = build_fact_market(redfin(), zil, 0.45)
    assert "zhvi" not in out.columns


def test_sorted_by_region_then_date() -> None:
    rf = pd.concat(
        [
            redfin().assign(region_id="99999", date=pd.Timestamp("2026-01-01")),
            redfin().assign(region_id="16740", date=pd.Timestamp("2026-02-01")),
            redfin().assign(region_id="16740", date=pd.Timestamp("2026-01-01")),
        ],
        ignore_index=True,
    )
    out = build_fact_market(rf, None, 0.45)
    assert out["region_id"].tolist() == ["16740", "16740", "99999"]
    assert out.index.tolist() == [0, 1, 2]


# ---- edges -------------------------------------------------------------------


def test_a_zero_price_yields_inf_not_an_exception() -> None:
    # Documents current behaviour rather than endorsing it: pandas divides by
    # zero to inf, and inf reaches SQLite and then Power BI. A Redfin median of
    # 0 should not occur, so this is a guard, not a known failure.
    out = build_fact_market(redfin(price=0.0), zillow(), 0.45)
    assert math.isinf(out["rent_to_price"][0])
    assert math.isinf(out["est_cap_rate"][0])


def test_a_zero_rent_yields_an_infinite_grm() -> None:
    out = build_fact_market(redfin(), zillow(rent=0.0), 0.45)
    assert math.isinf(out["gross_rent_multiplier"][0])
    assert out["rent_to_price"][0] == 0.0
