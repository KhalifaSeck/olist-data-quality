-- Règle métier : prix ne peut pas être négatif ou nul
select
    order_id,
    product_id,
    price,
    'negative_or_zero_price'        as anomaly_type,
    'critical'                      as severity
from {{ ref('stg_order_items') }}
where price <= 0