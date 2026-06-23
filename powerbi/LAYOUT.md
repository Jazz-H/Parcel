# Parcel — Power BI Layout Spec (`LAYOUT.md`)

Build-by-the-numbers companion to `MEASURES.md`. Exact visual positions for the two
core pages, matching the rendered preview. Pair with **`parcel-theme.json`**
(*View → Themes → Browse for themes*) so colors/typography are already correct — this
file only places and sizes the visuals.

> **Canvas:** 1280 × 720 px (Format pane → Canvas settings → Type = 16:9). All X/Y/W/H
> below are pixels from the top-left. Snap: *View → Show gridlines* + *Snap to grid* (8 px).
> Set each visual's exact box in **Format → General → Properties → Size and position**.

## Palette (from the theme — for manual conditional formatting)

| Token | Hex | Use |
|---|---|---|
| Ink | `#1A1F36` | titles, primary values |
| Slate | `#5A6478` | labels, secondary text, axes |
| Paper | `#F7F8FA` | page background |
| Card | `#FFFFFF` | visual backgrounds |
| Teal (accent) | `#0E7C7B` | price line, positive, table accent |
| Amber | `#C98A1A` | rent line (secondary axis) |
| Blue | `#2C7FB8` | DOM line / temp cold end |
| Red | `#D7301F` | months-of-supply line / temp hot end |
| Positive | `#0E7C7B` | YoY ▲ |
| Negative | `#C0392B` | YoY ▼ |
| Border | `#E7E9EF` | card borders, gridlines |

Diverging **Market Temperature** scale: min `#2C7FB8` → center `#EDEDED` → max `#D7301F`
(set center = 0, "Number" type).

---

## Page 1 — Market Ranking  (1280 × 720)

| # | Visual | Type | X | Y | W | H | Notes |
|---|---|---|---:|---:|---:|---:|---|
| 1 | Page title | Text box | 28 | 24 | 520 | 40 | "**Parcel** \| Market Ranking" — "Parcel" Ink 24 bold, "\| Market Ranking" Teal 15 semibold. |
| 2 | Subtitle | Text box | 28 | 60 | 620 | 22 | "Buy-and-hold market analytics · 8 metros · Redfin + Zillow" — Slate 10. |
| 3 | Last Updated | Card | 904 | 22 | 176 | 60 | `[Last Updated]`, category label "LAST UPDATED". |
| 4 | Coverage | Card | 1088 | 22 | 168 | 60 | `[Regions Tracked]` + `[Data Sources]` (multi-row card, or two stacked). |
| 5–8 | KPI strip | 4 × Card | 28 / 316 / 604 / 892 | 96 | 272 | 78 | Hottest market · Best rent-to-price · Median price · Median YoY. Gap 16. |
| 9 | Market map | **Filled map** | 28 | 188 | 560 | 496 | `dim_region[metro]`; bubble size = `[Median Sale Price]`; fill = `[Market Temperature]` (diverging). Title "Market Temperature". |
| 10 | Ranking detail | **Table** | 612 | 188 | 644 | 496 | Columns in §"Matrix columns" below. Sort `[Market Temperature]` desc. |
| 11 | State slicer | Slicer (dropdown) | 612 | 150 | 200 | 32 | `dim_region[state]`, horizontal/dropdown. |
| 12 | Anchor toggle | Slicer | 820 | 150 | 160 | 32 | `dim_region[is_anchor]`, single-select tile. |
| 13 | Source footnote | Text box | 28 | 690 | 1100 | 24 | "Sources: Redfin Market Tracker, Zillow ZHVI/ZORI · Temp = mean z-score of (−months supply, −price-cut share, list-to-sale)." Slate 8. |

**Matrix columns (#10), left→right:** Metro · `[Median Sale Price]` · `[YoY Appreciation]`
· `[Days on Market]` · `[Months of Supply]` · `[Rent to Price]` · `[Cap Rate (what-if)]`
· `[Market Temperature]`.
- YoY: **conditional font color** — Format → Cell elements → Font color → rules: `< 0` →
  `#C0392B`, `>= 0` → `#0E7C7B`. (Add ▲/▼ via a measure if you want the glyph.)
- Market Temperature: **Data bars** (Cell elements → Data bars) using the diverging scale,
  positive `#D7301F` / negative `#2C7FB8`.

---

## Page 2 — Market Detail  (1280 × 720)

| # | Visual | Type | X | Y | W | H | Notes |
|---|---|---|---:|---:|---:|---:|---|
| 1 | Page title | Text box | 28 | 24 | 520 | 40 | "**Parcel** \| Market Detail". |
| 2 | Subtitle | Text box | 28 | 60 | 620 | 22 | Selected metro name (or static "anchor market"). |
| 3 | Metro slicer | Slicer (dropdown, single-select) | 1024 | 22 | 232 | 60 | `dim_region[metro]`, default Charlotte. Header "METRO". |
| 4–7 | KPI cards | 4 × Card | 28 / 316 / 604 / 892 | 96 | 272 | 78 | Median price (+YoY sub) · Median rent (+GRM) · Days on market (+supply) · Cap rate (+rent/price). |
| 8 | Price vs rent | **Line chart** | 28 | 196 | 600 | 224 | X = `dim_date[date]`; Y = `[Median Sale Price (trend)]` (Teal); secondary Y = `[Median Rent]` (Amber). |
| 9 | DOM vs supply | **Line chart** | 656 | 196 | 600 | 224 | X = date; `[Days on Market]` (Blue) on L; `[Months of Supply]` (Red) on R. |
| 10 | What-if panel bg | Shape (rounded rect) | 28 | 440 | 1228 | 248 | Fill `#FCFCFD`, border `#E7E9EF` r=8. Header text "UNDERWRITING ASSUMPTIONS (what-if)". |
| 11–14 | What-if slicers | 4 × Slicer (numeric) | 44 / 268 / 492 / 716 | 500 | 208 | 96 | Down Payment % · Interest Rate · Loan Term · Expense Ratio (from `MEASURES.md` §3). |
| 15 | Cap Rate (what-if) | Card | 952 | 480 | 96 | 180 | Teal border, value `[Cap Rate (what-if)]`. |
| 16 | Cash-on-Cash | Card | 1056 | 480 | 96 | 180 | `[Cash on Cash (what-if)]`, conditional color (− red / + green). |
| 17 | Gross Rent Mult. | Card | 1160 | 480 | 96 | 180 | `[Gross Rent Multiplier]`. |
| 18 | Footnote | Text box | 28 | 692 | 1100 | 24 | "Cash-on-cash uses the what-if loan terms; cap rate uses the expense-ratio slider." |

> **Heads-up (real finding):** at 25% down / 7% / 45% expenses, cash-on-cash is **negative**
> across these metros at current prices vs. rents — these are appreciation plays, not
> cash-flow plays. Keep the negative red; it's the honest result and the reason the sliders exist.

---

## Interaction layer (after both pages are placed)

1. **Drill-through:** on Page 2, Format → Page information → Allow use as drill-through,
   add `dim_region[metro]` as the drill field. Right-click any metro on Page 1 → *Drill
   through → Market Detail*. A Back button is created automatically.
2. **Nav buttons:** add two Buttons (Insert → Buttons → Blank) top-left of each page,
   "Ranking" / "Detail", action = Page navigation. Use the theme's actionButton style.
3. **Custom tooltip page:** new page, Page size = **Tooltip** (320×240), Allow use as tooltip
   = On; add a mini price line + 2 cards. On Page 1's map/table set Format → Tooltip →
   Type = Report page → that page.
4. **Edit interactions:** select the map → *Format → Edit interactions* → set the trend
   charts to **Filter** and cards to **Filter**; curate the rest (don't let everything
   cross-filter everything).
5. **Tab order / alt text:** Selection pane → set logical tab order per page; give each
   chart Alt text. Ensure temperature is conveyed by **data bars + number**, not color alone.

---

## QA checklist before Publish

- [ ] Theme imported; every visual has the white card + 8px border + soft shadow.
- [ ] All measures formatted on the measure (currency 0dp, % 1dp, GRM/supply 1dp).
- [ ] No default titles ("Sum of…"); titles left-aligned, 11pt semibold.
- [ ] Raw fact columns hidden in the model; only measures in the Fields pane.
- [ ] `Last Updated` + source credits visible on Page 1.
- [ ] Every edge snapped to the 8px grid; KPI cards pixel-identical.
- [ ] `(Blank)` not leaking in cards/tables.
- [ ] Drill-through, nav buttons, custom tooltip all work.

Then **File → Publish → Publish to web (public)** → copy the link, capture 5 screenshots
into `docs/img/`, and hand both back for Steps C/D.
