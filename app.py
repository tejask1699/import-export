from flask import Flask, request, render_template,redirect, url_for, session,send_file, jsonify
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from datetime import datetime
import io
import mysql.connector
import requests
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# OpenWeatherMap API
WEATHER_API_KEY = 'bf98922579d3a372232f5f1736ece285'
WEATHER_BASE_URL = 'https://api.openweathermap.org/data/2.5'
GEOCODE_URL = "https://nominatim.openstreetmap.org/search"

# MySQL connection with connection pooling
def get_db_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="Tejas@1699",
        database="ai_shipping",
        # charset="utf8",
        # collation="utf8_general_ci"
    )

@app.route("/")
def home():
    
    return render_template("login.html")
# 📁 app.py


@app.route("/reports")
def reports_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    return render_template("reports.html", role=session.get("user_role"))


@app.route("/api/user-reports")
def user_reports():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'})

    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 5))
    search = request.args.get('search', '')
    status = request.args.get('status', '')

    offset = (page - 1) * limit
    search_term = f"%{search}%"

    db_conn = get_db_connection()
    cursor = db_conn.cursor(dictionary=True)

    # 🔥 BASE QUERY (with JOIN)
    base_query = """
        FROM shipments s
        JOIN users u ON s.user_id = u.id
        WHERE 1=1
    """

    params = []

    # ✅ USER FILTER (only for normal users)
    if session.get('user_role') != 'admin':
        base_query += " AND s.user_id=%s"
        params.append(session['user_id'])

    # ✅ SEARCH
    base_query += """
        AND (
            s.tracking_number LIKE %s OR
            s.origin LIKE %s OR
            s.destination LIKE %s
        )
    """
    params.extend([search_term, search_term, search_term])

    # ✅ STATUS FILTER
    if status:
        base_query += " AND s.status=%s"
        params.append(status)

    # ✅ DATA QUERY (with user_name)
    data_query = """
        SELECT s.*, u.name as user_name
    """ + base_query + """
        ORDER BY s.created_at DESC
        LIMIT %s OFFSET %s
    """

    cursor.execute(data_query, (*params, limit, offset))
    shipments = cursor.fetchall()

    # ✅ COUNT QUERY (same filters, no need to select user fields)
    count_query = "SELECT COUNT(*) as total " + base_query
    cursor.execute(count_query, tuple(params))
    total = cursor.fetchone()['total']

    # ✅ STATS (role-based)
    if session.get('user_role') == 'admin':
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM shipments
            GROUP BY status
        """)
    else:
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM shipments
            WHERE user_id=%s
            GROUP BY status
        """, (session['user_id'],))

    stats_data = cursor.fetchall()

    stats = {
        "total": total,
        "in_transit": 0,
        "delivered": 0,
        "delayed": 0
    }

    for s in stats_data:
        if s['status'] == 'in-transit':
            stats['in_transit'] = s['count']
        elif s['status'] == 'delivered':
            stats['delivered'] = s['count']
        elif s['status'] == 'delayed':
            stats['delayed'] = s['count']

    cursor.close()
    db_conn.close()

    return jsonify({
        'success': True,
        'data': shipments,
        'stats': stats,
        'pagination': {
            'total': total,
            'page': page,
            'limit': limit,
            'pages': (total + limit - 1) // limit
        }
    })


@app.route("/register", methods=["POST"])
def register_db():
    name = request.form["name"]
    email = request.form["email"]
    password = request.form["password"]
    role = request.form.get("role", "user")  # default role

    db_conn = None
    cursor = None

    try:
        db_conn = get_db_connection()
        cursor = db_conn.cursor()

        query = """
        INSERT INTO users (name, email, password, role)
        VALUES (%s, %s, %s, %s)
        """
        values = (name, email, password, role)  # ✅ FIXED

        cursor.execute(query, values)
        db_conn.commit()

        return jsonify({"status": "success"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

    finally:
        if cursor:
            cursor.close()
        if db_conn:
            db_conn.close()

# Login Backend

@app.route('/login', methods=['POST'])
def login_db():
    email = request.form['email']
    password = request.form['password']

    try:
        db_conn = get_db_connection()
        cursor = db_conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()

        if user and user['password'] == password:
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_role'] = user['role']

            return jsonify({
                "status": "success",
                "role": user['role']
            })
        else:
            return jsonify({
                "status": "error",
                "message": "Invalid Email or Password"
            })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if session.get('user_role') != 'admin':
        return "Unauthorized", 403

    return render_template('adminDashboard.html')


# Shipping Page - Main import/export functionality
@app.route('/shipping')
def shipping():
    
    return render_template("shipping.html")


@app.route('/api/shipments')
def get_shipments():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    if session.get('user_role') != 'admin':
        return jsonify({'error': 'Forbidden'}), 403

    db_conn = get_db_connection()
    cursor = db_conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM shipments ORDER BY created_at DESC")
    shipments = cursor.fetchall()

    cursor.close()
    db_conn.close()

    return jsonify({"data": shipments})


@app.route('/create-shipment', methods=['POST'])
def create_shipment():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    db_conn = None
    cursor = None
    try:
        origin = request.form.get('origin')
        destination = request.form.get('destination')
        payment_mode = request.form.get('payment')
        priority = request.form.get('priority')
        
        # Generate tracking number
        import random
        import datetime
        tracking_number = f"TRK-{datetime.datetime.now().year}-{random.randint(1000, 9999)}"
        
        db_conn = get_db_connection()
        cursor = db_conn.cursor()
        query = "INSERT INTO shipments (user_id, origin, destination, payment_mode, priority, status, tracking_number) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        values = (session['user_id'], origin, destination, payment_mode, priority, 'in-transit', tracking_number)
        cursor.execute(query, values)
        db_conn.commit()
        
        return json.dumps({
            'success': True, 
            'tracking_number': tracking_number,
            'message': 'Shipment created successfully!'
        })
    except Exception as e:
        return json.dumps({
            'success': False,
            'error': str(e)
        })
    finally:
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if db_conn:
            try:
                db_conn.close()
            except:
                pass


# Weather Page with API integration
@app.route('/weather')
def weather():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template("weather.html")


# Weather API endpoints
@app.route('/api/weather/<city>')
def get_weather(city):
    try:
        url = f"{WEATHER_BASE_URL}/weather"
        params = {
            'q': city,
            'appid': WEATHER_API_KEY,
            'units': 'metric'
        }
        response = requests.get(url, params=params)
        data = response.json()
        
        # Add shipping recommendation
        shipping_recommendation = get_shipping_recommendation(data)
        
        return json.dumps({
            'success': True,
            'weather': data,
            'shipping': shipping_recommendation
        })
    except Exception as e:
        return json.dumps({
            'success': False,
            'error': str(e)
        })


@app.route('/api/weather/coordinates')
def get_weather_coordinates():
    try:
        lat = request.args.get('lat')
        lon = request.args.get('lon')
        
        if not lat or not lon:
            return json.dumps({
                'success': False,
                'error': 'Latitude and longitude are required'
            })
        
        url = f"{WEATHER_BASE_URL}/weather"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': WEATHER_API_KEY,
            'units': 'metric'
        }
        response = requests.get(url, params=params)
        data = response.json()
        
        shipping_recommendation = get_shipping_recommendation(data)
        
        return json.dumps({
            'success': True,
            'weather': data,
            'shipping': shipping_recommendation
        })
    except Exception as e:
        return json.dumps({
            'success': False,
            'error': str(e)
        })


def get_shipping_recommendation(weather_data):
    """AI-powered shipping recommendation based on weather conditions"""
    main = weather_data['weather'][0]['main'].lower()
    temp = weather_data['main']['temp']
    wind_speed = weather_data['wind']['speed']
    visibility = weather_data.get('visibility', 10000)
    rain = weather_data.get('rain', {}).get('1h', 0)
    snow = weather_data.get('snow', {}).get('1h', 0)
    
    # Dangerous conditions
    dangerous_conditions = ['thunderstorm', 'tornado', 'hurricane', 'extreme']
    
    if main in dangerous_conditions:
        return {
            'suitable': False,
            'reason': f'Dangerous weather condition: {main}',
            'risk': 'HIGH',
            'recommendation': ' Do not ship - Dangerous weather conditions',
            'action': 'CANCEL'
        }
    
    # Temperature extremes
    if temp < -10 or temp > 45:
        return {
            'suitable': False,
            'reason': f'Extreme temperature: {temp}°C',
            'risk': 'HIGH',
            'recommendation': ' Do not ship - Extreme temperature',
            'action': 'CANCEL'
        }
    
    # High wind
    if wind_speed > 20:
        return {
            'suitable': False,
            'reason': f'High wind speed: {wind_speed} m/s',
            'risk': 'MEDIUM',
            'recommendation': ' Delay shipping - Wait for better conditions',
            'action': 'DELAY'
        }
    
    # Poor visibility
    if visibility < 1000:
        return {
            'suitable': False,
            'reason': f'Poor visibility: {visibility}m',
            'risk': 'MEDIUM',
            'recommendation': ' Delay shipping - Poor visibility',
            'action': 'DELAY'
        }
    
    # Heavy rain/snow
    if rain > 10 or snow > 5:
        return {
            'suitable': False,
            'reason': f'Heavy precipitation: Rain {rain}mm/h, Snow {snow}mm/h',
            'risk': 'MEDIUM',
            'recommendation': ' Delay shipping - Heavy precipitation',
            'action': 'DELAY'
        }
    
    # Moderate conditions
    warnings = []
    risk = 'LOW'
    
    if wind_speed > 15:
        warnings.append(f'Moderate wind: {wind_speed} m/s')
        risk = 'MEDIUM'
    
    if rain > 2:
        warnings.append(f'Light to moderate rain: {rain}mm/h')
        risk = 'MEDIUM'
    
    if main in ['drizzle', 'mist', 'fog']:
        warnings.append(f'Reduced visibility due to {main}')
        risk = 'MEDIUM'
    
    if warnings:
        return {
            'suitable': True,
            'reason': ', '.join(warnings),
            'risk': risk,
            'recommendation': ' Proceed with caution - Monitor weather conditions',
            'action': 'CAUTION'
        }
    
    # Good conditions
    return {
        'suitable': True,
        'reason': 'Weather conditions are suitable for shipping',
        'risk': 'LOW',
        'recommendation': ' Proceed with shipping - Weather conditions are optimal',
        'action': 'PROCEED'
    }


@app.route("/dashboard")
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if session.get('user_role') == 'admin':
        return redirect(url_for('admin_dashboard'))

    return render_template("dashboard.html")


@app.route("/login")
def login():
    if 'user_id' in session:
        return redirect(url_for('weather'))
    return render_template("login.html")


@app.route("/logout")
def logout():
    
    session.clear()
    return redirect(url_for('login'))


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/demo-map")
def demo_map():
    return render_template("demo_map.html")


@app.route("/tracking")
def tracking():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template("tracking.html")


def get_coordinates(city: str) -> dict:
    """Convert city → lat/lng using OSM"""
    try:
        response = requests.get(
            GEOCODE_URL,
            params={
                "q": city,
                "format": "json",
                "limit": 1
            },
            headers={"User-Agent": "ai-shipping-app"}
        )

        data = response.json()

        if not data:
            raise ValueError(f"No location found for {city}")

        return {
            "lat": float(data[0]["lat"]),
            "lng": float(data[0]["lon"])
        }

    except Exception as e:
        raise Exception(f"Geocoding failed: {str(e)}")



def safe_coords(city):
    try:
        return get_coordinates(city)
    except:
        return {"lat": 20.5937, "lng": 78.9629}


def get_current_location(origin, destination, progress):
    return {
        "lat": origin["lat"] + (destination["lat"] - origin["lat"]) * (progress / 100),
        "lng": origin["lng"] + (destination["lng"] - origin["lng"]) * (progress / 100)
    }


@app.route("/api/tracking/<tracking_number>")
def get_tracking_data(tracking_number):
    if 'user_id' not in session:
        return json.dumps({'success': False, 'error': 'Unauthorized'})

    db_conn = None
    cursor = None

    try:
        db_conn = get_db_connection()
        cursor = db_conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT origin, destination, status FROM shipments WHERE tracking_number=%s",
            (tracking_number,)
        )
        shipment = cursor.fetchone()

        if not shipment:
            return json.dumps({'success': False, 'error': 'Tracking not found'})

        origin = shipment['origin']
        destination = shipment['destination']
        status = shipment['status']

        origin_coords = safe_coords(origin)
        destination_coords = safe_coords(destination)

        progress = 65

        current_coords = get_current_location(
            origin_coords,
            destination_coords,
            progress
        )

        return json.dumps({
            'success': True,
            'tracking_number': tracking_number,
            'status': status,
            'origin': origin,
            'destination': destination,
            'origin_coords': origin_coords,
            'destination_coords': destination_coords,
            'current_coords': current_coords,
            'progress': progress,
            'eta': '2 days',
            'weather_alerts': []
        })

    except Exception as e:
        return json.dumps({
            'success': False,
            'error': str(e)
        })

    finally:
        if cursor:
            cursor.close()
        if db_conn:
            db_conn.close()

# Reports API - Fetch all shipments
@app.route("/api/reports/pdf")
def download_reports_pdf():
    if 'user_id' not in session:
        return json.dumps({"success": False, "error": "Unauthorized"})

    db_conn = None
    cursor = None

    try:
        db_conn = get_db_connection()
        cursor = db_conn.cursor(dictionary=True)

        # ✅ Role-based query
        if session.get('user_role') == 'admin':
            query = """
                SELECT tracking_number, origin, destination, payment_mode,
                       priority, status, created_at
                FROM shipments
                ORDER BY created_at DESC
            """
            cursor.execute(query)

        else:
            query = """
                SELECT tracking_number, origin, destination, payment_mode,
                       priority, status, created_at
                FROM shipments
                WHERE user_id=%s
                ORDER BY created_at DESC
            """
            cursor.execute(query, (session['user_id'],))

        shipments = cursor.fetchall()

        # ✅ Create PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer)
        styles = getSampleStyleSheet()

        elements = []
        elements.append(Paragraph("Shipping Reports", styles['Title']))
        elements.append(Spacer(1, 20))

        data = [[
            "Tracking Number",
            "Origin",
            "Destination",
            "Payment",
            "Priority",
            "Status",
            "Created At"
        ]]

        for s in shipments:
            data.append([
                s["tracking_number"],
                s["origin"],
                s["destination"],
                s["payment_mode"],
                s["priority"],
                s["status"],
                str(s["created_at"])
            ])

        table = Table(data)

        table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.grey),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("GRID", (0,0), (-1,-1), 1, colors.black),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold")
        ]))

        elements.append(table)
        doc.build(elements)

        buffer.seek(0)

        return send_file(
            buffer,
            as_attachment=True,
            download_name="shipping_report.pdf",
            mimetype="application/pdf"
        )

    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})

    finally:
        if cursor:
            cursor.close()
        if db_conn:
            db_conn.close()

@app.route("/welcome")
def welcome():
    return render_template("welcome.html")


if __name__ == "__main__":
    app.run(debug=True)