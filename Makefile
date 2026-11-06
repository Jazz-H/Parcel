.PHONY: install install-dev lint format test refresh refresh-force sample clean

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt -r requirements-dev.txt

# Lint and formatting, same checks CI runs.
lint:
	ruff check .
	black --check .

format:
	ruff check --fix .
	black .

test:
	pytest -q

# Full ETL refresh: ingest -> transform -> load -> stamp last_updated.
refresh:
	python -m parcel.run

# Re-download sources, ignoring the on-disk cache.
refresh-force:
	python -m parcel.run --force

# Regenerate the committed sample artifacts from the freshly built DB.
sample: refresh
	cp db/parcel.sqlite data/sample/parcel_sample.sqlite
	python -c "import sqlite3,pandas as pd; c=sqlite3.connect('db/parcel.sqlite'); \
pd.read_sql('select * from fact_market',c).to_csv('data/sample/fact_market.csv',index=False); \
pd.read_sql('select * from dim_region',c).to_csv('data/sample/dim_region.csv',index=False)"

clean:
	rm -f db/parcel.sqlite
	rm -rf data/raw/*
