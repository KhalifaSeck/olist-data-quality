with products as (
    select * from {{ ref('stg_products') }}
)

select
    product_id,
    category_name,
    category_name_english,
    weight_g,
    length_cm,
    height_cm,
    width_cm,
    volume_cm3
from products