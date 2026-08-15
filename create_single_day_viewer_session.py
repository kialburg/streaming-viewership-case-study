import sqlite3
import sys
from config import model_version

if len(sys.argv) < 2:
    print("Usage: python create_single_viewer_session.py <viewer_id>")
    sys.exit(1)

viewer_id = sys.argv[1]

db_path = "SQLite-db/sessions.db"
conn = sqlite3.connect(db_path)

conn.execute(f"DROP TABLE IF EXISTS viewer_{viewer_id}_sessions")

conn.execute(f"""
CREATE TABLE viewer_{viewer_id}_sessions AS
SELECT 
tv_day, channel_id, viewer_id, session_start, session_finish, session_duration, session_id
FROM viewer_sessions
WHERE 
viewer_id = '{viewer_id}'
and model_version = '{model_version}' --arbitrary choice
""")

conn.commit()
conn.close()