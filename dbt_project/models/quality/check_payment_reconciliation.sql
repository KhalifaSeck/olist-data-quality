-- Commandes livrées sans paiement associé
select
    o.order_id,
    o.order_status,
    o.purchased_at,
    'delivered_order_no_payment'    as anomaly_type,
    'critical'                      as severity
from {{ ref('stg_orders') }} o
left join {{ ref('stg_order_payments') }} p using (order_id)
where o.order_status = 'delivered'
  and p.order_id is null