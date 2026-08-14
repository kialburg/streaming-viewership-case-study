import sqlite3
import os
from pathlib import Path

def combine_databases():
    """Combine multiple SQLite database files into a single consolidated database using ATTACH DATABASE."""
    
    db_dir = Path("SQLite-db")
    
    # List of database files to combine
    db_files = [
        "digital_sessions.db",
        "target_group_mappings.db",
        "viewer_sessions.db",
        "viewer_weights.db"
    ]
    
    output_db = db_dir / "combined.db"
    
    # Remove existing combined database if it exists
    if output_db.exists():
        os.remove(output_db)
        print(f"Removed existing combined database: {output_db}")
    
    # Create connection to output database
    output_conn = sqlite3.connect(str(output_db))
    output_cursor = output_conn.cursor()
    
    # Enable faster writes
    output_cursor.execute("PRAGMA journal_mode = WAL")
    output_cursor.execute("PRAGMA synchronous = NORMAL")
    
    print(f"\nCombining databases into: {output_db}\n")
    
    table_summary = {}
    
    # Process each input database
    for idx, db_file in enumerate(db_files, 1):
        db_path = db_dir / db_file
        
        if not db_path.exists():
            print(f"⚠ Skipping {db_file} - file not found")
            continue
        
        print(f"Processing {db_file}:")
        
        # Attach the source database
        attach_alias = f"db{idx}"
        output_cursor.execute(f"ATTACH DATABASE '{str(db_path)}' AS {attach_alias}")
        
        # Get list of tables in the attached database
        output_cursor.execute(f"SELECT name FROM {attach_alias}.sqlite_master WHERE type='table'")
        tables = output_cursor.fetchall()
        
        if not tables:
            print("  No tables found")
            output_cursor.execute(f"DETACH DATABASE {attach_alias}")
            continue
        
        # Copy each table to the main database
        for table in tables:
            table_name = table[0]
            
            # Get row count
            output_cursor.execute(f"SELECT COUNT(*) FROM {attach_alias}.{table_name}")
            row_count = output_cursor.fetchone()[0]
            
            # Check if table already exists in main database
            output_cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            exists = output_cursor.fetchone()
            
            if not exists:
                # Create table using schema from attached database
                output_cursor.execute(f"SELECT sql FROM {attach_alias}.sqlite_master WHERE type='table' AND name='{table_name}'")
                create_sql = output_cursor.fetchone()[0]
                output_cursor.execute(create_sql)
                
                # Copy all data at once
                output_cursor.execute(f"INSERT INTO {table_name} SELECT * FROM {attach_alias}.{table_name}")
            else:
                # Table exists, append data
                output_cursor.execute(f"INSERT INTO {table_name} SELECT * FROM {attach_alias}.{table_name}")
            
            table_summary[table_name] = table_summary.get(table_name, 0) + row_count
            print(f"  ✓ {table_name}: {row_count:,} rows")
        
        # Commit all changes and detach the database
        output_conn.commit()
        output_cursor.execute(f"DETACH DATABASE {attach_alias}")

    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Summary of combined database: {output_db}")
    print(f"{'='*60}")
    
    total_rows = 0
    
    for table_name, row_count in sorted(table_summary.items()):
        total_rows += row_count
        print(f"  {table_name}: {row_count:,} rows")
    
    print(f"\nTotal tables: {len(table_summary)}")
    print(f"Total rows across all tables: {total_rows:,}")
    print(f"\nCombined database saved to: {output_db}")
    
    output_conn.close()


if __name__ == "__main__":
    combine_databases()
