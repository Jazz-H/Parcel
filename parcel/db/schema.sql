-- Parcel star schema (SQLite). Re-runnable: drops and recreates.

DROP TABLE IF EXISTS fact_market;
DROP TABLE IF EXISTS fact_listing;
DROP TABLE IF EXISTS dim_region;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS meta;

CREATE TABLE dim_region (
    region_id               TEXT PRIMARY KEY,   -- CBSA code
    metro                   TEXT NOT NULL,
    city                    TEXT,
    state                   TEXT,
    is_anchor               INTEGER DEFAULT 0,
    population              INTEGER,
    median_household_income INTEGER,
    vacancy_rate            REAL
);

CREATE TABLE dim_date (
    date        TEXT PRIMARY KEY,   -- first of month, YYYY-MM-DD
    year        INTEGER NOT NULL,
    quarter     INTEGER NOT NULL,
    month       INTEGER NOT NULL,
    month_name  TEXT NOT NULL,
    year_month  TEXT NOT NULL       -- YYYY-MM
);

CREATE TABLE fact_market (
    region_id             TEXT NOT NULL REFERENCES dim_region(region_id),
    date                  TEXT NOT NULL REFERENCES dim_date(date),
    median_sale_price     REAL,
    price_per_sqft        REAL,
    median_rent           REAL,
    days_on_market        REAL,
    inventory             REAL,
    months_of_supply      REAL,
    price_cut_share       REAL,
    list_to_sale_ratio    REAL,
    rent_to_price         REAL,
    gross_rent_multiplier REAL,
    est_cap_rate          REAL,
    homes_sold            REAL,
    new_listings          REAL,
    sold_above_list       REAL,
    PRIMARY KEY (region_id, date)
);

CREATE INDEX idx_fact_market_date ON fact_market(date);

-- Stretch: deal screener listings (populated later via RentCast/SimplyRETS)
CREATE TABLE fact_listing (
    listing_id  TEXT PRIMARY KEY,
    region_id   TEXT REFERENCES dim_region(region_id),
    date_pulled TEXT,
    price       REAL,
    beds        INTEGER,
    baths       REAL,
    sqft        REAL,
    est_rent    REAL,
    status      TEXT
);

CREATE TABLE meta (
    key   TEXT PRIMARY KEY,
    value TEXT
);
