with orders as (
    select * from {{ ref('stg_orders') }}
),

payments as (
    select
        order_id,
        sum(payment_value)                      as total_payment,
        count(distinct payment_type)            as payment_methods,
        max(installments)                       as max_installments,
        mode() within group (order by payment_type) as main_payment_type
    from {{ ref('stg_order_payments') }}
    group by order_id
),

items as (
    select
        order_id,
        count(item_seq)         as item_count,
        sum(price)              as revenue,
        sum(freight_value)      as freight_total
    from {{ ref('stg_order_items') }}
    group by order_id
),

reviews as (
    select
        order_id,
        avg(score)::numeric(3,2)    as avg_score,
        count(review_id)            as review_count
    from {{ ref('stg_order_reviews') }}
    group by order_id
)

select
    o.order_id,
    o.customer_id,
    o.order_status,
    o.purchased_at,
    o.approved_at,
    o.shipped_at,
    o.delivered_at,
    o.estimated_delivery_at,
    o.purchased_at::date                        as purchase_date,
    date_trunc('week',  o.purchased_at)::date   as purchase_week,
    date_trunc('month', o.purchased_at)::date   as purchase_month,

    -- Délais
    extract(epoch from (o.approved_at - o.purchased_at))/3600   as hours_to_approve,
    extract(epoch from (o.shipped_at  - o.approved_at))/3600    as hours_to_ship,
    extract(epoch from (o.delivered_at - o.shipped_at))/86400   as days_to_deliver,
    extract(epoch from (o.estimated_delivery_at - o.delivered_at))/86400 as days_early_late,

    -- Items
    coalesce(i.item_count, 0)       as item_count,
    coalesce(i.revenue, 0)          as revenue,
    coalesce(i.freight_total, 0)    as freight_total,
    coalesce(i.revenue, 0) + coalesce(i.freight_total, 0) as order_total,

    -- Paiements
    coalesce(p.total_payment, 0)    as total_payment,
    p.main_payment_type,
    coalesce(p.max_installments, 1) as max_installments,

    -- Avis
    r.avg_score,
    coalesce(r.review_count, 0)     as review_count

from orders o
left join items    i using (order_id)
left join payments p using (order_id)
left join reviews  r using (order_id)