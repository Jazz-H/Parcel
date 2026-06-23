# Parcel — Implementation Plan (updated)

> End-to-end real-estate market-analytics pipeline for a buy-and-hold investor: official
> public housing data → Python ETL → SQLite star schema → Power BI → Publish to web.
>
> **Updated** to reflect the built pipeline and the network allowlist now including the rent
> sources. For the original phased plan see git history; this is the current source of truth.

---

## Locked decisions

| Decision | Choice |
|---|---|
| **Name** | Parcel |
| **Medium** | Power BI (Claude builds pipeline + `MEASURES.md`; you assemble the `.pbix` + Publish to web) |
| **Geographic scope** | Focused markets — Charlotte (anchor) + Sun-Belt targets |
| **Deal Screener (View 4)** | Stretch (post-MVP) |
| **Rent data** | **Broaden network allowlist** to reach Zillow (+ Census) — *in progress* |

**Markets (CBSA, configurable in `config.yml`):** Charlotte 16740 (anchor), Raleigh 39580,
Atlanta 12060, Nashville 34980, Tampa 45300, Dallas **19124**, Columbus 18140, Indianapolis 26900.

---

## Network allowlist (the unblock)

Rent metrics were blocked because this environment's allowlist excluded the rent sources.
**Resolution:** set the environment **Network access → Custom** (web UI at claude.ai/code →
cloud icon → edit environment) with these **Allowed domains**, "include default package
managers" checked:

```
files.zillowstatic.com     # Zillow ZHVI (values) + ZORI (rents) — required for rent metrics
api.census.gov             # Census ACS enrichment — stretch
www2.census.gov            # Census bulk — stretch
```

> Changing allowed hosts rebuilds the environment cache; **start a fresh session** for it to
> take effect, then run `make refresh`. Mobile is monitor-only — make this edit on the web.

---

## Status at a glance

| Phase | What | Status |
|---|---|---|
| 0 | Data spike — sources, fields, CBSA join key | ✅ done (`docs/data-spike.md`) |
| 1 | Repo scaffold (config, requirements, Makefile, .env) | ✅ done |
| 2 | Ingest — Redfin (live) + Zillow module (ready) | ✅ done |
| 3 | Transform — clean, geo-normalize, derive metrics | ✅ done |
| 4 | Storage — SQLite star schema + loader | ✅ done |
| 5 | Orchestration — one-command refresh + sample | ✅ done |
| 6 | Power BI spec — `MEASURES.md` | ✅ done |
| 8 | Portfolio entry copy | ✅ done (`docs/portfolio-entry.md`) |
| S1 | GitHub Actions scheduled refresh | ✅ done |
| — | **Rent metrics live run** | ⏳ pending fresh session on updated allowlist |
| 7 | **Power BI report assembly + Publish to web** | ◻️ your GUI step |
| 8b | Fill portfolio `TODO`s (live link, screenshots) | ◻️ after Publish |
| S2 | Census enrichment (income/vacancy) | ◻️ stretch |
| S3 | Deal Screener (View 4) | ◻️ stretch |

**Current database:** price-side, 8 metros, 2012-01 → 2026-05, ~1,358 region-months. Rent
columns present but null until the Zillow run.

---

## Remaining steps (in order)

### Step A — Activate rent metrics  *(Claude, once the new session is on the updated allowlist)*
1. `make refresh` (or `python -m parcel.run`) — now fetches Zillow ZHVI + ZORI and populates
   `median_rent`, `rent_to_price`, `gross_rent_multiplier`, `est_cap_rate`.
2. Sanity-check rent values per metro; confirm CBSA↔Zillow name mapping resolved all 8 markets.
3. `make sample` — regenerate `data/sample/parcel_sample.sqlite` + CSV exports.
4. Bump `meta.data_sources` to 2 (Redfin + Zillow) automatically; verify in the DB.
5. Commit + push the refreshed sample.

### Step B — Assemble the Power BI report  *(You — GUI)*
Follow `powerbi/MEASURES.md` exactly:
1. Connect to `db/parcel.sqlite` (ODBC) or the committed sample; load all 4 tables.
2. Set the star relationships; mark `dim_date` as the date table.
3. Create the what-if parameters and paste the DAX measures.
4. Build **View 1 Market Ranking**, **View 2 Market Detail**, **View 3 KPI header**.
5. **Publish to web** → copy the public link.
6. Capture 3–5 screenshots (ranking + map, detail trends, what-if panel) + a cover image.

### Step C — Finalize portfolio entry  *(Claude)*
1. Fill the `TODO`s in `docs/portfolio-entry.md`: `live` link, `image`, `images`.
2. Optionally swap one metric card for a headline finding (e.g. top metro by rent-to-price).
3. If you add the portfolio-site repo to the session, wire the entry into `Portfolio.jsx`
   and retire the *Real-time Stock Market Dashboard* entry (fold in the *Web Scraper*).

### Step D — README polish  *(Claude)*
1. Embed the live link + screenshots in `README.md`; flip the status checklist to ✅.

---

## Stretch (after MVP ships)

- **S2 — Census enrichment:** `ingest/census.py` → populate `dim_region` population /
  median household income / vacancy (allowlist already includes Census).
- **S3 — Deal Screener (View 4):** `fact_listing` via RentCast/SimplyRETS free tier; cap rate /
  cash-on-cash / deal score with the live what-if panel.
- **S4 — Threshold alerts:** flag when a market crosses a market-temperature score.

---

## Risks & mitigations (current)

| Risk | Mitigation |
|---|---|
| Zillow RegionName ↔ CBSA mapping misses a metro | Step A.2 verifies all 8; fallback name-match in `zillow.py`; adjust `config.yml` names if needed. |
| Allowlist change not picked up by running session | Start a fresh session after editing the environment (noted above). |
| Power BI SQLite/ODBC friction | `MEASURES.md` documents the driver; CSV fallback (`data/sample/*.csv`) provided. |
| Scope creep into live listings | Hard rule: any view not answering decision 1/2/3 is out; deal screener stays stretch. |

---

## Definition of done (MVP)

- [x] Redfin ingested → SQLite star schema; reproducible one-command refresh
- [x] Core metrics in ETL; remaining specced as DAX in `MEASURES.md`
- [x] Committed sample so the repo runs offline
- [x] README with architecture diagram
- [x] Portfolio entry copy drafted
- [ ] **Rent metrics populated** (Step A — pending fresh session on updated allowlist)
- [ ] **Power BI report assembled + Published to web** (Step B — your GUI step)
- [ ] Portfolio `TODO`s filled with live link + screenshots (Step C)

**Next action:** start a fresh session on the updated environment, then tell me
**"network's open"** — I'll run Step A and populate the rent metrics.
