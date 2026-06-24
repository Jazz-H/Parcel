# Parcel — Portfolio Entry Copy

Formatted to match the existing entries (e.g. *KPI Management Dashboard*): a category kicker,
descriptive title, one-line subtitle, Company/Role, Stack, Visit-live, then
Challenge / Approach / Outcome and three Results cards. Keep every line short and scannable.
Fill the `TODO`s once the Power BI report is published.

---

## Field-by-field (matches the on-page layout)

- **Category:** `Data`
- **Title:** **Real-Estate Market Analytics**
- **Subtitle:** An end-to-end pipeline that turns official housing data into a clear view of
  *where to buy and when* — for a buy-and-hold investor.
- **Company:** Personal project
- **Role:** Data / BI analyst
- **Stack:** `Python` · `pandas` · `SQL` · `SQLite` · `Power BI` · `DAX`
- **Visit live:** `TODO` — Power BI Publish-to-web link
- **Code:** https://github.com/Jazz-H/Parcel

**Challenge**
> Turn scattered public housing data into one view a real-estate investor can act on — which
> market, and is now the time?

**Approach**
> Built a Python ETL over officially published data (Redfin, Zillow — no scraping), modeled it
> into a SQLite star schema, and delivered investor metrics in an interactive Power BI report.

**Outcome**
> A refreshable, decision-ready dashboard ranking metros by appreciation, market temperature,
> and rent-to-price.

**Results** *(three cards — bold header + short line)*

| Header | Line |
|---|---|
| **End-to-end** | Ingest → model → BI |
| **Officially sourced** | Public data, no scraping |
| **Refreshable** | Scheduled auto-update |

---

## Portfolio.jsx object (paste into the projects array; adjust field names to your schema)

```jsx
{
  category: "Data",
  title: "Real-Estate Market Analytics",
  subtitle:
    "An end-to-end pipeline that turns official housing data into a clear view of " +
    "where to buy and when — for a buy-and-hold investor.",
  company: "Personal project",
  role: "Data / BI analyst",
  stack: ["Python", "pandas", "SQL", "SQLite", "Power BI", "DAX"],
  challenge:
    "Turn scattered public housing data into one view a real-estate investor can act on — " +
    "which market, and is now the time?",
  approach:
    "Built a Python ETL over officially published data (Redfin, Zillow — no scraping), " +
    "modeled it into a SQLite star schema, and delivered investor metrics in an interactive " +
    "Power BI report.",
  outcome:
    "A refreshable, decision-ready dashboard ranking metros by appreciation, market " +
    "temperature, and rent-to-price.",
  results: [
    { header: "End-to-end",        line: "Ingest → model → BI" },
    { header: "Officially sourced", line: "Public data, no scraping" },
    { header: "Refreshable",       line: "Scheduled auto-update" },
  ],
  live: "TODO_POWERBI_PUBLISH_TO_WEB_LINK",
  code: "https://github.com/Jazz-H/Parcel",
  image: "TODO_COVER_IMAGE",
  images: ["TODO_1", "TODO_2", "TODO_3"],
}
```

---

## Alternate Results cards (if you prefer numbers over qualitative)

Swap the three qualitative cards for quantified ones once rent data is loaded:

| Header | Line |
|---|---|
| **8 metros** | Charlotte + Sun-Belt targets |
| **14+ yrs** | Monthly history, 2012–2026 |
| **10+ metrics** | Appreciation, temp, cap rate |

---

## Notes

- Replace `TODO` live link + images after **Publish to web** and screenshot capture.
- Keep the **last-updated** stamp visible in the dashboard so "refreshable" is honest.
- Hold the **no-scraping** framing — it reads as data-sourcing maturity in interviews.
- Title is kept descriptive (like the other entries); "Parcel" can live as the repo name / a
  small kicker if your layout supports one.
