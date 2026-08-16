-- SQLite
WITH current_broadcast_day_viewers AS (
SELECT DISTINCT viewer_id FROM viewer_sessions
)

select * from
(select demo, viewer_id, viewer_weight,
rank() OVER (
    PARTITION BY demo ORDER BY viewer_weight
    ) AS activation_order
from digital_viewer_mapping
)
order by activation_order