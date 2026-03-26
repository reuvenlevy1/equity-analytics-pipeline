from google.cloud import bigquery, storage
import pandas as pd
import io
import os
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID  = os.getenv("PROJECT_ID")
DATASET_RAW = os.getenv("DATASET_RAW")
BUCKET_NAME = os.getenv("BUCKET_NAME")
PREFIX      = os.getenv("PREFIX", "raw/equities/")
TABLE_RAW   = "ohlcv_raw"
TABLE_OPT   = "ohlcv_partitioned"

SCHEMA = [
    bigquery.SchemaField("date",   "DATE"),
    bigquery.SchemaField("open",   "FLOAT64"),
    bigquery.SchemaField("high",   "FLOAT64"),
    bigquery.SchemaField("low",    "FLOAT64"),
    bigquery.SchemaField("close",  "FLOAT64"),
    bigquery.SchemaField("volume", "INT64"),
    bigquery.SchemaField("ticker", "STRING"),
    bigquery.SchemaField("sector", "STRING"),
]

def load_raw(bq: bigquery.Client, gcs: storage.Client) -> None:
    blobs = list(gcs.list_blobs(BUCKET_NAME, prefix=PREFIX))
    frames = []
    for blob in blobs:
        buf = io.BytesIO(blob.download_as_bytes())
        frames.append(pd.read_parquet(buf))


    df = pd.concat(frames, ignore_index=True)
    df["date"] = pd.to_datetime(df["date"])


    table_ref = f"{PROJECT_ID}.{DATASET_RAW}.{TABLE_RAW}"
    job_config = bigquery.LoadJobConfig(
        schema=SCHEMA,
        write_disposition="WRITE_TRUNCATE",
    )
    bq.load_table_from_dataframe(df, table_ref, job_config=job_config).result()
    print(f"Loaded {len(df):,} rows → {table_ref}")

def create_partitioned(bq: bigquery.Client) -> None:
    src = f"{PROJECT_ID}.{DATASET_RAW}.{TABLE_RAW}"
    dst = f"{PROJECT_ID}.{DATASET_RAW}.{TABLE_OPT}"
    sql = f"""
        CREATE OR REPLACE TABLE `{dst}`
        PARTITION BY date
        CLUSTER BY ticker, sector
        AS SELECT * FROM `{src}`
    """
    bq.query(sql).result()
    print(f"Created partitioned table → {dst}")

def main():
    bq  = bigquery.Client(project=PROJECT_ID)
    gcs = storage.Client()
    load_raw(bq, gcs)
    create_partitioned(bq)

if __name__ == "__main__":
    main()
