-- Règle métier : toute commande doit avoir un client associé
select
    o.order_id,
    o.customer_id,
    o.purchased_at,
    'orphan_order_no_customer'      as anomaly_type,
    'critical'                      as severity
from {{ ref('stg_orders') }} o
left join {{ ref('stg_customers') }} c using (customer_id)
where c.customer_id is null