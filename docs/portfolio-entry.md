# Parcel — Portfolio Entry Copy

Ready-to-paste copy and data for the portfolio site. Replace the `TODO` placeholders
(live link + screenshots) once the Power BI report is published. Figures below are pulled
from the built database (2012-01 → 2026-05, 8 metros).

> **Placement (per brief):** replace the *Real-time Stock Market Dashboard* entry and fold in
> the *Real Estate Web Scraper* (retire the standalone scraper). Category: `Power Apps & Data`,
> `kind: "Data"`.

---

## Title & one-liner

**Parcel — Real-Estate Market Analytics**

> An end-to-end pipeline that turns official public housing data into one view of *where to
> buy and whether now is the time* — built for a buy-and-hold investor.

## Short blurb (cards / list view, ~240 chars)

Python ETL → SQLite star schema → Power BI. Parcel ingests officially published housing
datasets (Redfin, Zillow), models them dimensionally, and surfaces investor metrics —
appreciation, market temperature, rent-to-price, cap rate — across target metros.

---

## Study — Challenge / Approach / Outcome

**Challenge.** A buy-and-hold investor evaluating multiple metros has no single, trustworthy
view of *which market to enter* and *whether the timing is right*. The usable signals —
appreciation, days-on-market, months-of-supply, price-cut share, rent-to-price — live in
separate published datasets at different grains and region keys, and listing portals can't be
scraped responsibly. The task was to build a defensible, refreshable analytics product from
**official data only**, that answers investor decisions rather than just plotting charts.

**Approach.** I built the full data lifecycle end-to-end:
- **Ingest** — a Python (requests/pandas) ETL pulls Redfin's metro market tracker and Zillow's
  ZHVI/ZORI research files. No scraping — every source is a dataset these companies publish
  for download.
- **Model** — cleaned, de-duplicated, and geo-normalized the sources onto a shared **CBSA**
  region key, then loaded a **star schema** (`fact_market` + `dim_region` + `dim_date`) in
  SQLite, with a `meta` table stamping the last-updated date for honest "refreshable" claims.
- **Derive** — computed investor metrics in the pipeline (rent-to-price/1% rule, gross rent
  multiplier, estimated cap rate) and specced the rest as **DAX** (YoY appreciation, a z-score
  **market-temperature** composite, and what-if cash-on-cash with adjustable down payment /
  rate / term / expense ratio).
- **Deliver** — a **Power BI** report (Power Query + DAX) with a Market Ranking view
  (*where to look*), a Market Detail view (*is now the time*), and a KPI header — Published to web.
- **Automate** — a scheduled **GitHub Actions** refresh rebuilds the database and updates the
  last-updated stamp weekly.

**Outcome.** A reproducible, single-command pipeline (`make refresh`) producing a clean
dimensional model over **8 metros and 14+ years of monthly data (~1,350 region-months)**,
delivered in the BI tool stakeholders actually use. Region reconciliation — the riskiest part —
was solved by standardizing on CBSA codes shared across sources. The result demonstrates the
combined story: *I can code the data pipeline and deliver it in the enterprise BI tool.*

---

## Metric cards (quantified)

| Value | Label |
|---|---|
| **8** | Target metros tracked |
| **14+ yrs** | Monthly history (2012 → 2026) |
| **~1,350** | Region-months modeled |
| **10+** | Investor metrics (DAX + ETL) |
| **4-table** | Dimensional star schema |
| **Weekly** | Automated refresh cadence |

*(After rent data loads and the report is published, optionally swap one card for a headline
finding, e.g. "Top market by rent-to-price: <metro>".)*

---

## Tech tags

`Python` · `pandas` · `SQL` · `SQLite` · `Dimensional modeling (star schema)` ·
`Power BI` · `DAX` · `Power Query` · `ETL` · `GitHub Actions`

---

## Deliverable links

- **live:** `TODO` — Power BI Publish-to-web link
- **code:** https://github.com/Jazz-H/Parcel
- **image:** `TODO` — cover (Market Ranking view with map)
- **images:** `TODO` — 3–5 gallery shots (ranking table, choropleth, market detail trends, what-if panel)

---

## Portfolio.jsx object (paste into the projects array, adjust field names to your schema)

```jsx
{
  title: "Parcel — Real-Estate Market Analytics",
  category: "Power Apps & Data",
  kind: "Data",
  blurb:
    "Python ETL → SQLite star schema → Power BI. Ingests officially published housing " +
    "datasets (Redfin, Zillow), models them dimensionally, and surfaces investor metrics — " +
    "appreciation, market temperature, rent-to-price, cap rate — across target metros.",
  tech: [
    "Python", "pandas", "SQL", "SQLite", "Star schema",
    "Power BI", "DAX", "Power Query", "ETL", "GitHub Actions",
  ],
  metrics: [
    { value: "8",       label: "Metros tracked" },
    { value: "14+ yrs", label: "Monthly history" },
    { value: "~1,350",  label: "Region-months modeled" },
    { value: "10+",     label: "Investor metrics" },
  ],
  study: {
    challenge:
      "A buy-and-hold investor had no single, trustworthy view of which metro to enter and " +
      "whether the timing was right — the signals live in separate published datasets at " +
      "different grains, and listing portals can't be scraped responsibly.",
    approach:
      "Built the full lifecycle: a Python ETL ingesting Redfin/Zillow research files (no " +
      "scraping), geo-normalized onto shared CBSA keys, loaded a SQLite star schema, derived " +
      "investor metrics in pipeline + DAX, and delivered a Power BI report published to web.",
    outcome:
      "A reproducible one-command pipeline over 8 metros and 14+ years of monthly data, " +
      "delivered in the BI tool stakeholders use — proving I can code the pipeline and ship " +
      "it in the enterprise tool.",
  },
  live: "TODO_POWERBI_PUBLISH_TO_WEB_LINK",
  code: "https://github.com/Jazz-H/Parcel",
  image: "TODO_COVER_IMAGE",
  images: ["TODO_1", "TODO_2", "TODO_3"],
}
```

---

## Notes / honesty checklist

- The metric cards reflect the **price-side** database that exists today. Rent-to-price / cap
  rate populate once Zillow rent is ingested (network allowlist), strengthening — not changing —
  the story.
- Keep the **last-updated** date visible in the dashboard; the copy claims "refreshable" and
  the GitHub Actions workflow backs it.
- Maintain the **no-scraping** framing in interviews — it reads as data-sourcing maturity.
