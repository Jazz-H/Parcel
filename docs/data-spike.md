# Phase 0 — Data Spike Findings

*Run date: 2026-06-23. Goal: confirm real source fields, grain, and the region join key before writing schema.*

## Network reality in this environment

The remote environment uses an **allowlist network policy**. Reachability tested:

| Source | Host | Status | Notes |
|---|---|---|---|
| **Redfin Data Center** | `redfin-public-data.s3.us-west-2.amazonaws.com` | ✅ 200 | Full market tracker available |
| **Realtor.com Econ Research** | `econdata.s3-us-west-2.amazonaws.com` | ✅ 200 | Core inventory metrics available |
| GitHub | `raw.githubusercontent.com` | ✅ 200 | — |
| **Zillow Research (ZHVI/ZORI)** | `files.zillowstatic.com`, `www.zillow.com` | ❌ 403 `host_not_allowed` | **Blocked** |
| **US Census ACS** | `api.census.gov`, `www2.census.gov` | ❌ 403 | **Blocked** |
| HUD Fair Market Rents | `huduser.gov`, `hudexchange.info` | ❌ 403 | **Blocked** |
| RentCast | `api.rentcast.io` | ❌ 403 | **Blocked** |

**Consequence:** Only **sale-side** market data is reachable. **No rent source is currently
reachable**, which affects the rent-driven metrics (rent-to-price / 1% rule, GRM, cap rate).
See "Open decision" at the bottom.

## Redfin metro tracker — confirmed

- **URL:** `…/redfin_market_tracker/redfin_metro_market_tracker.tsv000.gz` (gzipped TSV)
- **Grain:** one row per **metro × month × property type**. Filter `PROPERTY_TYPE = "All Residential"`.
- **Date range:** monthly, ~2012 → present (`PERIOD_BEGIN`); `LAST_UPDATED` column present.
- **Region key:** `PARENT_METRO_REGION_METRO_CODE` = **CBSA code** (e.g. Charlotte NC = **16740**).
- **Columns that map to `fact_market`:**
  - `PERIOD_BEGIN` → date
  - `MEDIAN_SALE_PRICE`, `MEDIAN_PPSF` → median_sale_price, price_per_sqft
  - `INVENTORY`, `MONTHS_OF_SUPPLY` → inventory, months_of_supply
  - `MEDIAN_DOM` → days_on_market
  - `AVG_SALE_TO_LIST` → list_to_sale_ratio
  - `PRICE_DROPS` → price_cut_share
  - `HOMES_SOLD`, `NEW_LISTINGS`, `PENDING_SALES`, `SOLD_ABOVE_LIST` → useful extras
  - (`*_YOY` columns exist but we'll compute YoY in DAX for control)
- **Region attrs for `dim_region`:** `REGION` (metro name), `STATE_CODE`, metro CBSA code.

## Realtor.com metro core metrics — confirmed

- **URL:** `…/Reports/Core/RDC_Inventory_Core_Metrics_Metro.csv`
- **Grain:** metro × month (`month_date_yyyymm`).
- **Region key:** `cbsa_code` + `cbsa_title` — **same CBSA codes as Redfin**.
- Useful fields: `median_listing_price`, `active_listing_count`, `median_days_on_market`,
  `price_reduced_share`, `pending_ratio`, `median_listing_price_per_square_foot`, `median_square_feet`.
- **Role:** supplementary / cross-check to Redfin (listing-side vs sold-side). Optional for MVP.

## Region join key — RESOLVED

Both Redfin and Realtor.com key on **CBSA code**. This eliminates the brief's biggest risk
(Redfin↔Zillow region mismatch) *for the sale-side sources*. `dim_region.region_id` = CBSA code.
Zillow, when added, also publishes a CBSA/RegionID crosswalk, so it will slot into the same key.

## Target markets → CBSA (anchor + initial targets)

| Metro | CBSA |
|---|---|
| Charlotte, NC | 16740 |
| Raleigh, NC | 39580 |
| Atlanta, GA | 12060 |
| Nashville, TN | 34980 |
| Tampa, FL | 45300 |
| Dallas, TX | 19100 |
| Columbus, OH | 18140 |
| Indianapolis, IN | 26900 |

*(CBSAs to be verified against the live files during ingest.)*

## Open decision (blocks rent metrics) — for the user

No rent source is reachable in this environment. The headline investor metrics that need rent
(rent-to-price / 1% rule, GRM, cap rate) cannot be computed without it. Three paths:

- **A — Broaden the network allowlist** to include Zillow + Census, then build the full metric
  set with automated refresh. (Requires changing the environment's network policy.)
- **B — Ship a price-side MVP now** (appreciation, market temperature, DOM, inventory,
  months-of-supply, sale-to-list, price-cut share — all from Redfin) and defer rent metrics
  to a stretch phase once a rent source is reachable.
- **C — Upload Zillow ZORI/ZHVI CSVs** (downloaded manually from Zillow Research) into
  `data/sample/`; ingest reads them from disk. Rent metrics preserved; refresh of the rent
  side is manual until the network allows Zillow.
