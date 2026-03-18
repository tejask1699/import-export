import mysql.connector

# Database setup script with shipments table
try:
    # Connect to MySQL without specifying database
    db = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="root@1699",
        # charset="utf8",
        # collation="utf8_general_ci"
    )
    
    cursor = db.cursor()
    
    # Create database if it doesn't exist
    cursor.execute("CREATE DATABASE IF NOT EXISTS ai_shipping")
    cursor.execute("USE ai_shipping")
    
    # Create users table if it doesn't exist
    create_users_table = """
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'user') DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""
    cursor.execute("""
ALTER TABLE users 
ADD COLUMN role ENUM('admin', 'user') DEFAULT 'user'
""")
    
    # Create shipments table if it doesn't exist
    create_shipments_table = """
    CREATE TABLE IF NOT EXISTS shipments (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        origin VARCHAR(255) NOT NULL,
        destination VARCHAR(255) NOT NULL,
        payment_mode VARCHAR(50) NOT NULL,
        priority VARCHAR(50) NOT NULL,
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
    cursor.execute(create_shipments_table)
    
    print("Database setup completed successfully!")
    print("Database 'ai_shipping', 'users' and 'shipments' tables created/verified.")
    
    cursor.close()
    db.close()
    
except Exception as e:
    print(f"Database setup error: {e}")
    print("Make sure MySQL is running and your credentials are correct.")
