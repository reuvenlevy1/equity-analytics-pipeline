select
    date,
    sector,
    round(avg(daily_return_pct), 4) as avg_daily_return_pct,
    round(avg(close), 4)            as avg_close,
    sum(volume)                     as total_volume
from {{ ref('fact_daily_prices') }}
group by date, sector
