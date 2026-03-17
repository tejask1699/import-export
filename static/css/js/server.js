// server.js
const express = require("express");
const path = require("path");
const session = require("express-session");
const bcrypt = require("bcrypt"); // optional, for password hashing
const con = require("./db");

const app = express();
const PORT = 3000;

// Middleware
app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(express.static(path.join(__dirname, "public")));
app.use(
    session({
        secret: "your_secret_key",
        resave: false,
        saveUninitialized: true,
    })
);

// ===== REGISTER =====
app.post("/register", async (req, res) => {
    try {
        const { name, email, password } = req.body;

        // Optional: hash password
        const hashedPassword = await bcrypt.hash(password, 10);

        // Insert user into DB
        await con.query(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            [name, email, hashedPassword]
        );

        res.redirect("/login.html");
    } catch (err) {
        console.error("REGISTER ERROR:", err.message);
        res.send("Error registering user: " + err.message);
    }
});

// ===== LOGIN =====
app.post("/login", async (req, res) => {
    try {
        const { email, password } = req.body;

        const [rows] = await con.query(
            "SELECT * FROM users WHERE email = ?",
            [email]
        );

        if (rows.length === 0) {
            return res.send("Invalid email or password");
        }

        const user = rows[0];

        // Compare password if using bcrypt
        const match = await bcrypt.compare(password, user.password);
        if (!match) {
            return res.send("Invalid email or password");
        }

        // Set session
        req.session.user = {
            id: user.id,
            name: user.name,
            email: user.email,
        };

        res.redirect("/dashboard.html");
    } catch (err) {
        console.error("LOGIN ERROR:", err.message);
        res.send("Error logging in: " + err.message);
    }
});

// ===== DASHBOARD =====
app.get("/dashboard.html", (req, res) => {
    if (!req.session.user) {
        return res.redirect("/login.html");
    }
    res.sendFile(path.join(__dirname, "public", "dashboard.html"));
});

// ===== LOGOUT =====
app.get("/logout", (req, res) => {
    req.session.destroy((err) => {
        if (err) {
            console.error(err);
        }
        res.redirect("/login.html");
    });
});

// Start server
app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});