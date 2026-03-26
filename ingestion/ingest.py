import yfinance as yf
import pandas as pd
from google.cloud import storage
from dotenv import load_dotenv
import io
import os

load_dotenv()

BUCKET_NAME = os.getenv("BUCKET_NAME")
START_DATE  = os.getenv("START_DATE")
END_DATE    = os.getenv("END_DATE")

TICKERS = {
    "AAPL": "Technology",      "MSFT": "Technology",   "NVDA": "Technology",
    "JPM":  "Financials",      "BAC":  "Financials",   "GS":   "Financials",
    "JNJ":  "Health Care",     "UNH":  "Health Care",  "PFE":  "Health Care",
    "XOM":  "Energy",          "CVX":  "Energy",       "COP":  "Energy",
    "AMZN": "Cons. Discret.",  "TSLA": "Cons. Discret.","HD":  "Cons. Discret.",
    "PG":   "Cons. Staples",   "KO":   "Cons. Staples","WMT":  "Cons. Staples",
    "CAT":  "Industrials",     "BA":   "Industrials",  "HON":  "Industrials",
    "LIN":  "Materials",       "APD":  "Materials",    "ECL":  "Materials",
    "AMT":  "Real Estate",     "PLD":  "Real Estate",  "CCI":  "Real Estate",
    "NEE":  "Utilities",       "DUK":  "Utilities",    "SO":   "Utilities",
    "GOOGL":"Comm. Services",  "META": "Comm. Services","VZ":  "Comm. Services",
    "SPY":  "Benchmark",
}

def download_ticker(ticker: str, sector: str) -> pd.DataFrame | None:
    """Download OHLCV data for a ticker with retries and MultiIndex handling."""
    for attempt in range(3):
        df = yf.download(
            ticker,
            start=START_DATE,
            end=END_DATE,
            auto_adjust=True,
            progress=False
        )

        # Must be a DataFrame
        if not isinstance(df, pd.DataFrame):
            continue

        # Must not be empty
        if df.empty:
            continue

        # Flatten MultiIndex columns if needed
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = ["_".join(col).strip() for col in df.columns]
        
        # Strip ticker suffix (e.g., Close_AAPL → Close)
        df.columns = [col.split("_")[0] for col in df.columns]

        # Normalize schema
        df = df.reset_index()
        df.columns = [c.lower() for c in df.columns]
        df["ticker"] = ticker
        df["sector"] = sector

        return df

    # All attempts failed — skip this ticker
    return None

def upload_parquet(df: pd.DataFrame, ticker: str, client: storage.Client) -> None:
    buffer = io.BytesIO()
    df.to_parquet(buffer, index=False, engine="pyarrow")
    buffer.seek(0)
    blob_path = f"raw/equities/ticker={ticker}/data.parquet"
    bucket = client.bucket(BUCKET_NAME)
    bucket.blob(blob_path).upload_from_file(buffer, content_type="application/octet-stream")
    print(f"Uploaded {ticker} → gs://{BUCKET_NAME}/{blob_path}")

def main():
    gcs = storage.Client()
    for ticker, sector in TICKERS.items():
        df = download_ticker(ticker, sector)
        upload_parquet(df, ticker, gcs)

if __name__ == "__main__":
    main()
