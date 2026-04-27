-- Règle métier : livraison ne peut pas précéder l'achat
select
    order_id,
    purchased_at,
    delivered_at,
    'delivered_before_purchased'    as anomaly_type,
    'critical'                      as severity
from {{ ref('stg_orders') }}
where delivered_at is not null
  and delivered_at < purchased_at