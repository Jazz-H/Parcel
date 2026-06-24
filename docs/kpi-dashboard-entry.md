# KPI Management Dashboard — Portfolio Entry Copy

Elevated to match the tone, depth, and structure of the Parcel entry (substantive intro
paragraph, decision-framed Challenge, technical Approach, three Results cards). Drop into the
portfolio repo's `Portfolio.jsx`. Fill the `TODO` live link.

---

## Field-by-field (matches the on-page layout)

- **Category:** `Data`
- **Title:** **KPI Management Dashboard**
- **Subtitle:** A sales-and-profit analytics dashboard that turns raw transaction exports into a
  single, decision-ready view of how the business is performing. It models the data into clean
  measures — revenue, profit, and margin with their trends — and surfaces them in an interactive
  Tableau dashboard a manager can filter by product, region, and period to move from the headline
  number to the segment driving it. Published to Tableau Public for one-click sharing, no analyst
  in the loop.
- **Company:** Personal project
- **Role:** Data analyst
- **Stack:** `Tableau` · `Tableau Public` · `Data modeling`
- **Visit live:** `TODO` — Tableau Public link

**Challenge**
> Raw sales and profit exports answer *what happened*, not *what to do about it*. A manager
> doesn't need another spreadsheet — they need to see at a glance which products, regions, and
> periods are driving the business and where margin is leaking, without waiting on an analyst.

**Approach**
> Modeled the sales and profit data into a clean, filterable structure, defined the KPIs that
> matter — revenue, profit, and margin % plus their period-over-period trends — as calculated
> fields, then built an interactive Tableau dashboard with filters and drill-downs so a manager
> can move from a top-line number to the segment behind it. Published to Tableau Public for
> instant, no-login sharing.

**Outcome**
> A shareable, self-serve dashboard that replaces a static export: filter by segment, read the
> trend, and act — decisions in seconds instead of a data request.

**Results** *(three cards — bold header + short line)*

| Header | Line |
|---|---|
| **Published** | Live on Tableau Public |
| **Interactive** | Filter by product, region & time |
| **Decision-ready** | KPIs and trends at a glance |

---

## Portfolio.jsx object (paste into the projects array; adjust field names to your schema)

```jsx
{
  category: "Data",
  title: "KPI Management Dashboard",
  subtitle:
    "A sales-and-profit analytics dashboard that turns raw transaction exports into a " +
    "single, decision-ready view of how the business is performing. It models the data " +
    "into clean measures — revenue, profit, and margin with their trends — and surfaces " +
    "them in an interactive Tableau dashboard a manager can filter by product, region, and " +
    "period to move from the headline number to the segment driving it. Published to " +
    "Tableau Public for one-click sharing, no analyst in the loop.",
  company: "Personal project",
  role: "Data analyst",
  stack: ["Tableau", "Tableau Public", "Data modeling"],
  challenge:
    "Raw sales and profit exports answer what happened, not what to do about it. A manager " +
    "needs to see at a glance which products, regions, and periods drive the business and " +
    "where margin is leaking — without waiting on an analyst.",
  approach:
    "Modeled the data into a clean, filterable structure, defined the KPIs that matter — " +
    "revenue, profit, and margin % with period-over-period trends — as calculated fields, " +
    "then built an interactive Tableau dashboard with filters and drill-downs, published to " +
    "Tableau Public.",
  outcome:
    "A shareable, self-serve dashboard that replaces a static export: filter by segment, " +
    "read the trend, and act — decisions in seconds instead of a data request.",
  results: [
    { header: "Published",      line: "Live on Tableau Public" },
    { header: "Interactive",    line: "Filter by product, region & time" },
    { header: "Decision-ready", line: "KPIs and trends at a glance" },
  ],
  live: "TODO_TABLEAU_PUBLIC_LINK",
}
```

---

## Notes

- Copy is kept **truthful to a generic sales/profit dashboard** — no fabricated metrics or
  segments. If you know the dataset (e.g. Superstore, or specific regions/categories), the
  Challenge/Approach can be made more concrete.
- **Stack** additions: if you used **Tableau Prep** or **LOD expressions**, add them — both are
  honest, recruiter-friendly signals.
- Replace the `TODO` live link with the Tableau Public URL.
