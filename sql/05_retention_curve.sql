WITH user_first_events AS (
    SELECT u.user_id, u."group", MIN(e.event_date) as first_event_date
    FROM users u
    LEFT JOIN events e ON u.user_id = e.user_id
    GROUP BY u.user_id, u."group"
),
retention_by_day AS (
    SELECT
        ufe."group",
        -- Subtract dates to get the exact day number (1 = first day)
        (e.event_date - ufe.first_event_date) + 1 as day_number,
        COUNT(DISTINCT ufe.user_id) as users_active
    FROM user_first_events ufe
    LEFT JOIN events e ON ufe.user_id = e.user_id
    WHERE e.event_date >= ufe.first_event_date
    GROUP BY ufe."group", day_number
),
cohort_sizes AS (
    SELECT "group", COUNT(*) as total_users
    FROM users
    GROUP BY "group"
)
SELECT
    r."group",
    r.day_number,
    r.users_active,
    c.total_users as cohort_size,
    ROUND(100.0 * r.users_active / c.total_users, 2) as retention_pct
FROM retention_by_day r
JOIN cohort_sizes c ON r."group" = c."group"
WHERE r.day_number BETWEEN 1 AND 30
ORDER BY r."group", r.day_number;