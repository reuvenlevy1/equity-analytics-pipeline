{{
    config(
        partition_by = {
            'field': 'date',
            'data_type': 'date'
        },
        cluster_by = ['ticker', 'sector']
    )
}}

with base as (
    select * from {{ ref('stg_ohlcv') }}
),

with_moving_averages as (
    select
        date,
        ticker,
        sector,
        open,
        high,
        low,
        close,
        volume,
        daily_return_pct,

        -- 20-day moving average
        round(avg(close) over (
            partition by ticker
            order by date
            rows between 19 preceding and current row
        ), 4) as ma_20d,

        -- 50-day moving average
        round(avg(close) over (
            partition by ticker
            order by date
            rows between 49 preceding and current row
        ), 4) as ma_50d

    from base
)

select * from with_moving_averages
