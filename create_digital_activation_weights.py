import sqlite3
import sys

if len(sys.argv) < 2:
    print("Usage: python create_single_viewer_session.py <viewer_id>")
    sys.exit(1)

date = sys.argv[1]
table_date = date.replace("-","")

db_path = "SQLite-db/sessions.db"
conn = sqlite3.connect(db_path)

conn.execute(f"DROP TABLE IF EXISTS digital_{table_date}_activation_weights")

conn.execute(f"""
CREATE TABLE digital_{table_date}_activation_weights AS
-- SQLite
WITH cte AS
(SELECT 
session_start AS ts, target_group, channel_id, 1 AS change
FROM digital_{table_date}_sessions

UNION ALL 

SELECT
session_finish AS ts, target_group, channel_id, -1 AS change
FROM digital_{table_date}_sessions
)

SELECT 
ts,
target_group,
channel_id,
SUM(change) OVER 
(PARTITION BY 
    target_group, channel_id 
ORDER BY ts 
ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW ) as channel_weight,
SUM(change) OVER 
(PARTITION BY target_group ORDER BY ts ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW ) as target_group_weight
FROM cte

order by ts
""")

conn.commit()
conn.close()