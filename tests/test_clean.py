"""clean_redfin: renaming, coercion, de-duplication, ordering."""

from __future__ import annotations

import pandas as pd

from parcel.transform.clean import NUMERIC, REDFIN_MAP, clean_redfin


def raw_row(**overrides: object) -> dict[str, object]:
    """A Redfin row with every source column clean_redfin reads."""
    row: dict[str, object] = {
        "PERIOD_BEGIN": "2026-03-15",
        "PARENT_METRO_REGION_METRO_CODE": "16740",
        "MEDIAN_SALE_PRICE": 400000,
        "MEDIAN_PPSF": 210.5,
        "INVENTORY": 1200,
        "MONTHS_OF_SUPPLY": 2.4,
        "MEDIAN_DOM": 31,
        "AVG_SALE_TO_LIST": 0.987,
        "PRICE_DROPS": 0.14,
        "HOMES_SOLD": 512,
        "NEW_LISTINGS": 680,
        "SOLD_ABOVE_LIST": 0.28,
    }
    row.update(overrides)
    return row


def test_keeps_exactly_the_canonical_columns() -> None:
    out = clean_redfin(pd.DataFrame([raw_row()]))
    assert list(out.columns) == list(REDFIN_MAP.values())


def test_period_begin_is_snapped_to_the_first_of_the_month() -> None:
    # Redfin's PERIOD_BEGIN is a real date; fact_market is monthly, and dim_date
    # is built from month starts, so anything else would not join.
    out = clean_redfin(pd.DataFrame([raw_row(PERIOD_BEGIN="2026-03-15")]))
    assert out["date"][0] == pd.Timestamp("2026-03-01")


def test_region_id_is_string_not_int() -> None:
    # CBSA codes have leading zeros in other metros; reading them as ints would
    # silently drop those, and dim_region joins on the string.
    out = clean_redfin(pd.DataFrame([raw_row()]))
    assert out["region_id"].dtype == "string"


def test_unparseable_numbers_become_na_rather_than_raising() -> None:
    out = clean_redfin(pd.DataFrame([raw_row(MEDIAN_SALE_PRICE="n/a")]))
    assert pd.isna(out["median_sale_price"][0])
    # the rest of the row survives
    assert out["homes_sold"][0] == 512


def test_every_numeric_column_is_numeric() -> None:
    out = clean_redfin(pd.DataFrame([raw_row()]))
    for col in NUMERIC:
        assert pd.api.types.is_numeric_dtype(out[col]), col


def test_one_row_per_region_month_keeping_the_first() -> None:
    # redfin.load_raw already filters to a single PROPERTY_TYPE, so duplicates
    # should not arrive — this pins the defensive behaviour if they ever do.
    dupes = pd.DataFrame(
        [
            raw_row(MEDIAN_SALE_PRICE=400000),
            raw_row(MEDIAN_SALE_PRICE=999999),
        ]
    )
    out = clean_redfin(dupes)
    assert len(out) == 1
    assert out["median_sale_price"][0] == 400000


def test_sorted_by_region_then_date_with_a_reset_index() -> None:
    rows = pd.DataFrame(
        [
            raw_row(PARENT_METRO_REGION_METRO_CODE="99999", PERIOD_BEGIN="2026-01-01"),
            raw_row(PARENT_METRO_REGION_METRO_CODE="16740", PERIOD_BEGIN="2026-02-01"),
            raw_row(PARENT_METRO_REGION_METRO_CODE="16740", PERIOD_BEGIN="2026-01-01"),
        ]
    )
    out = clean_redfin(rows)
    assert out["region_id"].tolist() == ["16740", "16740", "99999"]
    assert out["date"].tolist() == [
        pd.Timestamp("2026-01-01"),
        pd.Timestamp("2026-02-01"),
        pd.Timestamp("2026-01-01"),
    ]
    assert out.index.tolist() == [0, 1, 2]
