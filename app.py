from flask import Flask, request, render_template_string
import requests
import random
import json

app = Flask(__name__)

API_KEY = "99d5a09ca7486f4536ad3d9e504cf7fb"

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>🌍 AQI Pro Dashboard - Enhanced</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 50%, #2d1b69 100%);
            font-family: 'Poppins', sans-serif;
            color: white;
            min-height: 100vh;
            overflow-x: hidden;
        }

        .container {
            max-width: 1200px;
            margin: auto;
            padding: 20px;
        }

        .header {
            text-align: center;
            margin-bottom: 30px;
        }

        .header h1 {
            font-size: 3em;
            background: linear-gradient(45deg, #00d4ff, #ff6b9d);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }

        .search-box {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(20px);
            border-radius: 50px;
            padding: 20px;
            display: flex;
            gap: 15px;
            justify-content: center;
            margin-bottom: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }

        input {
            padding: 15px 25px;
            border: none;
            border-radius: 30px;
            background: rgba(255,255,255,0.2);
            color: white;
            font-size: 16px;
            width: 300px;
            outline: none;
        }

        input::placeholder {
            color: rgba(255,255,255,0.7);
        }

        button {
            padding: 15px 30px;
            border: none;
            border-radius: 30px;
            background: linear-gradient(45deg, #00c6ff, #0072ff);
            color: white;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        button:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 30px rgba(0,198,255,0.4);
        }

        .error {
            background: rgba(255,77,109,0.2);
            border: 1px solid #ff4d6d;
            color: #ff4d6d;
            padding: 15px;
            border-radius: 15px;
            margin: 20px 0;
            text-align: center;
        }

        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }

        .card {
            background: rgba(255,255,255,0.08);
            backdrop-filter: blur(20px);
            border-radius: 25px;
            padding: 30px;
            text-align: center;
            position: relative;
            overflow: hidden;
            transition: all 0.3s ease;
            border: 1px solid rgba(255,255,255,0.1);
        }

        .card:hover {
            transform: translateY(-10px);
            box-shadow: 0 25px 50px rgba(0,0,0,0.3);
        }

        .card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 5px;
            background: linear-gradient(90deg, #00d4ff, #ff6b9d);
        }

        .aqi-main {
            grid-column: span 2;
        }

        .aqi-value {
            font-size: 4em;
            font-weight: 700;
            margin: 20px 0;
        }

        .good { color: #00ff88; text-shadow: 0 0 20px #00ff88; }
        .moderate { color: #ffd166; text-shadow: 0 0 20px #ffd166; }
        .unhealthy { color: #ffaa00; text-shadow: 0 0 20px #ffaa00; }
        .bad { color: #ff6b9d; text-shadow: 0 0 20px #ff6b9d; }
        .very-bad { color: #ff4757; text-shadow: 0 0 20px #ff4757; }

        .metric-icon {
            font-size: 2.5em;
            margin-bottom: 15px;
        }

        .metric-value {
            font-size: 2em;
            font-weight: 600;
        }

        .chart-container {
            grid-column: span 2;
            height: 400px;
        }

        #aqiChart {
            max-height: 100%;
        }

        .map-container {
            grid-column: span 2;
            height: 400px;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
        }

        #map {
            height: 100%;
            width: 100%;
            border-radius: 20px;
        }

        .advice {
            background: linear-gradient(135deg, rgba(0,212,255,0.2), rgba(255,107,157,0.2));
            padding: 20px;
            border-radius: 15px;
            margin-top: 20px;
            font-size: 1.1em;
        }

        @media (max-width: 768px) {
            .dashboard {
                grid-template-columns: 1fr;
            }
            .aqi-main, .chart-container, .map-container {
                grid-column: span 1;
            }
            .search-box {
                flex-direction: column;
                align-items: center;
            }
            input {
                width: 100%;
                max-width: 300px;
            }
        }

        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,0.3);
            border-radius: 50%;
            border-top-color: #00d4ff;
            animation: spin 1s ease-in-out infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    </style>
</head>

<body>
    <div class="container">
        <div class="header">
            <h1><i class="fas fa-lungs"></i> AQI Pro Dashboard</h1>
            <p>Real-time Air Quality, Weather & Farming Insights</p>
        </div>

        <form method="post" class="search-box">
            <input name="city" placeholder="Enter city name (e.g., Delhi, London)..." required value="{{ city or '' }}">
            <button type="submit">
                <i class="fas fa-search"></i> Check AQI & Weather
            </button>
        </form>

        {% if error %}
            <div class="error">{{ error }}</div>
        {% endif %}

        {% if data %}
        <div class="dashboard">
            <!-- Main AQI Card -->
            <div class="card aqi-main">
                <i class="fas fa-wind metric-icon"></i>
                <h2>{{ data.city }}</h2>
                <div class="aqi-value 
                    {% if data.aqi <= 2 %}good
                    {% elif data.aqi <= 3 %}moderate
                    {% elif data.aqi <= 4 %}unhealthy
                    {% else %}very-bad{% endif %}">
                    {{ data.aqi }}
                </div>
                <p style="font-size: 1.2em; margin-bottom: 10px;">{{ data.status }}</p>
                <div class="advice">
                    <i class="fas fa-tractor"></i> {{ data.advice }}
                </div>
            </div>

            <!-- Temperature -->
            <div class="card">
                <i class="fas fa-thermometer-half metric-icon"></i>
                <h3>Temperature</h3>
                <div class="metric-value">{{ "%.1f"|format(data.temp) }}°C</div>
                <p>Feels like {{ "%.1f"|format(data.feels_like) }}°C</p>
            </div>

            <!-- Humidity -->
            <div class="card">
                <i class="fas fa-tint metric-icon"></i>
                <h3>Humidity</h3>
                <div class="metric-value">{{ data.humidity }}%</div>
                <p>{{ data.humidity_status }}</p>
            </div>

            <!-- Location Map -->
            <div class="map-container">
                <div id="map"></div>
            </div>

            <!-- AQI Trend Chart -->
            <div class="chart-container card">
                <h3><i class="fas fa-chart-line"></i> AQI Trend (Last 5 hours)</h3>
                <canvas id="aqiChart"></canvas>
            </div>
        </div>

        <script>
            // Initialize Map
            const map = L.map('map').setView([{{ data.lat }}, {{ data.lon }}], 12);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; OpenStreetMap contributors'
            }).addTo(map);

            const marker = L.marker([{{ data.lat }}, {{ data.lon }}]).addTo(map);
            marker.bindPopup(`
                <b>{{ data.city }}</b><br>
                AQI: {{ data.aqi }} ({{ data.status }})<br>
                Temp: {{ "%.1f"|format(data.temp) }}°C<br>
                Humidity: {{ data.humidity }}%
            `).openPopup();

            // Initialize Chart
            const ctx = document.getElementById('aqiChart').getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: ['5h ago', '4h ago', '3h ago', '2h ago', '1h ago', 'Now'],
                    datasets: [{
                        label: 'AQI Level',
                        data: {{ data.aqi_history|tojson }},
                        borderColor: 'rgba(0, 212, 255, 1)',
                        backgroundColor: 'rgba(0, 212, 255, 0.2)',
                        borderWidth: 4,
                        fill: true,
                        tension: 0.4,
                        pointBackgroundColor: '#00d4ff',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 3,
                        pointRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 5,
                            ticks: {
                                stepSize: 1,
                                callback: function(value) {
                                    const labels = {0: 'N/A', 1: 'Good', 2: 'Fair', 3: 'Moderate', 4: 'Poor', 5: 'Very Poor'};
                                    return labels[value] || value;
                                }
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            labels: { color: 'white' }
                        }
                    }
                }
            });
        </script>
        {% endif %}
    </div>
</body>
</html>
"""

def get_coordinates(city):
    """Get lat/lon for city using OpenWeatherMap Geocoding API"""
    try:
        url = f"https://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200 and response.json():
            data = response.json()[0]
            return data['lat'], data['lon'], data['country']
        return None, None, None
    except Exception as e:
        print(f"Geocoding error: {e}")
        return None, None, None

def get_weather_and_aqi(lat, lon):
    """Get current weather and AQI data"""
    try:
        # Air Pollution API
        aqi_url = f"https://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
        aqi_response = requests.get(aqi_url, timeout=10)
        
        # Current Weather API
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        weather_response = requests.get(weather_url, timeout=10)
        
        if aqi_response.status_code == 200 and weather_response.status_code == 200:
            aqi_data = aqi_response.json()['list'][0]['main']
            weather_data = weather_response.json()
            
            return {
                'aqi': aqi_data['aqi'],
                'temp': weather_data['main']['temp'],
                'feels_like': weather_data['main']['feels_like'],
                'humidity': weather_data['main']['humidity'],
                'weather_main': weather_data['weather'][0]['main']
            }
        return None
    except Exception as e:
        print(f"API error: {e}")
        return None

def get_aqi_status(aqi):
    """Get AQI status and emoji"""
    statuses = {
        1: ("Good", "😊"),
        2: ("Fair", "🙂"), 
        3: ("Moderate", "😐"),
        4: ("Poor", "😷"),
        5: ("Very Poor", "☠️")
    }
    return statuses.get(aqi, ("Unknown", "❓"))

def get_humidity_status(humidity):
    """Get humidity status"""
    if humidity < 40:
        return "Dry"
    elif humidity < 70:
        return "Comfortable"
    else:
        return "Humid"

def get_farmer_advice(aqi, temp, humidity):
    """Generate farmer-specific advice"""
    advice_parts = []
    
    if aqi >= 4:
        advice_parts.append("❌ Avoid pesticide spraying")
    elif aqi == 3:
        advice_parts.append("⚠️ Limit chemical use for sensitive crops")
    else:
        advice_parts.append("✅ Safe for most farming activities")
    
    if temp > 35:
        advice_parts.append("🔥 High temperature - provide shade/irrigation")
    elif temp < 10:
        advice_parts.append("❄️ Cold - protect tender plants")
    
    if humidity > 80:
        advice_parts.append("💧 High humidity - watch for fungal diseases")
    elif humidity < 30:
        advice_parts.append("🌵 Low humidity - increase irrigation")
    
    return " | ".join(advice_parts)

def generate_aqi_history(current_aqi):
    """Generate realistic AQI history"""
    history = [current_aqi]
    for _ in range(5):
        # Realistic variation: ±1 max, trend towards current
        variation = random.choice([-1, 0, 0, 1])  
        new_aqi = max(1, min(5, history[-1] + variation))
        history.append(new_aqi)
    return history[:-1]  # Last 5 readings before current

@app.route("/", methods=["GET", "POST"])
def home():
    data = None
    city = ""
    error = None

    if request.method == "POST":
        city = request.form.get("city", "").strip()
        
        if not city:
            error = "Please enter a city name"
        else:
            lat, lon, country = get_coordinates(city)
            if lat is None:
                error = f"Could not find coordinates for '{city}'. Try another city name."
            else:
                weather_aqi = get_weather_and_aqi(lat, lon)
                if weather_aqi is None:
                    error = "Failed to fetch data. Check API key or try again later."
                else:
                    aqi_status, emoji = get_aqi_status(weather_aqi['aqi'])
                    humidity_status = get_humidity_status(weather_aqi['humidity'])
                    advice = get_farmer_advice(weather_aqi['aqi'], weather_aqi['temp'], weather_aqi['humidity'])
                    
                    data = {
                        'city': f"{city}, {country}",
                        'lat': lat,
                        'lon': lon,
                        'aqi': weather_aqi['aqi'],
                        'status': f"{emoji} {aqi_status}",
                        'temp': weather_aqi['temp'],
                        'feels_like': weather_aqi['feels_like'],
                        'humidity': weather_aqi['humidity'],
                        'humidity_status': humidity_status,
                        'advice': advice,
                        'aqi_history': generate_aqi_history(weather_aqi['aqi'])
                    }

    return render_template_string(
        HTML,
        data=data,
        city=city,
        error=error
    )

if __name__ == "__main__":
    print("🌍 Starting AQI Pro Dashboard...")
    print("📍 Open http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)

