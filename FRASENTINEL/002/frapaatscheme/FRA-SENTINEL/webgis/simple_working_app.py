from flask import Flask, render_template, jsonify
import json

app = Flask(__name__)

# Hard-coded test data that ALWAYS works
TEST_VILLAGES = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {
                "village": "Khargone",
                "patta_holder": "Ram Singh",
                "latitude": 21.8225,
                "longitude": 75.6102,
                "area_hectares": 2.5,
                "claim_status": "Approved"
            },
            "geometry": {
                "type": "Point",
                "coordinates": [75.6102, 21.8225]
            }
        }
    ],
    "metadata": {
        "total_records": 1,
        "last_updated": "2025-09-01T12:31:00"
    }
}

TEST_STATS = {
    "farmland": {"percentage": 35.5, "pixels": 3550},
    "forest": {"percentage": 42.3, "pixels": 4230},
    "water": {"percentage": 7.8, "pixels": 780},
    "homestead": {"percentage": 14.4, "pixels": 1440}
}

@app.route("/")
def home():
    # Use an existing template in templates directory
    return render_template("simple_test.html")

@app.route("/api/fra_data")
def get_fra_data():
    print("✅ FRA data requested")
    return jsonify(TEST_VILLAGES)

@app.route("/api/classification_stats")
def get_stats():
    print("✅ Stats requested")
    return jsonify(TEST_STATS)

@app.route("/api/dss_recommendation/<village>")
def get_recommendations(village):
    print(f"✅ Recommendations requested for: {village}")
    return jsonify({
        "village_info": TEST_VILLAGES["features"][0]["properties"],
        "recommendations": [
            {
                "scheme": "PM-KISAN",
                "priority": "High",
                "reasons": ["Test reason"],
                "benefit": "Rs. 6,000 annual support",
                "ministry": "Ministry of Agriculture",
                "eligibility_score": 85.0
            }
        ]
    })

@app.route("/api/system_status")
def system_status():
    print("✅ System status requested")
    return jsonify({
        "status": "online",
        "villages_loaded": 1,
        "stats_loaded": 4,
        "timestamp": "2025-09-01T12:31:00"
    })

@app.route("/test")
def test_page():
    return """
    <h1>🧪 Simple Test - Working!</h1>
    <p>If you see this, Flask is working!</p>
    <ul>
        <li><a href="/api/fra_data" target="_blank">Test FRA Data</a></li>
        <li><a href="/api/classification_stats" target="_blank">Test Stats</a></li>
        <li><a href="/api/system_status" target="_blank">Test Status</a></li>
        <li><a href="/" target="_blank">Main App</a></li>
    </ul>
    """

if __name__ == "__main__":
    print("🚀 SIMPLE TEST APP STARTING")
    print("=" * 50)
    print("🌐 Main: http://localhost:5000")
    print("🧪 Test: http://localhost:5000/test")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
