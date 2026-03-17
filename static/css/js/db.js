// db.js
const mysql = require("mysql2");

// Create a connection pool
const pool = mysql.createPool({
    host: "localhost",
    user: "root",
    password: "your_password",  // change to your DB password
    database: "ai_shipping"
});

// Wrap with promise() to use async/await
const con = pool.promise();

module.exports = con;