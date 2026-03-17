# Google Maps API Setup Guide

## 🗺️ How to Get Google Maps API Key

### Step 1: Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account
3. Click "Select a project" → "NEW PROJECT"
4. Enter project name (e.g., "AI Shipping System")
5. Click "CREATE"

### Step 2: Enable Maps JavaScript API
1. In the Google Cloud Console, go to "APIs & Services" → "Library"
2. Search for "Maps JavaScript API"
3. Click on it and click "ENABLE"
4. Also enable "Geocoding API" and "Places API" (optional but recommended)

### Step 3: Create API Key
1. Go to "APIs & Services" → "Credentials"
2. Click "+ CREATE CREDENTIALS" → "API key"
3. Copy the generated API key
4. **IMPORTANT**: Restrict the API key for security:
   - Click on the API key name
   - Under "API restrictions", select "Restrict key"
   - Select "Maps JavaScript API"
   - Add "Geocoding API" and "Places API" if enabled
   - Under "Application restrictions", select "HTTP referrers"
   - Add: `http://127.0.0.1:5000/*` and `http://localhost:5000/*`
   - Click "SAVE"

### Step 4: Update the Code
Replace line 511 in tracking.html:
```javascript
script.src = 'https://maps.googleapis.com/maps/api/js?key=YOUR_ACTUAL_API_KEY_HERE&callback=initMap';
```

### Step 5: Test the Map
1. Restart your Flask app
2. Go to http://127.0.0.1:5000/tracking
3. The map should now load with live tracking

## 🔧 Quick Fix (For Testing Only)

If you want to test immediately, you can use this temporary approach:

1. Open tracking.html
2. Find line 511
3. Replace `YOUR_GOOGLE_MAPS_API_KEY` with a real API key from Google Cloud Console

## 📱 Alternative: OpenStreetMap (Free)

If you don't want to use Google Maps, I can implement OpenStreetMap which is free and doesn't require an API key.

Would you like me to:
1. Help you set up Google Maps API key?
2. Implement OpenStreetMap as a free alternative?
3. Create a demo map without API key?

## 🚨 Important Notes

- Google Maps API has a free tier (28,500 map loads per month)
- Beyond that, it costs approximately $7 per 1,000 additional map loads
- Always restrict your API key to prevent unauthorized usage
- Never commit API keys to public repositories
