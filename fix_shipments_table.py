import mysql.connector

# Script to fix shipments table structure completely
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
    
    # Backup existing data
    print("📦 Backing up existing shipment data...")
    cursor.execute("SELECT * FROM shipments")
    existing_data = cursor.fetchall()
    print(f"   Found {len(existing_data)} existing records")
    
    # Get column names
    cursor.execute("DESCRIBE shipments")
    old_columns = [col[0] for col in cursor.fetchall()]
    print(f"   Existing columns: {old_columns}")
    
    # Drop and recreate the table with correct structure
    print("\n🔄 Recreating shipments table with correct structure...")
    cursor.execute("DROP TABLE IF EXISTS shipments")
    
    create_table_query = """
    CREATE TABLE shipments (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        origin VARCHAR(255) NOT NULL,
        destination VARCHAR(255) NOT NULL,
        payment_mode VARCHAR(50) NOT NULL,
        priority VARCHAR(50) NOT NULL DEFAULT 'Standard',
        status VARCHAR(50) DEFAULT 'pending',
        tracking_number VARCHAR(50) UNIQUE,
        weather_origin_data TEXT,
        weather_destination_data TEXT,
        shipping_decision TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """
    cursor.execute(create_table_query)
    print("✅ New shipments table created successfully")
    
    # Restore any compatible data
    if existing_data and len(old_columns) >= 5:
        print("\n📥 Restoring compatible data...")
        for row in existing_data:
            try:
                # Map old data to new structure
                user_id = row[old_columns.index('user_id')] if 'user_id' in old_columns else 1
                origin = row[old_columns.index('origin')] if 'origin' in old_columns else 'Unknown'
                destination = row[old_columns.index('destination')] if 'destination' in old_columns else 'Unknown'
                payment_mode = row[old_columns.index('payment_mode')] if 'payment_mode' in old_columns else 'Online'
                status = row[old_columns.index('status')] if 'status' in old_columns else 'pending'
                
                # Generate tracking number for restored data
                import random
                import datetime
                tracking_number = f"TRK-{datetime.datetime.now().year}-{random.randint(1000, 9999)}"
                
                insert_query = """
                INSERT INTO shipments (user_id, origin, destination, payment_mode, priority, status, tracking_number) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_query, (user_id, origin, destination, payment_mode, 'Standard', status, tracking_number))
                
            except Exception as e:
                print(f"   ⚠️ Could not restore row: {e}")
        
        db.commit()
        print("✅ Data restoration completed")
    
    cursor.close()
    db.close()
    
    print("\n🎉 Shipments table structure fixed successfully!")
    print("✅ Priority column added")
    print("✅ Tracking number column added")
    print("✅ All required columns are now available")
    
except Exception as e:
    print(f"❌ Database fix error: {e}")
    print("Make sure MySQL is running and your credentials are correct.")
