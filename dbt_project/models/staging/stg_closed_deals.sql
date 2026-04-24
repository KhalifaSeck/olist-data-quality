with source as (
    select * from raw.closed_deals
),

renamed as (
    select
        mql_id::text                    as lead_id,
        seller_id::text                 as seller_id,
        sdr_id::text                    as sdr_id,
        sr_id::text                     as sr_id,
        won_date::timestamp             as won_date,
        business_segment::text          as business_segment,
        lead_type::text                 as lead_type,
        lead_behaviour_profile::text    as behaviour_profile,
        has_company::boolean            as has_company,
        has_gtin::boolean               as has_gtin,
        average_stock::text             as average_stock,
        business_type::text             as business_type,
        declared_product_catalog_size::numeric  as catalog_size,
        declared_monthly_revenue::numeric       as monthly_revenue
    from source
)

select * from renamed