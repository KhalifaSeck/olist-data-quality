with sellers as (
    select * from {{ ref('stg_sellers') }}
),

items as (
    select
        seller_id,
        count(distinct order_id)    as total_orders,
        sum(price)                  as total_revenue,
        avg(price)                  as avg_price
    from {{ ref('stg_order_items') }}
    group by seller_id
)

select
    s.seller_id,
    s.zip_code,
    s.city,
    s.state,
    coalesce(i.total_orders, 0)     as total_orders,
    coalesce(i.total_revenue, 0)    as total_revenue,
    coalesce(i.avg_price, 0)        as avg_price
from sellers s
left join items i using (seller_id)