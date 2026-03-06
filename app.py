from flask import Flask, render_template, request, jsonify
from model import predictor
from route_optimizer import get_optimized_route

app = Flask(__name__)

# In-memory storage for waste reports
reports = []

@app.route('/')
def home():
    return render_template('citizen.html')

@app.route('/citizen')
def citizen():
    return render_template('citizen.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/report_waste', methods=['POST'])
def report_waste():
    data = request.json
    lat = data.get('latitude')
    lng = data.get('longitude')
    image_data = data.get('image') # Optional base64 image data
    
    if lat is None or lng is None:
        return jsonify({"error": "Latitude and longitude are required"}), 400
        
    reports.append({
        "lat": lat, 
        "lng": lng,
        "image": image_data
    })
    return jsonify({"message": "Waste reported successfully", "status": "success"})

@app.route('/get_reports', methods=['GET'])
def get_reports():
    return jsonify({"reports": reports})

@app.route('/predict_hotspots', methods=['GET'])
def predict_hotspots():
    predictions = []
    for report in reports:
        level = predictor.predict_for_location(report['lat'], report['lng'])
        predictions.append({
            "lat": report['lat'],
            "lng": report['lng'],
            "level": level
        })
    return jsonify({"predictions": predictions})

@app.route('/optimize_route', methods=['GET'])
def optimize_route():
    locations = [[r['lat'], r['lng']] for r in reports]
    optimized = get_optimized_route(locations)
    return jsonify({"route": optimized})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
