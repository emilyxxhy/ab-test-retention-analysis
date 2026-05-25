-- SCRIPT 4: CALCULATE STRICT L28 RETENTION BY SEGMENT (Region & OS)
WITH user_first_events AS (
    SELECT
        u.user_id,
        u."group",
        u.device_os,  -- <-- We grab the OS
        u.region,     -- <-- We grab the Region
        MIN(e.event_date) as first_event_date
    FROM users u
    LEFT JOIN events e ON u.user_id = e.user_id
    GROUP BY u.user_id, u."group", u.device_os, u.region
),
l28_check AS (
    SELECT
        ufe.user_id,
        ufe."group",
        ufe.device_os,
        ufe.region,
        MAX(CASE 
            WHEN e.event_date = ufe.first_event_date + INTERVAL '28 days' 
            THEN 1 
            ELSE 0 
        END) as returned_l28
    FROM user_first_events ufe
    LEFT JOIN events e ON ufe.user_id = e.user_id
    GROUP BY ufe.user_id, ufe."group", ufe.device_os, ufe.region
)
SELECT
    "group",
    region,      
    device_os,    
    COUNT(*) as cohort_size,
    SUM(returned_l28) as returned_count,
    ROUND(100.0 * SUM(returned_l28) / COUNT(*), 2) as l28_retention_pct
FROM l28_check
GROUP BY "group", region, device_os
ORDER BY "group", region, device_os;