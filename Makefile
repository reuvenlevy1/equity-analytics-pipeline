.PHONY: help setup infra up down ingest load transform test pipeline deploy-flow

PROJECT_DIR := /opt/equity-pipeline
DBT_DIR     := $(PROJECT_DIR)/dbt/equity_transforms

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Install Python dependencies
	uv sync
	uv pip install -r ingestion/requirements.txt
	uv pip install python-dotenv

infra: ## Provision GCP infrastructure via Terraform
	cd $(PROJECT_DIR)/terraform && terraform init && terraform apply -auto-approve

up: ## Start Kestra and Postgres via Docker Compose
	docker compose up -d

down: ## Stop all Docker services
	docker compose down

ingest: ## Run yfinance ingestion -- downloads OHLCV and uploads to GCS
	uv run python $(PROJECT_DIR)/ingestion/ingest.py

load: ## Load GCS Parquet files into BigQuery and create partitioned table
	uv run python $(PROJECT_DIR)/ingestion/load_to_bq.py

transform: ## Run all dbt models (staging -> marts -> reporting)
	cd $(DBT_DIR) && uv run dbt run --profiles-dir .

test: ## Run dbt data quality tests
	cd $(DBT_DIR) && uv run dbt test --profiles-dir .

pipeline: ingest load transform test ## Run full pipeline: ingest -> load -> transform -> test

deploy-flow: ## Deploy Kestra flow via API (requires Kestra running on localhost:8080)
	curl -X POST http://localhost:8080/api/v1/flows/import \
		-u 'YOUR_KESTRA_EMAIL:YOUR_KESTRA_PASSWORD' \
		-F fileUpload=@$(PROJECT_DIR)/kestra/flows/equity_pipeline.yml
