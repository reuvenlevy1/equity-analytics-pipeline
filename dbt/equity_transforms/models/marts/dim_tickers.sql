select distinct
    ticker,
    sector
from {{ ref('stg_ohlcv') }}
order by sector, ticker
