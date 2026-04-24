select
    purchase_date,
    purchase_week,
    purchase_month,
    order_status,
    count(distinct order_id)        as order_count,
    count(distinct customer_id)     as customer_count,
    sum(revenue)                    as revenue,
    sum(freight_total)              as freight_total,
    sum(order_total)                as total_gmv,
    avg(revenue)                    as avg_order_value,
    avg(avg_score)                  as avg_review_score
from {{ ref('fct_orders') }}
group by 1, 2, 3, 4