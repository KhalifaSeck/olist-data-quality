with products as (
    select * from {{ ref('stg_products') }}
),

translation as (
    select * from {{ ref('stg_category_translation') }}
)

select
    p.product_id,
    p.category_name,
    coalesce(t.category_name_english, p.category_name) as category_name_english,
    p.weight_g,
    p.length_cm,
    p.height_cm,
    p.width_cm,
    p.photos_qty
from products p
left join translation t
    on p.category_name = t.category_name_portuguese