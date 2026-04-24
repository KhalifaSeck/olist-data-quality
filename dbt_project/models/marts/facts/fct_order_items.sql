with items as (
    select * from {{ ref('stg_order_items') }}
),

orders as (
    select
        order_id,
        customer_id,
        order_status,
        purchased_at,
        purchase_date
    from {{ ref('fct_orders') }}
),

products as (
    select * from {{ ref('dim_products') }}
)

select
    i.order_id,
    i.item_seq,
    i.product_id,
    i.seller_id,
    o.customer_id,
    o.order_status,
    o.purchased_at,
    o.purchase_date,
    p.category_name_english     as category,
    i.price,
    i.freight_value,
    i.price + i.freight_value   as total_value
from items i
left join orders   o using (order_id)
left join products p using (product_id)