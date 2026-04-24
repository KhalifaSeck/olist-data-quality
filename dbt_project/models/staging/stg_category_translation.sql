with source as (
    select * from raw.category_translation
),

renamed as (
    select
        product_category_name::text         as category_name_portuguese,
        product_category_name_english::text as category_name_english
    from source
)

select * from renamed