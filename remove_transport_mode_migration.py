import mysql.connector

try:
    db = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="Tejas@1699",
        database="ai_shipping"
    )
    cursor = db.cursor()
    
    print("Dropping transport_mode column from shipments table...")
    cursor.execute("ALTER TABLE shipments DROP COLUMN transport_mode;")
    
    db.commit()
    print("Column dropped successfully!")
    
except mysql.connector.Error as err:
    if err.errno == 1091: # Column doesn't exist
        print("Column transport_mode does not exist.")
    else:
        print(f"Error: {err}")
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'db' in locals():
        db.close()
