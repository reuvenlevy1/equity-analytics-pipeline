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


[table: Component | Technology | Purpose — 2-sentence justification per tool]


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


[partitioned by DATE(date), clustered by ticker and sector — explain WHY]


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
