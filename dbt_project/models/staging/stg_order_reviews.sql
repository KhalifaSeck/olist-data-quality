with source as (
    select * from raw.order_reviews
),

renamed as (
    select
        review_id::text                     as review_id,
        order_id::text                      as order_id,
        review_score::integer               as score,
        review_comment_title::text          as title,
        review_comment_message::text        as message,
        review_creation_date::timestamp     as created_at,
        review_answer_timestamp::timestamp  as answered_at
    from source
)

select * from renamed