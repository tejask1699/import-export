// server.js
const express = require("express");
const path = require("path");
const session = require("express-session");
const bcrypt = require("bcrypt"); // optional, for password hashing
const con = require("./db");
const WeatherService = require("./weatherService");

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

        res.redirect("/weather.html");
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

// ===== WEATHER DASHBOARD =====
app.get("/weather.html", (req, res) => {
    if (!req.session.user) {
        return res.redirect("/login.html");
    }
    res.sendFile(path.join(__dirname, "templates", "weather.html"));
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

// ===== WEATHER ROUTES =====
// Get weather by city
app.get("/api/weather/:city", async (req, res) => {
    try {
        const { city } = req.params;
        const weatherData = await WeatherService.getWeatherByCity(city);
        const shippingRecommendation = WeatherService.getShippingRecommendation(weatherData);
        
        res.json({
            success: true,
            weather: weatherData,
            shipping: shippingRecommendation
        });
    } catch (error) {
        console.error("Weather API Error:", error.message);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// Get weather by coordinates
app.get("/api/weather/coordinates", async (req, res) => {
    try {
        const { lat, lon } = req.query;
        
        if (!lat || !lon) {
            return res.status(400).json({
                success: false,
                error: "Latitude and longitude are required"
            });
        }
        
        const weatherData = await WeatherService.getCurrentWeather(parseFloat(lat), parseFloat(lon));
        const shippingRecommendation = WeatherService.getShippingRecommendation(weatherData);
        
        res.json({
            success: true,
            weather: weatherData,
            shipping: shippingRecommendation
        });
    } catch (error) {
        console.error("Weather API Error:", error.message);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// Get weather forecast
app.get("/api/forecast/:city", async (req, res) => {
    try {
        const { city } = req.params;
        const weatherData = await WeatherService.getWeatherByCity(city);
        const forecastData = await WeatherService.getForecast(weatherData.coord.lat, weatherData.coord.lon);
        
        // Analyze forecast for shipping suitability
        const forecastAnalysis = forecastData.list.map(item => {
            const recommendation = WeatherService.getShippingRecommendation(item);
            return {
                datetime: new Date(item.dt * 1000),
                weather: item.weather[0].description,
                temp: item.main.temp,
                windSpeed: item.wind.speed,
                shipping: recommendation
            };
        });
        
        res.json({
            success: true,
            current: weatherData,
            forecast: forecastAnalysis
        });
    } catch (error) {
        console.error("Forecast API Error:", error.message);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// Check shipping eligibility
app.post("/api/check-shipping", async (req, res) => {
    try {
        const { city, lat, lon } = req.body;
        
        let weatherData;
        if (city) {
            weatherData = await WeatherService.getWeatherByCity(city);
        } else if (lat && lon) {
            weatherData = await WeatherService.getCurrentWeather(parseFloat(lat), parseFloat(lon));
        } else {
            return res.status(400).json({
                success: false,
                error: "City or coordinates are required"
            });
        }
        
        const shippingRecommendation = WeatherService.getShippingRecommendation(weatherData);
        
        res.json({
            success: true,
            location: weatherData.name,
            weather: {
                condition: weatherData.weather[0].description,
                temperature: weatherData.main.temp,
                windSpeed: weatherData.wind.speed,
                visibility: weatherData.visibility
            },
            shipping: shippingRecommendation
        });
    } catch (error) {
        console.error("Shipping Check Error:", error.message);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// ===== CREATE SHIPMENT =====
app.post("/create-shipment", async (req, res) => {
    try {

        const { origin, destination, payment, priority } = req.body;

        await con.query(
            "INSERT INTO shipments (origin, destination, payment, priority, status) VALUES (?, ?, ?, ?, ?)",
            [origin, destination, payment, priority, "Confirmed"]
        );

        res.send("Shipment successfully created");

    } catch (err) {
        console.error(err);
        res.status(500).send("Error creating shipment");
    }
});

// Start server
app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});

