terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}
provider "google" {
  project = var.project_id
  region  = var.region
}

# GCS bucket — raw data lake
resource "google_storage_bucket" "data_lake" {
  name          = "${var.project_id}-equity-lake"
  location      = var.region
  force_destroy = true
  lifecycle_rule {
    condition { age = 30 }
    action    { type = "Delete" }
  }
}

# BigQuery dataset — raw ingested data
resource "google_bigquery_dataset" "raw" {
  dataset_id = "equity_raw"
  location   = var.region
}

# BigQuery dataset — dbt-transformed data
resource "google_bigquery_dataset" "analytics" {
  dataset_id = "equity_analytics"
  location   = var.region
}
