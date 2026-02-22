#!/usr/bin/env python3
"""
Simplified Flask app without problematic dependencies
"""
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import os
import sys
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretfra2025"

# Simple data storage
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
        },
        {
            "type": "Feature",
            "properties": {
                "village": "Mandla",
                "patta_holder": "Sita Devi",
                "latitude": 22.6000,
                "longitude": 80.3667,
                "area_hectares": 3.2,
                "claim_status": "Verified",
                "uploaded_by": "dcf.mandla@fra.gov.in",
                "file_id": "FRA12345678",
                "tribal_group": "Gond",
                "family_size": 5,
                "file_name": "mandla_patta_001.pdf",
                "upload_date": "2025-09-16T10:27:00"
            },
            "geometry": {
                "type": "Point",
                "coordinates": [80.3667, 22.6000]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "village": "Dindori",
                "patta_holder": "Ganga Ram",
                "latitude": 22.9500,
                "longitude": 81.0833,
                "area_hectares": 4.1,
                "claim_status": "Verified",
                "uploaded_by": "rfo.dindori@fra.gov.in",
                "file_id": "FRA87654321",
                "tribal_group": "Baiga",
                "family_size": 7,
                "file_name": "dindori_claim_002.pdf",
                "upload_date": "2025-09-16T10:32:00"
            },
            "geometry": {
                "type": "Point",
                "coordinates": [81.0833, 22.9500]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "village": "Barwani",
                "patta_holder": "Kavita Bai",
                "latitude": 22.0333,
                "longitude": 74.9000,
                "area_hectares": 2.8,
                "claim_status": "Verified",
                "uploaded_by": "ccf.admin@fra.gov.in",
                "file_id": "FRA11223344",
                "tribal_group": "Bhil",
                "family_size": 4,
                "file_name": "barwani_survey_003.pdf",
                "upload_date": "2025-09-16T10:35:00"
            },
            "geometry": {
                "type": "Point",
                "coordinates": [74.9000, 22.0333]
            }
        }
    ],
    "metadata": {
        "total_records": 4,
        "last_updated": "2025-09-16T10:35:00"
    }
}

# Simple users database
USERS = {
    "ccf.admin@fra.gov.in": {"password": "fra2025ccf", "role": "official"},
    "dcf.admin@fra.gov.in": {"password": "fra2025dcf", "role": "official"},
    "rfo.admin@fra.gov.in": {"password": "fra2025rfo", "role": "official"},
    "public@fra.gov.in": {"password": "public2025", "role": "public"}
}

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ""
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        
        if '@' not in email:
            error = "Invalid email format. Please include '@' in the email address."
            return render_template("login.html", error=error)
        
        user = USERS.get(email)
        if user and user["password"] == password:
            session["user"] = email
            session["role"] = user["role"]
            session["user_name"] = email.split("@")[0]
            local = email.split("@")[0]
            if local.startswith("ccf"):
                session["user_role"] = "CCF"
            elif local.startswith("dcf"):
                session["user_role"] = "DCF"
            elif local.startswith("rfo"):
                session["user_role"] = "RFO"
            else:
                session["user_role"] = "PUBLIC"
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid credentials. Please check email and password."
    return render_template("login.html", error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route("/dashboard")
def dashboard():
    user = session.get("user")
    role = session.get("role")
    if not user:
        return redirect(url_for("login"))
    return render_template("dashboard.html", user=user, role=role)

@app.route('/admin_panel')
def admin_panel():
    if not session.get('user'):
        return redirect(url_for('login'))
    if session.get('user_role') not in ['CCF', 'DCF', 'RFO']:
        flash('Access denied. Admin panel is only for CCF, DCF, and RFO officials.', 'error')
        return redirect(url_for('dashboard'))
    return render_template('admin_panel.html')

@app.route('/upload_patta', methods=['GET', 'POST'])
def upload_patta_admin():
    if not session.get("user"):
        return redirect(url_for("login"))
    if session.get('user_role') not in ['CCF', 'DCF', 'RFO']:
        return "Unauthorized", 403
    
    if request.method == 'POST':
        village = request.form.get('village', '').strip()
        patta_holder = request.form.get('patta_holder', '').strip()
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        area_hectares = request.form.get('area_hectares')
        tribal_group = request.form.get('tribal_group', '').strip()
        family_size = request.form.get('family_size', '').strip()
        file = request.files.get('patta_file')

        if not file or not file.filename.lower().endswith('.pdf'):
            flash(('error', 'Please upload a PDF file.'))
            return render_template('admin_panel.html')

        # Create uploads directory
        os.makedirs(os.path.join(os.path.dirname(__file__), 'uploads'), exist_ok=True)
        save_path = os.path.join(os.path.dirname(__file__), 'uploads', file.filename)
        file.save(save_path)

        # Process form data
        new_village = village
        new_holder = patta_holder
        try:
            new_lat = float(latitude)
            new_lon = float(longitude)
        except Exception:
            new_lat, new_lon = 0.0, 0.0
        try:
            new_area = float(area_hectares)
        except Exception:
            new_area = 0.0
        try:
            new_family_size = int(family_size) if family_size else 0
        except Exception:
            new_family_size = 0

        # Generate unique file ID
        file_id = f"FRA{str(uuid.uuid4())[:8].upper()}"

        # Add to map data
        new_feature = {
            "type": "Feature",
            "properties": {
                "village": new_village or "Unknown",
                "patta_holder": new_holder or "Unknown",
                "latitude": new_lat,
                "longitude": new_lon,
                "area_hectares": new_area,
                "claim_status": "Verified",
                "uploaded_by": session.get("user"),
                "file_id": file_id,
                "tribal_group": tribal_group or "Unknown",
                "family_size": new_family_size,
                "file_name": file.filename,
                "upload_date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            },
            "geometry": {
                "type": "Point",
                "coordinates": [new_lon, new_lat]
            }
        }
        
        TEST_VILLAGES["features"].append(new_feature)
        TEST_VILLAGES["metadata"]["total_records"] = len(TEST_VILLAGES["features"])
        TEST_VILLAGES["metadata"]["last_updated"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        flash(('success', f'✅ File {file.filename} uploaded successfully! Added {new_village} to map with coordinates ({new_lat}, {new_lon}).'))
        return redirect(url_for('admin_panel'))
    
    return render_template('admin_panel.html')

@app.route("/api/fra_data")
def api_fra_data():
    return jsonify(TEST_VILLAGES)

@app.route("/api/system_status")
def api_system_status():
    return jsonify({
        "status": "online",
        "villages_loaded": len(TEST_VILLAGES.get("features", [])),
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    })

if __name__ == "__main__":
    print("🚀 Starting Simplified FRA Sentinel Server...")
    print("✅ No problematic dependencies")
    print("✅ Upload functionality working")
    print("✅ Map integration ready")
    print("🌐 Server running on: http://localhost:5000")
    app.run(debug=True, port=5000)
