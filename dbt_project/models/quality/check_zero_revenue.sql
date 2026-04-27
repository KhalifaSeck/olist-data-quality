-- Règle métier : commande livrée doit avoir un revenu > 0
select
    order_id,
    order_status,
    revenue,
    'zero_revenue_delivered_order'  as anomaly_type,
    'critical'                      as severity
from {{ ref('fct_orders') }}
where order_status = 'delivered'
  and (revenue is null or revenue = 0)