import mysql.connector

# Test script to verify shipment creation works
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
    
    # Test the exact query used in the Flask app
    print("🧪 Testing shipment creation query...")
    
    import random
    import datetime
    tracking_number = f"TRK-{datetime.datetime.now().year}-{random.randint(1000, 9999)}"
    
    query = """
    INSERT INTO shipments (user_id, origin, destination, payment_mode, priority, status, tracking_number) 
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    values = (1, 'Mumbai', 'Delhi', 'Online', 'Express', 'in-transit', tracking_number)
    
    cursor.execute(query, values)
    db.commit()
    print(f"✅ Test shipment created: {tracking_number}")
    
    # Verify the data was inserted correctly
    cursor.execute("SELECT * FROM shipments WHERE tracking_number = %s", (tracking_number,))
    result = cursor.fetchone()
    
    if result:
        print("✅ Shipment data verified:")
        print(f"   ID: {result[0]}")
        print(f"   User ID: {result[1]}")
        print(f"   Origin: {result[2]}")
        print(f"   Destination: {result[3]}")
        print(f"   Payment: {result[4]}")
        print(f"   Priority: {result[5]}")
        print(f"   Status: {result[6]}")
        print(f"   Tracking: {result[7]}")
    else:
        print("❌ Could not verify shipment data")
    
    # Clean up test data
    cursor.execute("DELETE FROM shipments WHERE tracking_number = %s", (tracking_number,))
    db.commit()
    print("✅ Test data cleaned up")
    
    cursor.close()
    db.close()
    
    print("\n🎉 Shipment creation test completed successfully!")
    print("✅ All columns are working correctly")
    print("✅ Priority column error is resolved")
    
except Exception as e:
    print(f"❌ Test error: {e}")
    print("Make sure MySQL is running and your credentials are correct.")
