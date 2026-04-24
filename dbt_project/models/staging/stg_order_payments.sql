with source as (
    select * from raw.order_payments
),

renamed as (
    select
        order_id::text              as order_id,
        payment_sequential::integer as payment_seq,
        payment_type::text          as payment_type,
        payment_installments::integer as installments,
        payment_value::numeric      as payment_value
    from source
)

select * from renamed