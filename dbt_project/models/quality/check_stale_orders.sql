-- Règle métier : commande expédiée depuis plus de 30 jours sans livraison
select
    order_id,
    order_status,
    purchased_at,
    shipped_at,
    current_date - shipped_at::date as days_since_shipped,
    'stale_shipped_order'           as anomaly_type,
    'warning'                       as severity
from {{ ref('stg_orders') }}
where order_status = 'shipped'
  and delivered_at is null
  and shipped_at < current_date - interval '30 days'