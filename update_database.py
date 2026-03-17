import mysql.connector

# Script to add tracking_number column to existing shipments table
try:
    db = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="Tejas@1699",
        # charset="utf8",
        # collation="utf8_general_ci"
    )
    
    cursor = db.cursor()
    
    # Check if tracking_number column exists
    cursor.execute("SHOW COLUMNS FROM shipments LIKE 'tracking_number'")
    result = cursor.fetchone()
    
    if not result:
        # Add the missing tracking_number column
        alter_query = """
        ALTER TABLE shipments 
        ADD COLUMN tracking_number VARCHAR(50) UNIQUE AFTER status
        """
        cursor.execute(alter_query)
        print("✅ Added 'tracking_number' column to shipments table")
    else:
        print("✅ 'tracking_number' column already exists")
    
    cursor.close()
    db.close()
    
    print("Database column update completed successfully!")
    
except Exception as e:
    print(f"Database update error: {e}")
    print("Make sure MySQL is running and your credentials are correct.")
