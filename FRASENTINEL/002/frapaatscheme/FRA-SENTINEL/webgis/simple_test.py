from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "<h1>Flask is Working!</h1><p><a href='/api/test'>Test API</a></p>"

@app.route("/api/test")
def api_test():
    return jsonify({
        "status": "working",
        "message": "API is responding",
        "data": {"test": "success"}
    })

@app.route("/api/classification_stats")
def classification_stats():
    return jsonify({
        "farmland": {"percentage": 35.5, "pixels": 3550},
        "forest": {"percentage": 42.3, "pixels": 4230},
        "water": {"percentage": 7.8, "pixels": 780},
        "homestead": {"percentage": 14.4, "pixels": 1440}
    })

if __name__ == "__main__":
    print("🧪 Starting Simple Test Server...")
    print("🌐 Go to: http://localhost:5000")
    print("📊 API: http://localhost:5000/api/classification_stats")
    app.run(debug=True, host='0.0.0.0', port=5000)
