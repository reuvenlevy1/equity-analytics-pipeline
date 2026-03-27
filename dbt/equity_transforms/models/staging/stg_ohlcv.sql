with source as (
    select * from {{ source('equity_raw', 'ohlcv_partitioned') }}
),

renamed as (
    select
        date,
        ticker,
        sector,
        cast(open  as float64) as open,
        cast(high  as float64) as high,
        cast(low   as float64) as low,
        cast(close as float64) as close,
        cast(volume as int64)  as volume,

        -- Daily return percentage vs previous trading day
        round(
            safe_divide(
                close - lag(close) over (partition by ticker order by date),
                lag(close) over (partition by ticker order by date)
            ) * 100,
        4) as daily_return_pct

    from source
    where close is not null
      and close > 0
)

select * from renamed
