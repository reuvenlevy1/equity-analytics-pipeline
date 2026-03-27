select
    date,
    ticker,
    sector,
    close,
    ma_20d,
    ma_50d,
    daily_return_pct
from {{ ref('fact_daily_prices') }}
