with source as (
    select * from raw.geolocation
),

-- Moyenne lat/lng par zip_code pour éliminer les doublons
deduplicated as (
    select
        geolocation_zip_code_prefix             as zip_code,
        avg(geolocation_lat::numeric)           as latitude,
        avg(geolocation_lng::numeric)           as longitude,
        max(geolocation_city)                   as city,
        max(geolocation_state)                  as state
    from source
    group by geolocation_zip_code_prefix
)

select * from deduplicated