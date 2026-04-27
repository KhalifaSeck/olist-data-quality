with source as (
    select * from raw.order_reviews
),

renamed as (
    select
        review_id::text                     as review_id,
        order_id::text                      as order_id,
        review_score::integer               as score,

        -- Indicateurs de présence (au lieu de stocker le texte brut)
        case when review_comment_title is not null
            then true else false
        end                                 as has_title,
        case when review_comment_message is not null
            then true else false
        end                                 as has_message,

        review_creation_date::timestamp     as created_at,
        review_answer_timestamp::timestamp  as answered_at
    from source
)

select * from renamed