with source as (
    select * from raw.customers
),

renamed as (
    select
        customer_id::text           as customer_id,
        customer_unique_id::text    as unique_customer_id,
        customer_zip_code_prefix    as zip_code,
        customer_city               as city,
        customer_state              as state
    from source
)

select * from renamed