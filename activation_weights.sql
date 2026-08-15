-- SQLite

--Do I need to add logic for this instruction?
--Prefer synthetic viewer that have not yet been activated on the current broadcast day. 

WITH cte AS
(SELECT 
session_start AS ts, target_group, channel_id, 1 AS change
FROM digital_20250904_sessions

UNION ALL 

SELECT
session_finish AS ts, target_group, channel_id, -1 AS change
FROM digital_20250904_sessions
)

SELECT 
ts,
target_group,
channel_id,
CASE WHEN change = 1 THEN 'start' ELSE 'end' END AS session_event,
session_id
-- SUM(change) OVER 
-- (PARTITION BY 
--     target_group, channel_id 
-- ORDER BY ts 
-- ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW ) as channel_weight,
-- SUM(change) OVER 
-- (PARTITION BY target_group ORDER BY ts ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW ) as target_group_weight
FROM cte

order by ts
;