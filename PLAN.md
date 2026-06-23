# Parcel — Implementation Plan

> Step-by-step build plan for **Parcel**, an end-to-end real-estate market-analytics
> pipeline for a buy-and-hold investor. Turns official public housing data into a single
> view of *where to buy and whether now is the time*.
>
> Derived from `ParcelBuildBrief v2`. This is the working plan; check off phases as they ship.

---

## Locked decisions

| Decision | Choice | Implication |
|---|---|---|
| **Name** | **Parcel** | — |
| **Medium** | **Power BI** | Claude builds the full Python pipeline + a `MEASURES.md` spec. You assemble the `.pbix` in the Power BI GUI and **Publish to web**. One manual GUI step. |
| **Geographic scope** | **Focused markets** | Charlotte (anchor) + a configurable target list of Sun-Belt buy-and-hold metros. Tighter narrative, smaller data, faster to ship. |
| **Deal Screener (View 4)** | **Stretch (post-MVP)** | Keeps MVP scrape-free and API-key-free. Added later via RentCast/SimplyRETS. |

**Target markets (initial, configurable in `config.yml`):** Charlotte NC (anchor), Raleigh NC,
Atlanta GA, Nashville TN, Tampa FL, Dallas TX, Columbus OH, Indianapolis IN. Easy to add/remove.

---

## Definition of done (MVP)

- [ ] Redfin + Zillow bulk data ingested for the target markets → SQLite star schema
- [ ] Core investor metrics derived in ETL; remaining metrics specced as DAX in `MEASURES.md`
- [ ] One reproducible end-to-end run (`make refresh` or `python -m parcel.run`) with a `last_updated` stamp
- [ ] Committed sample data so the repo runs without network access
- [ ] README with architecture diagram + run instructions
- [ ] `MEASURES.md` complete enough that the Power BI report can be assembled without guesswork
- [ ] Power BI report assembled (by you) covering Views 1–2 + KPI header, Published to web
- [ ] Portfolio entry copy (challenge / approach / outcome + metric cards) drafted

---

## Phase 0 — Data spike & decisions (½ day)

*Goal: confirm the real-world data before writing any schema. The brief's "first move."*

1. Download **one Redfin Data Center** market CSV/TSV (city or metro level) and inspect columns,
   grain, update cadence, and how regions are keyed.
2. Download **one Zillow Research** file each for **ZHVI** (home values) and **ZORI** (rents);
   inspect region keys and the wide (date-as-columns) layout that will need melting.
3. Confirm the join key strategy between Redfin regions and Zillow regions (metro name + state,
   or CBSA/RegionID crosswalk). **This is the riskiest part of the project** — document it.
4. Write findings to `docs/data-spike.md`: available fields, grains, gotchas, chosen join key.

**Exit criteria:** we know exactly which columns feed each fact/dim and how regions reconcile.

---

## Phase 1 — Repo scaffold (½ day)

Set up the structure from brief §12, adapted:

```
parcel/
  parcel/                 # python package
    ingest/               # redfin.py, zillow.py, census.py (stub), base.py
    transform/            # clean.py, geo.py (ZIP<->metro), metrics.py
    db/                   # schema.sql, load.py
    config.py             # loads config.yml (target markets, paths, source URLs)
    run.py                # orchestrates full refresh
  data/
    raw/                  # downloaded source files (gitignored)
    sample/               # small committed sample for reproducibility
  db/
    parcel.sqlite         # built artifact (gitignored; sample committed)
  powerbi/
    MEASURES.md           # every DAX measure + relationships + view wireframes
  docs/
    data-spike.md
    architecture.png      # (or .drawio / mermaid in README)
  .github/workflows/
    refresh.yml           # scheduled refresh (stretch)
  config.yml              # target markets + source config
  requirements.txt
  .env.example
  .gitignore
  README.md
  PLAN.md                 # this file
```

Tasks:
- [ ] `requirements.txt` — `requests`, `pandas`, `pyyaml`, `python-dotenv` (+ `duckdb` optional)
- [ ] `.gitignore` — `data/raw/`, `*.sqlite` (except sample), `.env`, `__pycache__`
- [ ] `.env.example` — placeholders for future API keys (Census, RentCast) — none required for MVP
- [ ] `config.yml` — target market list, source URLs, output paths
- [ ] Package skeleton with empty modules + docstrings

---

## Phase 2 — Ingest layer (1 day)

*Pure download + light validation. No business logic here.*

- [ ] `ingest/base.py` — shared download helper (requests, retries, on-disk caching to `data/raw/`,
      polite headers). Records a per-source `fetched_at` timestamp.
- [ ] `ingest/redfin.py` — pull the relevant Redfin market file(s), filter to target markets early.
- [ ] `ingest/zillow.py` — pull ZHVI + ZORI; filter to target markets.
- [ ] Each ingest module returns a tidy raw DataFrame and writes a cached copy.
- [ ] Generate the committed `data/sample/` slice (a few markets, recent dates) from real pulls.

**Exit criteria:** `python -m parcel.ingest.redfin` and `...zillow` produce cached raw files for the targets.

---

## Phase 3 — Transform layer (1–1.5 days)

*Clean → normalize → derive. This is the ETL the BA story rests on.*

- [ ] `transform/clean.py` — type-cast, parse dates, dedupe, handle nulls, standardize column names.
- [ ] `transform/geo.py` — geo-normalize: reconcile Redfin and Zillow region keys to a single
      `region_id`; build the `dim_region` crosswalk (metro, state; ZIP where available).
- [ ] Melt Zillow wide format (date-as-columns) into long `region_id × date × value`.
- [ ] `transform/metrics.py` — derive ETL-side metrics that aren't time-intelligence:
  - rent-to-price (1% rule) = monthly_rent / sale_price
  - gross rent multiplier = sale_price / annual_rent
  - estimated cap rate = (annual_rent × (1 − expense_ratio)) / sale_price  *(default expense_ratio 0.45)*
  - *(YoY appreciation, market-temperature z-score blend, and what-if-driven measures are left for DAX — see MEASURES.md)*
- [ ] Produce final tidy frames matching the star schema below.

**Exit criteria:** in-memory frames for `fact_market`, `dim_region`, `dim_date` validate against expectations.

---

## Phase 4 — Storage / star schema (½ day)

Star schema (brief §7):

- **`fact_market`** — region_id, date, median_sale_price, price_per_sqft, median_rent,
  days_on_market, inventory, months_of_supply, price_cut_share, list_to_sale_ratio,
  rent_to_price, gross_rent_multiplier, est_cap_rate
- **`dim_region`** — region_id, zip, city, metro, state, lat, long, population,
  median_household_income, vacancy_rate *(income/vacancy stretch via Census)*
- **`dim_date`** — full date table for time-intelligence
- **`fact_listing`** *(stretch / deal screener)* — listing_id, region_id, date_pulled, price,
  beds, baths, sqft, est_rent, status

Tasks:
- [ ] `db/schema.sql` — DDL for tables + indexes + a `meta` table holding `last_updated`.
- [ ] `db/load.py` — create schema, truncate/upsert, load frames, stamp `last_updated`. Re-runnable.
- [ ] Generate `dim_date` programmatically across the data's date range.
- [ ] Commit a built **sample `parcel.sqlite`** (small) so the report can be wired without a full pull.

**Exit criteria:** `sqlite3 db/parcel.sqlite` shows populated tables; re-running `load.py` is idempotent.

---

## Phase 5 — Orchestration & reproducibility (½ day)

- [ ] `parcel/run.py` — single entry point: ingest → transform → load → stamp. Logs each stage.
- [ ] `Makefile` (or documented commands): `make refresh`, `make sample`, `make clean`.
- [ ] Verify a cold run from a clean checkout using committed sample produces a working DB.

**Exit criteria:** one command rebuilds the database end-to-end and updates `last_updated`.

---

## Phase 6 — Power BI spec: `MEASURES.md` (1 day) — Claude

*The bridge to the GUI step. Must be complete enough to build the report without guessing.*

- [ ] **Table relationships** — `fact_market[region_id] → dim_region[region_id]`,
      `fact_market[date] → dim_date[date]` (single-direction, star).
- [ ] **Power Query notes** — connect to `parcel.sqlite`, expected column types, any folding caveats.
- [ ] **DAX measures, fully written out:**
  - YoY appreciation = median price vs 12 months prior (`CALCULATE` + `DATEADD`)
  - Market temperature = z-score blend of months-of-supply + price-cut share + list-to-sale ratio
  - rent-to-price, GRM, cap rate (confirm whether computed in ETL or re-derived in DAX)
  - Cash-on-cash with **what-if parameters** (down %, rate, term, expense ratio)
  - KPI measures: last-updated, # regions, date range, # sources
- [ ] **View-by-view wireframes** (layout, visuals, fields, slicers) for Views 1–3.

---

## Phase 7 — Build the report (GUI) — YOU

1. Open Power BI Desktop → connect to `db/parcel.sqlite` (via ODBC/SQLite connector or import).
2. Apply Power Query steps and set relationships per `MEASURES.md`.
3. Add measures (copy/paste DAX from `MEASURES.md`).
4. Build the three MVP views:
   - **View 1 — Market Ranking:** choropleth + sortable table by rent-to-price, YoY appreciation,
     market temperature. *"Where should I look?"*
   - **View 2 — Market Detail:** drill into one region — price & rent trends, DOM, inventory,
     months-of-supply over time. *"Is now the time?"*
   - **View 3 — KPI header:** last-updated, # regions, date range, # sources.
5. **Publish to web** → capture the live link.
6. Capture 3–5 gallery screenshots + a cover image.

---

## Phase 8 — Docs & portfolio wiring (½ day) — Claude

- [ ] README: one-liner, architecture diagram (mermaid or `architecture.png`), data-source
      credits + "no scraping" note, run instructions, screenshots, live link.
- [ ] Portfolio entry copy: challenge / approach / outcome study + quantified metric cards
      (# markets, # metrics, date range, refresh cadence).
- [ ] Wire deliverables into the portfolio site (`components/Portfolio.jsx`): `live`, `code`,
      `image`, `images`, study, metric cards. Retire the Stock Dashboard entry; fold in the Web Scraper.

---

## Stretch phases (after MVP ships)

- **S1 — GitHub Actions refresh** (`.github/workflows/refresh.yml`): scheduled run of the ETL,
  commits refreshed sample DB, updates `last_updated`. Makes "refreshable" real.
- **S2 — Census enrichment**: `ingest/census.py` for median household income + vacancy into `dim_region`.
- **S3 — Deal Screener (View 4)**: `fact_listing` via RentCast/SimplyRETS free tier; cap rate /
  CoC / deal score + live what-if panel. Requires an API key (`.env`).
- **S4 — Threshold alerts**: flag when a market crosses a market-temperature/score threshold.

---

## Risks & mitigations

| Risk | Mitigation |
|---|---|
| Redfin↔Zillow region key mismatch | Resolve in Phase 0 spike; build explicit crosswalk in `dim_region`. |
| Source file URLs/schema change | Cache raw pulls; pin column mapping in config; committed sample keeps repo runnable. |
| Power BI SQLite connectivity friction | Document ODBC driver setup in README; fall back to CSV export from SQLite if needed. |
| Scope creep into "live listings" | Hard rule: any view that doesn't answer decision 1/2/3 is out. Deal screener stays stretch. |

---

## Suggested sequencing

Phase 0 → 1 → 2 → 3 → 4 → 5 → 6 (Claude can do 0–6 and 8) → **7 (you, GUI)** → 8 → stretch.

**Next action:** start **Phase 0 — the data spike**: download one Redfin CSV and one Zillow CSV,
confirm fields, and lock the region join key. Say the word and I'll begin.
