import duckdb
import sys

if len(sys.argv) < 2:
    print("Usage: python create_single_day_viewer_session.py <viewer_id>")
    sys.exit(1)

date = sys.argv[1]
table_date = date.replace("-","")

db_path = "DuckDB/sessions.duckdb"
conn = duckdb.connect(db_path)

conn.execute(f"DROP TABLE IF EXISTS viewer_{table_date}_sessions")

conn.execute(f"""
CREATE TABLE viewer_{table_date}_sessions AS
SELECT tv_day, channel_id, viewer_id, session_start, session_finish, session_duration, model_version, device_id, session_id, delivery_id, resolution_id, session_source, timeshifted_start, target_groups
FROM viewer_sessions
where tv_day = '{date}'
and model_version = '4.30.2_spin+at.20250829113426'
""")

conn.commit()
conn.close()