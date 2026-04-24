with customers as (
    select * from {{ ref('stg_customers') }}
),

orders as (
    select
        customer_id,
        count(distinct order_id)    as total_orders,
        min(purchased_at)           as first_order_date,
        max(purchased_at)           as last_order_date
    from {{ ref('stg_orders') }}
    group by customer_id
)

select
    c.customer_id,
    c.unique_customer_id,
    c.zip_code,
    c.city,
    c.state,
    coalesce(o.total_orders, 0)     as total_orders,
    o.first_order_date,
    o.last_order_date
from customers c
left join orders o using (customer_id)