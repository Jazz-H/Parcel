# Parcel

> An end-to-end real-estate **market-analytics** pipeline that turns official public
> housing data into a single view of *where to buy and whether now is the time* — for a
> buy-and-hold investor.

Parcel ingests officially published housing datasets (no scraping), models them into a
SQLite **star schema**, derives investor metrics, and presents them in **Power BI**. It
answers three investor decisions: **market selection** (where to look), **timing** (is a
market heating or cooling), and — as a stretch — **deal context** for individual listings.

**Scope:** focused markets — Charlotte, NC (anchor) plus a configurable set of Sun-Belt
buy-and-hold metros (Raleigh, Atlanta, Nashville, Tampa, Dallas, Columbus, Indianapolis).

## Architecture

```mermaid
flowchart TD
    A[Redfin Data Center<br/>metro market tracker] -->|requests + pandas| C
    B[Zillow Research<br/>ZORI rents] -->|requests + pandas| C
    C[Transform<br/>clean · geo-normalize CBSA · derive metrics] --> D[(SQLite star schema)]
    D --> E[Power BI<br/>Power Query + DAX]
    E --> F[Dashboard → Publish to web]
    G[GitHub Actions<br/>scheduled refresh] -.-> C
```

**Data model (star schema):** `fact_market` (region × month metrics) → `dim_region`
(CBSA-keyed metros) and `dim_date` (time-intelligence). `fact_listing` is reserved for the
stretch deal screener. See `parcel/db/schema.sql`.

## Data sources (official, published — no scraping)

| Source | Provides | Status in this build |
|---|---|---|
| [Redfin Data Center](https://www.redfin.com/news/data-center/) | sale price, price/sqft, DOM, inventory, months-of-supply, sale-to-list, price-drops | ✅ live |
| [Zillow Research](https://www.zillow.com/research/data/) (ZORI) | **rents** (rent-to-price, GRM, cap rate) | ⏳ pending network allowlist |
| [Realtor.com Econ Research](https://www.realtor.com/research/data/) | listing-side cross-check | optional |
| US Census ACS | income / vacancy enrichment | stretch |

> Both Redfin and Realtor.com key regions on **CBSA code**, so `dim_region.region_id` =
> CBSA — a clean, durable join key.

## Quick start

```bash
make install        # pip install -r requirements.txt
make refresh        # ingest -> transform -> load -> stamp last_updated
```

This builds `db/parcel.sqlite`. A small prebuilt sample lives at
`data/sample/parcel_sample.sqlite` so the Power BI report can be assembled without
re-downloading sources.

## Power BI

The pipeline produces the SQLite database; the report is assembled from
[`powerbi/MEASURES.md`](powerbi/MEASURES.md), which specs every DAX measure, the table
relationships, and a view-by-view layout. MVP views: **Market Ranking**, **Market Detail**,
and a **KPI header**.

## Status

- ✅ Repo scaffold, config, ingest (Redfin + Zillow modules), transform, star schema, loader, one-command refresh
- ✅ Reproducible price-side database (2012 → present, 8 metros) + committed sample
- ✅ Rent metrics (rent-to-price / GRM / cap rate), from Zillow ZORI — populated on
  1,128 of 1,416 rows; ZORI's history starts later than Redfin's, so earlier months
  are null by nature rather than by failure
- ✅ Scheduled GitHub Actions refresh (`.github/workflows/refresh.yml`) — ran weekly
  from Aug 2026 and committed the regenerated sample each Monday
- ◻️ Power BI `MEASURES.md` spec + report assembly (next)
- ◻️ Stretch: Census enrichment, deal screener

### Redfin Data Center move, 2 Nov 2026

Redfin rebuilt the Data Center and moved these files from
`redfin_market_tracker/` to `redfin_data_center/`. The old path now returns
`AccessDenied`, which is why the scheduled refresh failed on 2 Nov — the new
file's `Last-Modified` is that same day, so the cutover and the breakage were
the same event.

Migrated on 2026-11-06. Three things changed with the move: plain CSV instead
of gzipped TSV, column names that are space-separated and carry their units
(`MEDIAN SALE PRICE NSA ($)`), and no `PROPERTY_TYPE` column to filter on —
the metro file is already one row per metro per month. `price_cut_share` moved
to a sibling price-drops file carrying no `REGION ID`, so it joins on
`(REGION NAME, PERIOD BEGIN)`.

One conversion worth knowing about: the rebuilt feed publishes
`list_to_sale_ratio`, `price_cut_share` and `sold_above_list` as **percentages**
(99.17) where the old tracker gave **fractions** (0.9917). `fact_market`, the
committed sample and the Power BI measures are all built on fractions, so
`clean_redfin` divides those three by 100. Mapping them straight through would
leave the columns 100x out and nothing would have complained.

See [`PLAN.md`](PLAN.md) for the full phased plan and [`docs/data-spike.md`](docs/data-spike.md)
for the source-field findings.

## Repo layout

```
parcel/        # python package: ingest/ transform/ db/ config.py run.py
data/sample/   # committed sample DB + CSV exports (reproducible without network)
db/            # built parcel.sqlite (gitignored; sample committed)
powerbi/       # MEASURES.md (DAX, relationships, wireframes)
docs/          # data-spike findings, architecture notes
config.yml     # target markets + source URLs
```
