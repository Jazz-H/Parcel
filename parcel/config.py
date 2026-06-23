"""Configuration loader for Parcel.

Reads config.yml (and .env for optional API keys) and exposes a typed-ish view of
markets, source URLs, and paths used across the pipeline.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml

try:  # optional; .env is only needed for stretch enrichment
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # pragma: no cover
    pass

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config.yml"


@dataclass(frozen=True)
class Market:
    region_id: str
    name: str
    state: str
    anchor: bool = False


@dataclass(frozen=True)
class Config:
    markets: list[Market]
    sources: dict
    paths: dict
    metrics: dict = field(default_factory=dict)

    # --- convenience accessors -------------------------------------------------
    @property
    def cbsa_codes(self) -> set[str]:
        return {m.region_id for m in self.markets}

    @property
    def market_names(self) -> list[str]:
        return [m.name for m in self.markets]

    def path(self, key: str) -> Path:
        """Resolve a configured path relative to the repo root."""
        return ROOT / self.paths[key]


def load_config(path: Path | str = CONFIG_PATH) -> Config:
    with open(path, "r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)
    markets = [Market(**m) for m in raw["markets"]]
    return Config(
        markets=markets,
        sources=raw["sources"],
        paths=raw["paths"],
        metrics=raw.get("metrics", {}),
    )


def env(key: str, default: str | None = None) -> str | None:
    return os.environ.get(key, default)
