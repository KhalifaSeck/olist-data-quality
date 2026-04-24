with source as (
    select * from raw.order_items
),

renamed as (
    select
        order_id::text          as order_id,
        order_item_id::integer  as item_seq,
        product_id::text        as product_id,
        seller_id::text         as seller_id,
        price::numeric          as price,
        freight_value::numeric  as freight_value
    from source
)

select * from renamed