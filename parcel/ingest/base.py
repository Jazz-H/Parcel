"""Shared download helpers: polite, cached, retrying HTTP fetch."""
from __future__ import annotations

import time
from pathlib import Path

import requests

USER_AGENT = "Parcel/0.1 (portfolio market-analytics project; contact via GitHub)"
DEFAULT_TIMEOUT = 180


def download(url: str, dest: Path, *, force: bool = False, retries: int = 4) -> Path:
    """Download ``url`` to ``dest`` with on-disk caching and exponential backoff.

    If ``dest`` already exists and ``force`` is False, the cached file is reused.
    """
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and not force:
        print(f"[cache] {dest.name} ({dest.stat().st_size:,} bytes)")
        return dest

    last_err: Exception | None = None
    for attempt in range(retries):
        try:
            print(f"[fetch] {url}")
            with requests.get(
                url, headers={"User-Agent": USER_AGENT}, stream=True, timeout=DEFAULT_TIMEOUT
            ) as resp:
                resp.raise_for_status()
                tmp = dest.with_suffix(dest.suffix + ".part")
                with open(tmp, "wb") as fh:
                    for chunk in resp.iter_content(chunk_size=1 << 20):
                        if chunk:
                            fh.write(chunk)
                tmp.replace(dest)
            print(f"[saved] {dest.name} ({dest.stat().st_size:,} bytes)")
            return dest
        except requests.HTTPError as err:
            # 4xx (except 429) are not transient — fail fast, don't burn backoff.
            status = err.response.status_code if err.response is not None else None
            if status is not None and 400 <= status < 500 and status != 429:
                raise RuntimeError(f"Download of {url} failed: HTTP {status}") from err
            last_err = err
            wait = 2 ** (attempt + 1)
            print(f"[retry] attempt {attempt + 1} failed: {err} — waiting {wait}s")
            time.sleep(wait)
        except Exception as err:  # network error
            last_err = err
            wait = 2 ** (attempt + 1)
            print(f"[retry] attempt {attempt + 1} failed: {err} — waiting {wait}s")
            time.sleep(wait)

    raise RuntimeError(f"Failed to download {url} after {retries} attempts") from last_err
