with base as (
    select
        customer_id,
        max(purchase_date)                          as last_purchase_date,
        count(distinct order_id)                    as frequency,
        sum(revenue)                                as monetary,
        current_date - max(purchase_date)           as recency_days
    from {{ ref('fct_orders') }}
    where order_status = 'delivered'
    group by customer_id
),

scored as (
    select *,
        ntile(5) over (order by recency_days desc)  as r_score,
        ntile(5) over (order by frequency)          as f_score,
        ntile(5) over (order by monetary)           as m_score
    from base
)

select *,
    case
        when r_score >= 4 and f_score >= 4  then 'Champion'
        when r_score >= 3 and f_score >= 3  then 'Loyal'
        when r_score >= 3 and f_score < 3   then 'Potential'
        when r_score < 2                    then 'At Risk'
        else 'Needs Attention'
    end as segment
from scored