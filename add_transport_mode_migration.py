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
    
    print("Adding transport_mode column to shipments table...")
    cursor.execute("ALTER TABLE shipments ADD COLUMN transport_mode VARCHAR(50) DEFAULT 'Road';")
    
    db.commit()
    print("Column added successfully!")
    
except mysql.connector.Error as err:
    if err.errno == 1060: # Duplicate column name
        print("Column transport_mode already exists.")
    else:
        print(f"Error: {err}")
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'db' in locals():
        db.close()
