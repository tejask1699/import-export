import mysql.connector

# Script to validate and fix priority column issues
try:
    db = mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password="root",
        database="ai_shipping",
        charset="utf8",
        collation="utf8_general_ci"
    )
    
    cursor = db.cursor()
    
    # Check shipments table structure
    cursor.execute("DESCRIBE shipments")
    columns = cursor.fetchall()
    
    print("📋 Current shipments table structure:")
    for column in columns:
        print(f"  - {column[0]}: {column[1]}")
    
    # Check if priority column exists and has correct type
    priority_exists = False
    for column in columns:
        if column[0] == 'priority':
            priority_exists = True
            print(f"\n✅ Priority column found: {column[1]}")
            break
    
    if not priority_exists:
        print("\n❌ Priority column not found. Adding it...")
        alter_query = """
        ALTER TABLE shipments 
        ADD COLUMN priority VARCHAR(50) NOT NULL DEFAULT 'Standard' AFTER payment_mode
        """
        cursor.execute(alter_query)
        print("✅ Added 'priority' column to shipments table")
    
    # Test inserting a sample shipment to verify all columns work
    print("\n🧪 Testing shipment creation...")
    test_query = """
    INSERT INTO shipments (user_id, origin, destination, payment_mode, priority, status, tracking_number) 
    VALUES (1, 'Test Origin', 'Test Destination', 'Online', 'Standard', 'pending', 'TRK-TEST-001')
    """
    
    try:
        cursor.execute(test_query)
        db.commit()
        print("✅ Sample shipment created successfully")
        
        # Clean up test data
        cursor.execute("DELETE FROM shipments WHERE tracking_number = 'TRK-TEST-001'")
        db.commit()
        print("✅ Test data cleaned up")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        db.rollback()
    
    cursor.close()
    db.close()
    
    print("\n🎉 Priority column validation completed successfully!")
    
except Exception as e:
    print(f"❌ Database validation error: {e}")
    print("Make sure MySQL is running and your credentials are correct.")
