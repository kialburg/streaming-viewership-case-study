-- Viewer Integrity: 
-- Recreate logic for session_pivot to check session activation rules


with slide_activation_cte AS (
    select 
    *,
    SUM(COALESCE(start_of_session, 0)) OVER
        (PARTITION BY viewer_id order by ts 
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS session_index
from (
    select 
        *
    from (
        select 
            datetime(ts) AS ts, channel_id, viewer_id, target_group, 
            activation_flag, start_or_finish,
            CASE WHEN activation_flag = 1 THEN 1 END AS start_of_session,
            CASE WHEN activation_flag = -1 THEN 1 END AS end_of_session,
            session_id
        from output_sessions_20250904
        where viewer_id = '10631_24'
        )
    )
),
session_accumulation_cte AS (
SELECT
    viewer_id, target_group, channel_id, ts,
    activation_flag, end_of_session, session_id, 
    session_index, start_or_finish,
    vw.viewer_weight,
    cumulative_session_count,
    cumulative_session_ids
FROM (
    select * ,
    --Session IDs linked to a given active period.
    --Note: This can exceed the weight, since sessions will expire during active sessions.
    GROUP_CONCAT(session_id) OVER (
        PARTITION BY viewer_id, session_index
        ORDER BY ts
        ) AS cumulative_session_ids,
    -- Track number of session_ids accumulating, removing expired sessions from the count.
    SUM(start_or_finish) OVER (
        PARTITION BY viewer_id
        ORDER BY ts, session_id
        ) AS cumulative_session_count
    from slide_activation_cte
        ) sesh
LEFT JOIN (SELECT DISTINCT viewer, viewer_weight FROM viewer_weights) vw
    ON vw.viewer = sesh.viewer_id
)
-- select viewer_id, target_group, channel_id, ts,
--     activation_flag, end_of_session, session_id, 
--     start_of_new_session_links, session_index,
--     viewer_weight,
--     cumulative_session_count
--     from session_accumulation_cte;

select 
'over or under capacity' AS error, 
ts, viewer_id, session_index, target_group, channel_id,
viewer_weight, cumulative_session_count,
NULL AS prev_session_count,
activation_flag, 
start_or_finish, session_id,
cumulative_session_ids
from session_accumulation_cte
where cumulative_session_count > viewer_weight or cumulative_session_count < 0


-- Checking the activation logic is a bit trickier, multiple session links can happen in a single ts.
-- This makes it a challenge in SQL to find the  
-- I'll leave this work for later.
-- UNION ALL

-- select
-- -- 'faulty activation logic' AS error,
-- *
-- FROM
-- (SELECT ts, viewer_id, NULL AS session_index, target_group, channel_id,
-- viewer_weight, 
-- cumulative_session_count, 
-- lag(cumulative_session_count) OVER (PARTITION BY viewer_id order by ts) AS prev_session_count,
-- activation_flag,
-- NULL AS start_or_finish, NULL AS session_id,
-- NULL AS cumulative_session_ids
-- FROM (SELECT 
--     ts, viewer_id, target_group, channel_id, viewer_weight, cumulative_session_count,
--     MAX(CASE WHEN activation_flag <> 0 THEN 1 END) AS activation_flag
--     FROM session_accumulation_cte
--     group by 1,2,3,4,5,6)) 
-- where activation_flag = 1-- all flags are coerced to 1 for simplicity
-- AND (
--     (ROUND(viewer_weight * 0.5, 0) < cumulative_session_count
--     AND ROUND(viewer_weight * 0.5, 0) < prev_session_count)
--     OR 
--     (ROUND(viewer_weight * 0.5, 0) > cumulative_session_count
--     AND ROUND(viewer_weight * 0.5, 0) > prev_session_count)
--     )

;