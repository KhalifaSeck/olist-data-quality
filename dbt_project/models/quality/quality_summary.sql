-- Vue consolidée de toutes les anomalies détectées
select
    current_timestamp               as checked_at,
    anomaly_type,
    severity,
    count(*)                        as violation_count
from (
    select anomaly_type, severity
    from {{ ref('check_order_consistency') }}
    union all
    select anomaly_type, severity
    from {{ ref('check_zero_revenue') }}
    union all
    select anomaly_type, severity
    from {{ ref('check_duplicate_items') }}
    union all
    select anomaly_type, severity
    from {{ ref('check_orphan_orders') }}
    union all
    select anomaly_type, severity
    from {{ ref('check_negative_prices') }}
    union all
    select anomaly_type, severity
    from {{ ref('check_stale_orders') }}
    union all
    select anomaly_type, severity
    from {{ ref('check_payment_reconciliation') }}
) all_anomalies
group by anomaly_type, severity
order by
    case severity
        when 'critical' then 1
        when 'warning'  then 2
        else 3
    end,
    violation_count desc
