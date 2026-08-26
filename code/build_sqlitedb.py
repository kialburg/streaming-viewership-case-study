import duckdb
import glob
import pandas as pd
from decimal import Decimal

def build_table(table_name, files):

    # Create DuckDB database
    db_path = "DuckDB/sessions.duckdb"
    conn = duckdb.connect(db_path)

    # Process files in batches of 8
    batch_size = 8
    for i in range(0, len(files), batch_size):
        batch_files = files[i:i+batch_size]
        
        # Read and concatenate parquet files in this batch
        dfs = [pd.read_parquet(file) for file in batch_files]
        df_batch = pd.concat(dfs, ignore_index=True)

        # Convert Decimal columns to float
        for col in df_batch.columns:
            if df_batch[col].dtype == 'object':
                try:
                    df_batch[col] = df_batch[col].apply(
                        lambda x: float(x) if isinstance(x, Decimal) else x
                    )
                except (ValueError, TypeError):
                    pass
        
        print(f"\n{table_name.replace('_', ' ').title()} Batch {i//batch_size + 1}:")
        print(f"  Shape: {df_batch.shape}")
        print(f"  Columns: {df_batch.columns.tolist()}")
        print(f"  Memory usage: {df_batch.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        
        # Write dataframe to DuckDB table
        is_first = (i == 0)
        conn.register("df_batch", df_batch)
        if is_first:
            conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM df_batch")
        else:
            conn.execute(f"INSERT INTO {table_name} SELECT * FROM df_batch")
        conn.unregister("df_batch")

    # Verify table creation
    row_count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
    print(f"\nDuckDB table created: {db_path}")
    print(f"  Table name: {table_name}")
    print(f"  Total rows: {row_count:,}")

    # Show column info
    columns_info = conn.execute(f"DESCRIBE {table_name}").fetchall()
    print(f"\nTable schema:")
    for col in columns_info:
        print(f"  {col[0]} ({col[1]})")

    conn.close()
    print(f"\nDatabase connection closed. File ready at: {db_path}")


tables = [
    'digital_sessions',
    'viewer_sessions',
    'viewer_weights',
    'target_group_mappings',
]

for table_name in tables:
    files = sorted(glob.glob(rf"bucket/{table_name}_*.parquet"))
    build_table(table_name, files)