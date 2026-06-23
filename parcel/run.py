"""Parcel end-to-end refresh: ingest -> transform -> load -> stamp.

Degrades gracefully: if Zillow (rent) is unreachable, builds a price-side database and
leaves rent-derived columns null. Re-run once the network allowlist includes Zillow.

Usage:
    python -m parcel.run [--force] [--no-zillow]
"""
from __future__ import annotations

import argparse

from .config import load_config
from .db.load import load
from .ingest import redfin as redfin_ingest
from .ingest import zillow as zillow_ingest
from .transform.clean import clean_redfin
from .transform.geo import build_dim_region
from .transform.metrics import build_fact_market


def main(force: bool = False, use_zillow: bool = True) -> None:
    cfg = load_config()
    sources = 1  # Redfin

    # --- Ingest + clean Redfin (required) ---
    redfin_raw = redfin_ingest.load_raw(cfg, force=force)
    redfin = clean_redfin(redfin_raw)

    # --- Ingest Zillow (rent) — optional / network-gated ---
    zillow = None
    if use_zillow:
        try:
            zillow = zillow_ingest.load_raw(cfg, force=force)
            sources += 1
        except Exception as err:
            print(f"[warn] Zillow ingest skipped ({err}). "
                  f"Building price-side DB; rent metrics will be null.")

    # --- Transform ---
    expense_ratio = cfg.metrics.get("expense_ratio", 0.45)
    fact_market = build_fact_market(redfin, zillow, expense_ratio=expense_ratio)
    dim_region = build_dim_region(cfg, present_ids=set(fact_market["region_id"]))

    # --- Load ---
    load(cfg.path("db_path"), fact_market, dim_region, sources=sources)
    print("[done] refresh complete.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Parcel ETL refresh")
    ap.add_argument("--force", action="store_true", help="re-download sources, ignore cache")
    ap.add_argument("--no-zillow", action="store_true", help="skip Zillow rent ingest")
    args = ap.parse_args()
    main(force=args.force, use_zillow=not args.no_zillow)
