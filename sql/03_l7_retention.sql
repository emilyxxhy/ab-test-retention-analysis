-- SCRIPT 3: CALCULATE L7 RETENTION (STRICT/BOUNDED)
-- 1. Find each user's FIRST event date (their activation date)
-- 2. For each user, check if they had an event EXACTLY 7 days later
-- 3. Calculate % of users in each group who "returned"

WITH user_first_events AS (
    SELECT
        u.user_id,
        u."group",
        MIN(e.event_date) as first_event_date
    FROM users u
    LEFT JOIN events e ON u.user_id = e.user_id
    GROUP BY u.user_id, u."group"
),
l7_check AS (
    SELECT
        ufe.user_id,
        ufe."group",
        MAX(CASE 
            -- We changed this from >= to = so we only count exact Day 7 returns!
            WHEN e.event_date = ufe.first_event_date + INTERVAL '7 days' 
            THEN 1 
            ELSE 0 
        END) as returned_l7
    FROM user_first_events ufe
    LEFT JOIN events e ON ufe.user_id = e.user_id
    GROUP BY ufe.user_id, ufe."group"
)
SELECT
    "group",
    COUNT(*) as cohort_size,
    SUM(returned_l7) as returned_count,
    ROUND(100.0 * SUM(returned_l7) / COUNT(*), 2) as l7_retention_pct,
    ROUND(
        1.96 * SQRT((SUM(returned_l7)::NUMERIC / COUNT(*)) * (1 - SUM(returned_l7)::NUMERIC / COUNT(*)) / COUNT(*)) * 100,
        2
    ) as ci_margin_of_error
FROM l7_check
GROUP BY "group"
ORDER BY "group";