"""build_dim_region: which markets appear, and the shape when none do."""

from __future__ import annotations

import pandas as pd

from parcel.config import Config, Market
from parcel.transform.geo import DIM_REGION_COLUMNS, build_dim_region


def cfg() -> Config:
    return Config(
        markets=[
            Market(region_id="16740", name="Charlotte, NC", state="NC", anchor=True),
            Market(region_id="39580", name="Raleigh, NC", state="NC"),
            Market(region_id="12060", name="Atlanta, GA", state="GA"),
        ],
        sources={},
        paths={},
        metrics={},
    )


def test_only_markets_present_in_the_data_are_included() -> None:
    out = build_dim_region(cfg(), {"16740", "12060"})
    assert out["region_id"].tolist() == ["16740", "12060"]


def test_rows_follow_config_order_not_the_order_ids_were_seen() -> None:
    out = build_dim_region(cfg(), {"12060", "16740"})
    assert out["region_id"].tolist() == ["16740", "12060"]


def test_city_is_the_part_before_the_comma() -> None:
    out = build_dim_region(cfg(), {"16740"})
    assert out["city"][0] == "Charlotte"
    assert out["metro"][0] == "Charlotte, NC"


def test_the_anchor_flag_comes_from_config() -> None:
    out = build_dim_region(cfg(), {"16740", "39580"}).set_index("region_id")
    assert bool(out.loc["16740", "is_anchor"]) is True
    assert bool(out.loc["39580", "is_anchor"]) is False


def test_census_attributes_are_null_until_that_stretch_lands() -> None:
    out = build_dim_region(cfg(), {"16740"})
    for col in ("population", "median_household_income", "vacancy_rate"):
        assert pd.isna(out[col][0]), col


def test_an_id_not_in_config_is_ignored_rather_than_invented() -> None:
    out = build_dim_region(cfg(), {"16740", "00000"})
    assert out["region_id"].tolist() == ["16740"]


def test_no_matching_regions_still_returns_the_right_columns() -> None:
    # Regression guard. pd.DataFrame([]) is (0, 0) with no columns, and
    # db.load reads dim_region["region_id"] — which raised a bare KeyError.
    out = build_dim_region(cfg(), set())
    assert out.empty
    assert list(out.columns) == DIM_REGION_COLUMNS
    assert out["region_id"].nunique() == 0


def test_columns_are_declared_in_schema_order() -> None:
    out = build_dim_region(cfg(), {"16740"})
    assert list(out.columns) == DIM_REGION_COLUMNS
