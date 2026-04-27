-- Règle métier : pas de doublons dans order_items
select
    order_id,
    item_seq,
    count(*)                        as occurrence_count,
    'duplicate_order_item'          as anomaly_type,
    'warning'                       as severity
from {{ ref('stg_order_items') }}
group by order_id, item_seq
having count(*) > 1