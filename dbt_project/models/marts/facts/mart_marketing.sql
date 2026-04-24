with leads as (
    select * from {{ ref('stg_marketing_leads') }}
),

deals as (
    select * from {{ ref('stg_closed_deals') }}
)

select
    l.lead_id,
    l.first_contact_date,
    l.origin,
    l.landing_page_id,
    case when d.lead_id is not null
        then true else false
    end                             as is_converted,
    d.won_date,
    d.business_segment,
    d.lead_type,
    d.business_type,
    d.monthly_revenue,
    extract(epoch from (
        d.won_date - l.first_contact_date::timestamp
    ))/86400                        as days_to_convert
from leads l
left join deals d using (lead_id)