"""clean_redfin: renaming, unit conversion, coercion, de-duplication, ordering."""

from __future__ import annotations

import pandas as pd

from parcel.transform.clean import (
    NUMERIC,
    PERCENT_TO_FRACTION,
    REDFIN_MAP,
    clean_redfin,
)


def raw_row(**overrides: object) -> dict[str, object]:
    """A Data Center metro row with every source column clean_redfin reads.

    Column names and value formats are taken from the real file: space
    separated, units in the name, and the three share fields published as
    percentages rather than fractions.
    """
    row: dict[str, object] = {
        "PERIOD BEGIN": "2026-03-01",
        "REGION ID": "16740",
        "MEDIAN SALE PRICE NSA ($)": 400000,
        "MEDIAN SALE PRICE PER SQ.FT. ($)": 210.5,
        "INVENTORY": 1200,
        "MONTHS OF SUPPLY": 2.4,
        "MEDIAN DAYS ON MARKET (DAYS)": 31,
        "AVERAGE SALE TO LIST RATIO (%)": 98.7,
        "PERCENT ACTIVE WITH PRICE DROPS (%)": 14.0,
        "HOMES SOLD": 512,
        "NEW LISTINGS": 680,
        "SHARE SOLD ABOVE ORIGINAL LIST (%)": 28.0,
    }
    row.update(overrides)
    return row


def test_keeps_exactly_the_canonical_columns() -> None:
    out = clean_redfin(pd.DataFrame([raw_row()]))
    assert list(out.columns) == list(REDFIN_MAP.values())


# ---- the unit conversion introduced with the Data Center move ----------------


def test_percentage_fields_are_converted_to_fractions() -> None:
    # The rebuilt Data Center publishes these as percentages; fact_market, the
    # committed sample and the Power BI measures are all built on fractions.
    # Mapping them straight through would leave the columns 100x out.
    out = clean_redfin(pd.DataFrame([raw_row()]))
    assert out["list_to_sale_ratio"][0] == 0.987
    assert out["price_cut_share"][0] == 0.14
    assert out["sold_above_list"][0] == 0.28


def test_the_converted_fields_are_exactly_the_percentage_ones() -> None:
    # Guards against a future column being added to one list and not the other.
    assert set(PERCENT_TO_FRACTION) <= set(NUMERIC)
    assert set(PERCENT_TO_FRACTION) == {
        "list_to_sale_ratio",
        "price_cut_share",
        "sold_above_list",
    }


def test_absolute_fields_are_not_rescaled() -> None:
    out = clean_redfin(pd.DataFrame([raw_row()]))
    assert out["median_sale_price"][0] == 400000
    assert out["price_per_sqft"][0] == 210.5
    assert out["months_of_supply"][0] == 2.4
    assert out["days_on_market"][0] == 31
    assert out["homes_sold"][0] == 512


def test_a_missing_percentage_stays_missing_rather_than_becoming_zero() -> None:
    # The price-drops file has a shorter history than the market file, so this
    # column is legitimately null for older months. Dividing None by 100 must
    # not turn it into 0.0, which would read as "no price cuts".
    out = clean_redfin(
        pd.DataFrame([raw_row(**{"PERCENT ACTIVE WITH PRICE DROPS (%)": None})])
    )
    assert pd.isna(out["price_cut_share"][0])


def test_upstream_negative_price_drop_shares_pass_through() -> None:
    # Redfin's own file carries 276 negative values for this field. They are
    # upstream data, not a transform bug, and clamping them here would hide it.
    out = clean_redfin(
        pd.DataFrame([raw_row(**{"PERCENT ACTIVE WITH PRICE DROPS (%)": -0.21})])
    )
    assert out["price_cut_share"][0] == -0.0021


# ---- coercion and shape -----------------------------------------------------


def test_period_begin_is_snapped_to_the_first_of_the_month() -> None:
    # The Data Center already publishes month starts, so this is a guard. It
    # matters because dim_date is built from month starts and anything else
    # would not join.
    out = clean_redfin(pd.DataFrame([raw_row(**{"PERIOD BEGIN": "2026-03-15"})]))
    assert out["date"][0] == pd.Timestamp("2026-03-01")


def test_region_id_is_string_not_int() -> None:
    # CBSA codes have leading zeros in other metros; reading them as ints would
    # silently drop those, and dim_region joins on the string.
    out = clean_redfin(pd.DataFrame([raw_row()]))
    assert out["region_id"].dtype == "string"


def test_unparseable_numbers_become_na_rather_than_raising() -> None:
    # The real files use the string "NA" for missing values.
    out = clean_redfin(pd.DataFrame([raw_row(**{"MEDIAN SALE PRICE NSA ($)": "NA"})]))
    assert pd.isna(out["median_sale_price"][0])
    # the rest of the row survives
    assert out["homes_sold"][0] == 512


def test_every_numeric_column_is_numeric() -> None:
    out = clean_redfin(pd.DataFrame([raw_row()]))
    for col in NUMERIC:
        assert pd.api.types.is_numeric_dtype(out[col]), col


def test_one_row_per_region_month_keeping_the_first() -> None:
    # Load-bearing since the Data Center move: the old ingest filtered to a
    # single PROPERTY_TYPE, and that column no longer exists, so this is the
    # only thing between a duplicated upstream row and a double-counted month.
    dupes = pd.DataFrame(
        [
            raw_row(**{"MEDIAN SALE PRICE NSA ($)": 400000}),
            raw_row(**{"MEDIAN SALE PRICE NSA ($)": 999999}),
        ]
    )
    out = clean_redfin(dupes)
    assert len(out) == 1
    assert out["median_sale_price"][0] == 400000


def test_sorted_by_region_then_date_with_a_reset_index() -> None:
    rows = pd.DataFrame(
        [
            raw_row(**{"REGION ID": "99999", "PERIOD BEGIN": "2026-01-01"}),
            raw_row(**{"REGION ID": "16740", "PERIOD BEGIN": "2026-02-01"}),
            raw_row(**{"REGION ID": "16740", "PERIOD BEGIN": "2026-01-01"}),
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
