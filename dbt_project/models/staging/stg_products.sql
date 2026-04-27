with source as (
    select * from raw.products
),

translation as (
    select * from raw.category_translation
),

-- Moyenne des dimensions par catégorie pour remplir les nulls
category_avg as (
    select
        product_category_name,
        avg(product_weight_g::numeric)      as avg_weight,
        avg(product_length_cm::numeric)     as avg_length,
        avg(product_height_cm::numeric)     as avg_height,
        avg(product_width_cm::numeric)      as avg_width
    from source
    where product_weight_g is not null
    group by product_category_name
),

cleaned as (
    select
        p.product_id::text                                          as product_id,

        -- Catégorie : null → "unknown"
        coalesce(p.product_category_name, 'unknown')::text         as category_name,

        -- Traduction anglaise
        coalesce(t.product_category_name_english,
                 p.product_category_name,
                 'unknown')::text                                   as category_name_english,

        -- Dimensions : null → moyenne de la catégorie
        coalesce(p.product_weight_g::numeric,
                 ca.avg_weight)                                     as weight_g,
        coalesce(p.product_length_cm::numeric,
                 ca.avg_length)                                     as length_cm,
        coalesce(p.product_height_cm::numeric,
                 ca.avg_height)                                     as height_cm,
        coalesce(p.product_width_cm::numeric,
                 ca.avg_width)                                      as width_cm,

        -- Volume calculé
        coalesce(p.product_length_cm::numeric, ca.avg_length) *
        coalesce(p.product_height_cm::numeric, ca.avg_height) *
        coalesce(p.product_width_cm::numeric,  ca.avg_width)        as volume_cm3

    from source p
    left join translation t
        on p.product_category_name = t.product_category_name
    left join category_avg ca
        on p.product_category_name = ca.product_category_name
)

select * from cleaned