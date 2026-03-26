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
| Data Ingestion         | Python + yfinance    | Downloads daily OHLCV data for 33 US equities and SPY from Yahoo Finance. No API key required. |
| Environment Management | uv                   | Manages Python virtual environments and dependency locking. Ensures reproducible installs across local and containerized environments. |
| Version Control        | Git + GitHub         | Tracks all code changes. Required for zoomcamp project submission and peer review. |


## Architecture


[Lucidchart/draw.io diagram: yfinance → GCS → BigQuery → dbt → Looker Studio]


## Project Structure


[folder tree with ├── formatting + 1-line explanation per file/folder]


## Data Source


[what yfinance is, which tickers, date range, fields: OHLCV + sector]


## Data Pipeline


[subsections per stage: Ingestion → Data Lake → Data Warehouse →
 Transformation → Orchestration → Visualization]
[include: Kestra DAG screenshot, dbt lineage screenshot]


## BigQuery: Partitioning & Clustering


Raw data is loaded into the `equity_raw` dataset provisioned by Terraform.
Partitioning and clustering details are covered in Phase 4.


## dbt Models


[staging → marts → reporting layer names and what each model computes]
[include dbt DAG lineage image]


## Dashboard


[2 screenshots: sector bar chart tile + price time series tile]
[link to live Looker Studio report]


## Data Quality & Testing


[dbt generic tests: not_null, unique, accepted_values on sector]


## Steps to Reproduce


[numbered ~8-10 steps, every shell command copy-pasteable]
1. Prerequisites
2. Clone repo
3. GCP setup + service account
4. Terraform init/apply
5. Configure .env
6. Run ingestion script
7. Load to BigQuery
8. Run dbt models
9. Open Looker Studio


## Acknowledgements


[DataTalks.Club | yfinance / Yahoo Finance | dbt Labs]
