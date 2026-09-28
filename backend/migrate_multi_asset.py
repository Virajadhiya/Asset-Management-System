import sqlite3

def run_migration():
    con = sqlite3.connect('pravi.db')
    cur = con.cursor()

    def add_col(table, col, col_type):
        try:
            cur.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}")
            print(f"Added {col} to {table}")
        except Exception as e:
            print(f"{table}.{col}: {e}")

    add_col('bridges', 'asset_type', "VARCHAR DEFAULT 'BRIDGE'")
    add_col('bridge_engineering', 'tunnel_type', "VARCHAR")
    add_col('bridge_engineering', 'bore_diameter', "FLOAT")
    add_col('bridge_engineering', 'ventilation_system', "VARCHAR")
    add_col('bridge_engineering', 'pavement_type', "VARCHAR")
    add_col('bridge_engineering', 'carriageway_width', "FLOAT")
    add_col('bridge_engineering', 'culvert_type', "VARCHAR")
    add_col('bridge_engineering', 'opening_span', "FLOAT")
    add_col('bridge_engineering', 'clear_height', "FLOAT")

    cur.execute("UPDATE bridges SET asset_type = 'BRIDGE' WHERE asset_type IS NULL OR asset_type = ''")
    con.commit()
    con.close()
    print("Migration completed successfully!")

if __name__ == "__main__":
    run_migration()
