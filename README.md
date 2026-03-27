# US Equity Analytics Pipeline


![GCP](https://img.shields.io/badge/GCP-4285F4?style=flat&logo=googlecloud&logoColor=white)
![Terraform](https://img.shields.io/badge/Terraform-7B42BC?style=flat&logo=terraform&logoColor=white)
![Kestra](https://img.shields.io/badge/Kestra-FF6B6B?style=flat)
![BigQuery](https://img.shields.io/badge/BigQuery-4285F4?style=flat&logo=googlebigquery&logoColor=white)
![dbt](https://img.shields.io/badge/dbt-FF694B?style=flat&logo=dbt&logoColor=white)
![Looker Studio](https://img.shields.io/badge/Looker_Studio-4285F4?style=flat&logo=looker&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)


## Problem Statement


[3-4 paragraphs: the business need, why equity data pipelines matter,
 tie-in to SMA/portfolio management context, what this project solves]


## Overview


[2-3 paragraphs: what the pipeline does end-to-end, what the dashboard shows]


## Table of Contents


[linked section headers]


## Tech Stack


| Component              | Technology           | Purpose |
|------------------------|----------------------|---------|
| Infrastructure as Code | Terraform            | Provisions the GCS data lake bucket and BigQuery datasets reproducibly. Any reviewer can recreate the full cloud infrastructure with three commands (`terraform init`, `terraform plan`, `terraform apply`). |
| Cloud Platform         | GCP                  | Hosts all infrastructure — object storage (GCS), analytical database (BigQuery), and authentication (IAM service accounts). |
| Data Lake              | Google Cloud Storage | Stores raw OHLCV data as Parquet files partitioned by ticker. Decouples ingestion from the warehouse — raw data survives independently of BigQuery. |
| Data Warehouse         | BigQuery             | Stores and queries structured equity data. Tables are partitioned by date and clustered by ticker and sector for query efficiency. |
| Transformation         | dbt Core             | Transforms raw BigQuery data through staging → marts → reporting layers. Applies moving averages, daily returns, and sector aggregations. Version-controlled SQL with built-in data quality tests. |
| Data Ingestion         | Python + yfinance    | Downloads daily OHLCV data for 33 US equities and SPY from Yahoo Finance. No API key required. |
| Environment Management | uv                   | Manages Python virtual environments and dependency locking. Ensures reproducible installs across local and containerized environments. |
| Version Control        | Git + GitHub         | Tracks all code changes. Required for zoomcamp project submission and peer review. |
| Orchestration          | Kestra               | Runs the 4-task pipeline DAG on a daily weekday schedule. Handles task dependencies, retries, and execution logging. |
| Containerization       | Docker               | Runs Kestra and its backing Postgres database in isolated containers. Ensures the orchestration layer is reproducible across machines. |
| Visualization | Looker Studio | Free BI tool with native BigQuery integration. Serves a two-tile dashboard — sector performance bar chart and stock price time series — directly from dbt reporting views. |


## Architecture


[Lucidchart/draw.io diagram: yfinance → GCS → BigQuery → dbt → Looker Studio]


## Project Structure


[folder tree with ├── formatting + 1-line explanation per file/folder]


## Data Source


**Library:** [yfinance](https://ranaroussi.github.io/yfinance/) — free, no API key required
**Date range:** 2020-01-01 to 2024-12-31 (configurable via `.env`)
**Universe:** 33 US equities (3 per GICS sector across all 11 sectors) + SPY benchmark
**Fields:** date, open, high, low, close, volume, ticker, sector
**Format:** Parquet — columnar, compressed, type-preserving
**Lake path:** gs://equity-analytics-pipeline-equity-lake/raw/equities/ticker={TICKER}/data.parquet


## Data Pipeline


### Ingestion


Daily OHLCV data for 33 US equities and SPY is downloaded from Yahoo Finance
via yfinance and uploaded to GCS as Parquet files. One file per ticker, stored
at `raw/equities/ticker={TICKER}/data.parquet` using Hive-style partitioning.


### Data Lake


Raw Parquet files land in the GCS bucket
`equity-analytics-pipeline-equity-lake`. This decouples ingestion from the
warehouse — raw data is preserved independently of BigQuery and can be
reloaded without re-fetching from yfinance.


### Data Warehouse


Parquet files are loaded from GCS into BigQuery as `equity_raw.ohlcv_raw`,
then a partitioned and clustered version is created as
`equity_raw.ohlcv_partitioned`. See BigQuery: Partitioning & Clustering below.


### Transformation


dbt Core transforms raw data through three layers. See dbt Models below.


### Orchestration


The pipeline is orchestrated by [Kestra](https://kestra.io/) running in Docker.
A single flow (`kestra/flows/equity_pipeline.yml`) defines a 4-task DAG that
runs automatically at 6 AM UTC every weekday:


1. **ingest** — downloads OHLCV data from yfinance, uploads Parquet files to GCS
2. **load_to_bq** — loads Parquet files from GCS into BigQuery raw tables
3. **dbt_run** — executes all dbt models (staging → marts → reporting)
4. **dbt_test** — runs data quality tests on all transformed tables


Tasks execute sequentially — each must complete successfully before the next
starts. If any task fails, Kestra halts execution and downstream tasks do not
run on bad data.


Each task runs in an isolated Docker container (`python:3.12-slim` for ingestion,
`ghcr.io/dbt-labs/dbt-bigquery:1.8.0` for transformation) with dependencies
installed fresh per execution.


![Kestra DAG](images/kestra_dag.png)


### Visualization


Looker Studio connects directly to BigQuery and queries the reporting
layer views (`rpt_sector_performance`, `rpt_ticker_timeseries`) on demand.
No data export or intermediate step is required. The dashboard updates
automatically after each daily Kestra pipeline run.


## BigQuery: Partitioning & Clustering


The raw BigQuery table (`equity_raw.ohlcv_partitioned`) is:
- **Partitioned by:** `date` — daily partitions (DATE column, no wrapper needed)
- **Clustered by:** `ticker`, then `sector`


**Why partition by date?**
Every query in this pipeline — in dbt models and in the dashboard — filters by
date range. BigQuery uses the partition boundary to skip entire days it doesn't
need to scan. A query for the last 30 days reads ~30 partitions instead of
the full table, reducing bytes scanned and query cost proportionally.


**Why cluster by ticker and sector?**
The dashboard and dbt models almost always GROUP BY or filter on ticker and sector.
Clustering physically co-locates rows with the same ticker value in storage,
so BigQuery reads a contiguous block of data for a given ticker rather than
scanning the entire partition. For a 33-ticker dataset this reduces bytes
scanned per query by approximately 1/33 when filtering on a single ticker.


The dbt fact table (`equity_analytics.fact_daily_prices`) uses the same
partitioning and clustering strategy, applied via dbt's `config()` macro.


## dbt Models


Transformations use dbt Core with the BigQuery adapter across three layers:


**Staging** (`equity_analytics.stg_ohlcv`) — view
Reads from `equity_raw.ohlcv_partitioned`. Casts types, filters invalid
prices, and computes `daily_return_pct` using a LAG window function.


**Marts**
- `dim_tickers` (table) — distinct ticker/sector combinations
- `fact_daily_prices` (table) — prices, daily returns, 20-day and 50-day
  moving averages. Partitioned by date, clustered by ticker and sector.


**Reporting**
- `rpt_sector_performance` (view) — sector-level daily return aggregations,
  feeds Dashboard Tile 1
- `rpt_ticker_timeseries` (view) — price and moving average per ticker,
  feeds Dashboard Tile 2


![dbt Lineage](images/dbt_lineage.png)


## Dashboard


Two-tile Looker Studio dashboard connected directly to BigQuery:


**Tile 1 — Average Daily Return by GICS Sector**
Bar chart showing average daily return percentage per sector across the
selected date range. Allows comparison of sector performance relative to
the S&P 500 benchmark (SPY).


**Tile 2 — Stock Price with 20-Day Moving Average**
Time series showing daily close price and 20-day moving average for a
selected ticker. Moving average is pre-computed by dbt in
`fact_daily_prices` and served via `rpt_ticker_timeseries`.


![Dashboard](images/dashboard.png)


[View live dashboard](https://lookerstudio.google.com/reporting/1520a3de-3182-4253-9643-2a2fe92b8a08)


## Data Quality & Testing


dbt generic tests run as Task 4 in the Kestra DAG after every dbt run:


| Test | Model | Guards against |
|------|-------|----------------|
| `not_null` on date, ticker | `stg_ohlcv`, `fact_daily_prices` | Missing primary keys |
| `unique` on ticker | `dim_tickers` | Duplicate dimension entries |
| `unique_combination_of_columns` (date+ticker) | `fact_daily_prices` | Duplicate fact rows |
| `accepted_values` on sector | source `ohlcv_partitioned` | Invalid sector names from ingestion |


If any test fails, Kestra halts and the dashboard is not updated with bad data.


## Steps to Reproduce


A Makefile at the project root provides shortcut commands for all operations.
Run `make help` to see all available commands after completing setup.


**Prerequisites:**
- WSL2 (Ubuntu-22.04) with uv, Git, gcloud CLI, Terraform, and Docker Desktop installed
- A GCP account with billing enabled
- Copy `.env.example` to `.env` and fill in your values


1. **Clone the repository**
   ```bash
   git clone https://github.com/reuvenlevy1/equity-analytics-pipeline.git
   cd equity-analytics-pipeline
   ```


2. **Install dependencies**
   ```bash
   make setup
   ```


3. **GCP setup** — create a service account, download credentials JSON,
   save as `gcp-credentials.json` in the project root (see Phase 0 notes)


4. **Provision infrastructure**
   ```bash
   make infra
   ```


5. **Configure environment** — copy `.env.example` to `.env` and fill in values


6. **Run the full pipeline**
   ```bash
   make pipeline
   ```


7. **Start Kestra** (for scheduled execution)
   ```bash
   make up
   make deploy-flow
   ```
   Then open http://localhost:8080 and trigger a manual execution to verify.


8. **View the dashboard**
   Open the live Looker Studio report: [Dashboard link](https://lookerstudio.google.com/reporting/1520a3de-3182-4253-9643-2a2fe92b8a08)


## Acknowledgements


[DataTalks.Club | yfinance / Yahoo Finance | dbt Labs]
