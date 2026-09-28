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

    # Maintenance columns
    add_col('maintenance_records', 'estimated_by', "CHAR(32)")
    add_col('maintenance_records', 'sanction_number', "VARCHAR")
    add_col('maintenance_records', 'sanctioned_amount', "FLOAT")
    add_col('maintenance_records', 'tender_number', "VARCHAR")
    add_col('maintenance_records', 'work_order_number', "VARCHAR")
    add_col('maintenance_records', 'tender_value', "FLOAT")
    add_col('maintenance_records', 'assigned_contractor', "VARCHAR")

    # Inspection proof & geofence columns
    add_col('inspections', 'inspector_gps_latitude', "FLOAT")
    add_col('inspections', 'inspector_gps_longitude', "FLOAT")
    add_col('inspections', 'geofence_distance_meters', "FLOAT")
    add_col('inspections', 'geofence_verified', "BOOLEAN DEFAULT 1")
    add_col('inspections', 'photo_evidence_url', "VARCHAR")
    add_col('inspections', 'counter_signed_by', "CHAR(32)")
    add_col('inspections', 'counter_signed_at', "TIMESTAMP")
    add_col('inspections', 'verification_remarks', "TEXT")

    # Distress issues table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS distress_issues (
        id CHAR(32) PRIMARY KEY,
        bridge_id CHAR(32) NOT NULL,
        title VARCHAR NOT NULL,
        description TEXT,
        source VARCHAR NOT NULL DEFAULT 'FIELD_SCOUT',
        severity VARCHAR NOT NULL DEFAULT 'HIGH',
        photo_url VARCHAR,
        status VARCHAR NOT NULL DEFAULT 'OPEN',
        assigned_inspector_id CHAR(32),
        assigned_engineer_id CHAR(32),
        target_date TIMESTAMP,
        reported_by_name VARCHAR,
        reported_by_id CHAR(32),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        resolved_at TIMESTAMP,
        FOREIGN KEY (bridge_id) REFERENCES bridges (id),
        FOREIGN KEY (assigned_inspector_id) REFERENCES users (id),
        FOREIGN KEY (assigned_engineer_id) REFERENCES users (id)
    )
    """)
    print("Created distress_issues table if not exists")

    con.commit()
    con.close()
    print("Government workflow migration completed successfully!")

if __name__ == "__main__":
    run_migration()
