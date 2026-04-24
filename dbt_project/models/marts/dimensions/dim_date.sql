with date_spine as (
    select generate_series(
        '2016-01-01'::date,
        '2019-12-31'::date,
        '1 day'::interval
    )::date as date_day
)

select
    date_day                                        as date_day,
    extract(year  from date_day)::integer           as year,
    extract(month from date_day)::integer           as month,
    extract(day   from date_day)::integer           as day,
    extract(week  from date_day)::integer           as week_of_year,
    extract(quarter from date_day)::integer         as quarter,
    to_char(date_day, 'Month')                      as month_name,
    to_char(date_day, 'Day')                        as day_name,
    case when extract(isodow from date_day) in (6,7)
        then true else false end                    as is_weekend,
    date_trunc('week',  date_day)::date             as week_start,
    date_trunc('month', date_day)::date             as month_start,
    date_trunc('quarter', date_day)::date           as quarter_start
from date_spine