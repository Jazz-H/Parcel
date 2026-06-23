# Parcel — Power BI Build Spec (`MEASURES.md`)

Everything needed to assemble the report from `db/parcel.sqlite` (or
`data/sample/parcel_sample.sqlite`): data connection, relationships, DAX measures,
what-if parameters, and a view-by-view wireframe. Copy the DAX verbatim.

---

## 1. Connect to the data

Power BI Desktop → **Get Data**. Two reliable options for SQLite:

- **ODBC** (recommended): install the SQLite ODBC driver (http://www.ch-werner.de/sqliteodbc/),
  create a DSN pointing at `parcel.sqlite`, then *Get Data → ODBC → that DSN*. Import mode.
- **CSV fallback**: `data/sample/fact_market.csv` + `dim_region.csv` if you'd rather skip ODBC.
  (You'll lose the `meta` and `dim_date` tables — build a date table in DAX instead, §4.)

Load all four tables: **fact_market, dim_region, dim_date, meta**.

### Power Query notes
- `fact_market.date` and `dim_date.date` → set type **Date**.
- Numeric measure columns → **Decimal Number** (SQLite stores them as REAL/TEXT depending on driver; force the type).
- `dim_region.is_anchor` → **True/False**.
- `meta` is a tall key/value table — keep as-is; we read it with `LOOKUPVALUE`.
- `price_cut_share` and `list_to_sale_ratio` are already fractions (0–1); format as **Percentage**.

---

## 2. Relationships (star)

| From | To | Cardinality | Direction |
|---|---|---|---|
| `fact_market[region_id]` | `dim_region[region_id]` | many-to-one | single |
| `fact_market[date]` | `dim_date[date]` | many-to-one | single |

Mark **`dim_date`** as the official **Date table** (Table tools → Mark as date table → `date`).
Do **not** relate `meta` to anything.

---

## 3. What-if parameters (Modeling → New parameter)

Create these as **numeric range** parameters (they generate a table + slicer + a
`Selected Value` measure each):

| Parameter | Min | Max | Increment | Default |
|---|---|---|---|---|
| `Down Payment %` | 0.05 | 0.50 | 0.05 | 0.25 |
| `Interest Rate` | 0.03 | 0.10 | 0.0025 | 0.07 |
| `Loan Term (yrs)` | 15 | 30 | 5 | 30 |
| `Expense Ratio` | 0.20 | 0.60 | 0.05 | 0.45 |

These feed Cap Rate (override of the ETL default) and Cash-on-Cash (§5.4).

---

## 4. Date table (only if you used the CSV fallback)

```DAX
dim_date =
ADDCOLUMNS (
    CALENDAR ( DATE ( 2012, 1, 1 ), DATE ( 2026, 12, 1 ) ),
    "year", YEAR ( [Date] ),
    "quarter", QUARTER ( [Date] ),
    "month", MONTH ( [Date] ),
    "month_name", FORMAT ( [Date], "MMMM" ),
    "year_month", FORMAT ( [Date], "YYYY-MM" )
)
```

---

## 5. Measures

Create a measures-only table (`_Measures`) to keep them tidy. All measures below.

### 5.1 KPI header (from `meta`)
```DAX
Last Updated = LOOKUPVALUE ( meta[value], meta[key], "last_updated" )
Regions Tracked = INT ( LOOKUPVALUE ( meta[value], meta[key], "regions_tracked" ) )
Data Sources = INT ( LOOKUPVALUE ( meta[value], meta[key], "data_sources" ) )
Date Range =
    LOOKUPVALUE ( meta[value], meta[key], "date_min" ) & "  →  "
    & LOOKUPVALUE ( meta[value], meta[key], "date_max" )
```

### 5.2 Core market measures
Use the **last date in context** so cards/tables show the latest value per region.
```DAX
Latest Date = MAX ( fact_market[date] )

Median Sale Price =
CALCULATE ( AVERAGE ( fact_market[median_sale_price] ),
    fact_market[date] = [Latest Date] )

Days on Market =
CALCULATE ( AVERAGE ( fact_market[days_on_market] ), fact_market[date] = [Latest Date] )

Months of Supply =
CALCULATE ( AVERAGE ( fact_market[months_of_supply] ), fact_market[date] = [Latest Date] )

Price Cut Share =
CALCULATE ( AVERAGE ( fact_market[price_cut_share] ), fact_market[date] = [Latest Date] )

List to Sale Ratio =
CALCULATE ( AVERAGE ( fact_market[list_to_sale_ratio] ), fact_market[date] = [Latest Date] )

Inventory =
CALCULATE ( AVERAGE ( fact_market[inventory] ), fact_market[date] = [Latest Date] )
```
For the **trend lines** in View 2 use the columns directly (no `[Latest Date]` filter),
e.g. `Median Sale Price (trend) = AVERAGE ( fact_market[median_sale_price] )`.

### 5.3 YoY appreciation
```DAX
Median Price 12mo Ago =
CALCULATE (
    AVERAGE ( fact_market[median_sale_price] ),
    DATEADD ( dim_date[date], -12, MONTH )
)

YoY Appreciation =
VAR Now =
    CALCULATE ( AVERAGE ( fact_market[median_sale_price] ),
        fact_market[date] = [Latest Date] )
VAR Prior =
    CALCULATE ( AVERAGE ( fact_market[median_sale_price] ),
        fact_market[date] = EDATE ( [Latest Date], -12 ) )
RETURN DIVIDE ( Now - Prior, Prior )
```

### 5.4 Rent-based metrics (activate when Zillow rent is loaded)
The ETL already writes `rent_to_price`, `gross_rent_multiplier`, `est_cap_rate`
(null until Zillow is ingested). Surface them, and add a what-if-driven cap rate /
cash-on-cash:
```DAX
Rent to Price =
CALCULATE ( AVERAGE ( fact_market[rent_to_price] ), fact_market[date] = [Latest Date] )

Gross Rent Multiplier =
CALCULATE ( AVERAGE ( fact_market[gross_rent_multiplier] ), fact_market[date] = [Latest Date] )

Median Rent =
CALCULATE ( AVERAGE ( fact_market[median_rent] ), fact_market[date] = [Latest Date] )

-- Cap rate recomputed live with the Expense Ratio what-if (overrides ETL default)
Cap Rate (what-if) =
VAR AnnualRent = [Median Rent] * 12
VAR NOI = AnnualRent * ( 1 - [Expense Ratio Value] )
RETURN DIVIDE ( NOI, [Median Sale Price] )

-- Cash-on-cash: annual pre-tax cash flow / cash invested
Cash on Cash (what-if) =
VAR Price        = [Median Sale Price]
VAR DownPct      = [Down Payment % Value]
VAR Rate         = [Interest Rate Value]
VAR TermMonths   = [Loan Term (yrs) Value] * 12
VAR Loan         = Price * ( 1 - DownPct )
VAR MonthlyRate  = Rate / 12
VAR MonthlyPmt   =
    IF ( MonthlyRate = 0, DIVIDE ( Loan, TermMonths ),
        Loan * MonthlyRate / ( 1 - ( 1 + MonthlyRate ) ^ -TermMonths ) )
VAR AnnualDebt   = MonthlyPmt * 12
VAR AnnualNOI    = [Median Rent] * 12 * ( 1 - [Expense Ratio Value] )
VAR AnnualCash   = AnnualNOI - AnnualDebt
VAR CashInvested = Price * DownPct
RETURN DIVIDE ( AnnualCash, CashInvested )
```
> `[<Parameter> Value]` are the auto-generated selected-value measures from §3.

### 5.5 Market temperature (z-score blend)
A composite, computed **across the regions currently visible**, for the latest month.
Hotter = **lower** months-of-supply, **lower** price-cut share, **higher** list-to-sale.
We z-score each component across regions, invert the two "lower is hotter" ones, and average.

```DAX
-- helper: population mean/std across visible regions at the latest date
Temp: MoS z =
VAR Vals =
    CALCULATETABLE (
        ADDCOLUMNS ( VALUES ( dim_region[region_id] ), "v", [Months of Supply] ),
        ALLSELECTED ( dim_region )
    )
VAR Mu = AVERAGEX ( Vals, [v] )
VAR Sd = STDEVX.P ( Vals, [v] )
RETURN DIVIDE ( [Months of Supply] - Mu, Sd )

Temp: PriceCut z =
VAR Vals =
    CALCULATETABLE (
        ADDCOLUMNS ( VALUES ( dim_region[region_id] ), "v", [Price Cut Share] ),
        ALLSELECTED ( dim_region )
    )
VAR Mu = AVERAGEX ( Vals, [v] )
VAR Sd = STDEVX.P ( Vals, [v] )
RETURN DIVIDE ( [Price Cut Share] - Mu, Sd )

Temp: ListSale z =
VAR Vals =
    CALCULATETABLE (
        ADDCOLUMNS ( VALUES ( dim_region[region_id] ), "v", [List to Sale Ratio] ),
        ALLSELECTED ( dim_region )
    )
VAR Mu = AVERAGEX ( Vals, [v] )
VAR Sd = STDEVX.P ( Vals, [v] )
RETURN DIVIDE ( [List to Sale Ratio] - Mu, Sd )

Market Temperature =
AVERAGEX (
    { ( - [Temp: MoS z] ), ( - [Temp: PriceCut z] ), [Temp: ListSale z] },
    [Value]
)
```
Positive = hotter than the peer set; negative = cooler. Apply a diverging color scale
(blue → red) on this measure in the ranking table/map.

---

## 6. View-by-view wireframe

### View 1 — Market Ranking  *"Where should I look?"*
- **KPI strip (top):** cards — `Last Updated`, `Regions Tracked`, `Date Range`, `Data Sources`.
- **Left ~55%:** Filled **Map** (`dim_region[metro]` or city; bubble size = `Median Sale Price`,
  color = `Market Temperature`).
- **Right ~45%:** **Table/Matrix** by `dim_region[metro]`, columns:
  `Median Sale Price`, `YoY Appreciation` (▲/▼ conditional color), `Days on Market`,
  `Months of Supply`, `Market Temperature` (data bars), and (when rent loaded)
  `Rent to Price`, `Cap Rate (what-if)`. Default sort: `Market Temperature` desc.
- **Slicer:** `dim_region[state]`; toggle `dim_region[is_anchor]`.

### View 2 — Market Detail  *"Is now the time?"*
- **Slicer (single-select):** `dim_region[metro]` (default = Charlotte).
- **Cards:** `Median Sale Price`, `YoY Appreciation`, `Days on Market`, `Months of Supply`.
- **Line charts (x = `dim_date[date]`):**
  1. `Median Sale Price (trend)` (+ `Median Rent` on a secondary axis once loaded)
  2. `Days on Market` and `Months of Supply`
  3. `Price Cut Share` and `List to Sale Ratio`
- **What-if panel (when rent loaded):** the four §3 slicers + cards `Cap Rate (what-if)`,
  `Cash on Cash (what-if)`, `Gross Rent Multiplier`.

### View 3 — KPI header
Can be the strip atop View 1, or a standalone summary page: the four meta cards plus a
one-line method note and source credits (Redfin, Zillow). Honesty cue: surface
`Last Updated` prominently.

### (Stretch) View 4 — Deal Screener
Table on `fact_listing` with `Cap Rate`, `Cash on Cash`, `Deal Score`; the §3 what-if panel
recalculates live. Build after `fact_listing` is populated (RentCast/SimplyRETS).

---

## 7. Publish

File → Publish → *Publish to web (public)* → copy the embed/live link into the README and
portfolio entry. Capture 3–5 screenshots (Views 1–2, the map, the what-if panel) for the gallery.
