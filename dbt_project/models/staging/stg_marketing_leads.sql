with source as (
    select * from raw.marketing_leads
),

renamed as (
    select
        mql_id::text                as lead_id,
        first_contact_date::date    as first_contact_date,
        landing_page_id::text       as landing_page_id,
        origin::text                as origin
    from source
)

select * from renamed