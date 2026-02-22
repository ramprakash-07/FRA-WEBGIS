from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import os
import sys

app = Flask(__name__)
app.secret_key = "supersecretfra2025"

# Re-enable OCR/NER integration so uploads can add villages to map
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)
try:
    from digitization.ocr_ner import pdf_to_text, extract_entities
except Exception:
    pdf_to_text = None
    extract_entities = None

# Lightweight test data for dashboard APIs
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

# Dummy users DB for demo
USERS = {
    "ccf.admin@fra.gov.in": {"password": "fra2025ccf", "role": "official"},
    "dcf.admin@fra.gov.in": {"password": "fra2025dcf", "role": "official"},
    "rfo.admin@fra.gov.in": {"password": "fra2025rfo", "role": "official"},
    "sarpanch.admin@fra.gov.in": {"password": "fra2025gram", "role": "official"},
    "public@fra.gov.in": {"password": "public2025", "role": "public"}
}

# Example patta claims database
PATTA_CLAIMS = [
    {
        "id": "MP001234",
        "applicant_name": "Ramesh Kumar Bhil",
        "village": "Khargone",
        "district": "Khargone",
        "state": "Madhya Pradesh",
        "claim_type": "IFR",
        "area_hectares": 2.5,
        "status": "Approved",
        "coordinates": [21.8245, 75.6102],
        "verified_by": "ccf.admin@fra.gov.in",
        "document": None
    },
    {
        "id": "OD005678",
        "applicant_name": "Sita Devi Santhal",
        "village": "Mayurbhanj",
        "district": "Mayurbhanj",
        "state": "Odisha",
        "claim_type": "CFR",
        "area_hectares": 15.0,
        "status": "Pending",
        "coordinates": [21.9270, 86.7470],
        "verified_by": None,
        "document": None
    }
]

@app.route('/', methods=['GET'])
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ""
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        
        # Simple email format validation
        if '@' not in email:
            error = "Invalid email format. Please include '@' in the email address."
            return render_template("login.html", error=error)
        
        user = USERS.get(email)
        if user and user["password"] == password:
            session["user"] = email
            session["role"] = user["role"]
            # Derive display name and fine-grained role for UI
            session["user_name"] = email.split("@")[0]
            local = email.split("@")[0]
            if local.startswith("ccf"):
                session["user_role"] = "CCF"
            elif local.startswith("dcf"):
                session["user_role"] = "DCF"
            elif local.startswith("rfo"):
                session["user_role"] = "RFO"
            elif local.startswith("sarpanch"):
                session["user_role"] = "GRAM_SABHA"
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

# ----- Admin-only routes -----
def _is_admin_user():
    return session.get("user_role") in {"CCF", "DCF", "RFO"}

@app.route('/admin')
def admin_panel():
    if not session.get("user"):
        return redirect(url_for("login"))
    if not _is_admin_user():
        return "Unauthorized", 403
    # Minimal example list (wire to DB if needed)
    files = []
    return render_template("manage_files.html", files=files)

@app.route('/upload_patta', methods=['GET', 'POST'])
def upload_patta_admin():
    if not session.get("user"):
        return redirect(url_for("login"))
    if not _is_admin_user():
        return "Unauthorized", 403
    if request.method == 'POST':
        village = request.form.get('village', '').strip()
        patta_holder = request.form.get('patta_holder', '').strip()
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        area_hectares = request.form.get('area_hectares')
        file = request.files.get('patta_file')

        if not file or not file.filename.lower().endswith('.pdf'):
            flash(('error', 'Please upload a PDF file.'))
            return render_template('upload_patta.html')

        os.makedirs(os.path.join(os.path.dirname(__file__), 'uploads'), exist_ok=True)
        save_path = os.path.join(os.path.dirname(__file__), 'uploads', file.filename)
        file.save(save_path)

        # Default values from form
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

        # Try OCR extraction if tools are available
        if pdf_to_text and extract_entities:
            try:
                text = pdf_to_text(save_path)
                ovillage, oholder, olat, olon = extract_entities(text)
                if ovillage:
                    new_village = ovillage
                if oholder:
                    new_holder = oholder
                if olat and olon:
                    new_lat, new_lon = float(olat), float(olon)
            except Exception:
                pass

        # Append to map data so it shows immediately
        TEST_VILLAGES["features"].append({
            "type": "Feature",
            "properties": {
                "village": new_village or "Unknown",
                "patta_holder": new_holder or "Unknown",
                "latitude": new_lat,
                "longitude": new_lon,
                "area_hectares": new_area,
                "claim_status": "Verified",
                "uploaded_by": session.get("user")
            },
            "geometry": {
                "type": "Point",
                "coordinates": [new_lon, new_lat]
            }
        })

        flash(('success', f'File {file.filename} uploaded. Added {new_village} to map.'))
        return render_template('upload_patta.html')
    return render_template('upload_patta.html')

@app.route('/fra_data_collection', methods=['GET', 'POST'])
def fra_data_collection():
    if not session.get("user"):
        return redirect(url_for("login"))
    if not _is_admin_user():
        return "Unauthorized", 403
    
    if request.method == 'POST':
        # Collect all form data
        fra_data = {
            # Personal Information
            'head_name': request.form.get('head_name', '').strip(),
            'aadhaar_number': request.form.get('aadhaar_number', '').strip(),
            'mobile_number': request.form.get('mobile_number', '').strip(),
            'social_category': request.form.get('social_category', '').strip(),
            'complete_address': request.form.get('complete_address', '').strip(),
            
            # Family Information
            'total_family_members': request.form.get('total_family_members', '').strip(),
            'adults_count': request.form.get('adults_count', '').strip(),
            'elderly_count': request.form.get('elderly_count', '').strip(),
            'bpl_status': request.form.get('bpl_status', '').strip(),
            'has_widowed_disabled': 'Yes' if request.form.get('has_widowed_disabled') else 'No',
            
            # Housing Information
            'owns_house': request.form.get('owns_house', '').strip(),
            'house_type': request.form.get('house_type', '').strip(),
            'land_area_hectares': request.form.get('land_area_hectares', '').strip(),
            'survey_numbers': request.form.get('survey_numbers', '').strip(),
            
            # Agriculture Information
            'cultivates_crops': request.form.get('cultivates_crops', '').strip(),
            'crops_list': request.form.get('crops_list', '').strip(),
            
            # Basic Amenities
            'tap_water': request.form.get('tap_water', '').strip(),
            'toilet_facility': request.form.get('toilet_facility', '').strip(),
            'electricity': request.form.get('electricity', '').strip(),
            'clean_fuel': request.form.get('clean_fuel', '').strip(),
            
            # Documentation
            'ration_card': request.form.get('ration_card', '').strip(),
            'bank_account': request.form.get('bank_account', '').strip(),
            'secc_code': request.form.get('secc_code', '').strip(),
            
            # Forest & Tribal Information
            'tribal_district': request.form.get('tribal_district', '').strip(),
            'collects_forest_produce': request.form.get('collects_forest_produce', '').strip(),
            'forest_products': request.form.get('forest_products', '').strip(),
            
            # Employment & Schemes
            'willing_mgnrega': request.form.get('willing_mgnrega', '').strip(),
            'enrolled_schemes': request.form.get('enrolled_schemes', '').strip(),
            
            # Metadata
            'submitted_by': session.get("user"),
            'submission_date': '2025-01-27'  # You can use datetime.now() for real timestamp
        }
        
        # Here you would typically save to database
        # For now, we'll just show a success message
        flash(('success', f'FRA household data for {fra_data["head_name"]} submitted successfully! Data collected for eligibility assessment.'))
        
        # You can add database saving logic here
        # Example: save_fra_data_to_database(fra_data)
        
        return render_template('fra_data_collection.html')
    
    return render_template('fra_data_collection.html')

@app.route('/unified_assessment', methods=['GET', 'POST'])
def unified_assessment():
    """Unified assessment combining FRA data and patta details"""
    if not session.get("user"):
        return redirect(url_for("login"))
    if not _is_admin_user():
        return "Unauthorized", 403
    
    if request.method == 'POST':
        try:
            # Import eligibility engine
            from eligibility_engine import EligibilityEngine
            
            # Get FRA data from form
            fra_data = {
                'head_name': request.form.get('head_name', '').strip(),
                'aadhaar_number': request.form.get('aadhaar_number', '').strip(),
                'mobile_number': request.form.get('mobile_number', '').strip(),
                'social_category': request.form.get('social_category', '').strip(),
                'complete_address': request.form.get('complete_address', '').strip(),
                'total_family_members': request.form.get('total_family_members', '').strip(),
                'adults_count': request.form.get('adults_count', '').strip(),
                'elderly_count': request.form.get('elderly_count', '').strip(),
                'bpl_status': request.form.get('bpl_status', '').strip(),
                'has_widowed_disabled': 'Yes' if request.form.get('has_widowed_disabled') else 'No',
                'owns_house': request.form.get('owns_house', '').strip(),
                'house_type': request.form.get('house_type', '').strip(),
                'land_area_hectares': request.form.get('land_area_hectares', '').strip(),
                'survey_numbers': request.form.get('survey_numbers', '').strip(),
                'cultivates_crops': request.form.get('cultivates_crops', '').strip(),
                'crops_list': request.form.get('crops_list', '').strip(),
                'tap_water': request.form.get('tap_water', '').strip(),
                'toilet_facility': request.form.get('toilet_facility', '').strip(),
                'electricity': request.form.get('electricity', '').strip(),
                'clean_fuel': request.form.get('clean_fuel', '').strip(),
                'ration_card': request.form.get('ration_card', '').strip(),
                'bank_account': request.form.get('bank_account', '').strip(),
                'secc_code': request.form.get('secc_code', '').strip(),
                'tribal_district': request.form.get('tribal_district', '').strip(),
                'collects_forest_produce': request.form.get('collects_forest_produce', '').strip(),
                'forest_products': request.form.get('forest_products', '').strip(),
                'willing_mgnrega': request.form.get('willing_mgnrega', '').strip(),
                'enrolled_schemes': request.form.get('enrolled_schemes', '').strip(),
                'submitted_by': session.get("user"),
                'submission_date': '2025-01-27'
            }
            
            # Get patta file if uploaded
            patta_file = request.files.get('patta_file')
            patta_data = None
            
            if patta_file and patta_file.filename:
                # Save patta file
                os.makedirs(os.path.join(os.path.dirname(__file__), 'uploads'), exist_ok=True)
                patta_path = os.path.join(os.path.dirname(__file__), 'uploads', patta_file.filename)
                patta_file.save(patta_path)
                
                # Try to extract patta data using OCR if available
                if pdf_to_text and extract_entities:
                    try:
                        text = pdf_to_text(patta_path)
                        village, holder, lat, lon = extract_entities(text)
                        patta_data = {
                            'village': village or '',
                            'owner_name': holder or '',
                            'latitude': lat or '',
                            'longitude': lon or '',
                            'document_path': patta_path
                        }
                    except Exception as e:
                        print(f"OCR extraction failed: {e}")
                        patta_data = {'document_path': patta_path}
                else:
                    patta_data = {'document_path': patta_path}
            
            # Run eligibility assessment
            engine = EligibilityEngine()
            assessment_result = engine.assess_eligibility(fra_data, patta_data)
            
            # Save assessment result
            output_file = engine.save_assessment(assessment_result)
            
            # Store in session for display
            session['last_assessment'] = assessment_result
            session['assessment_file'] = output_file
            
            flash(('success', f'Unified assessment completed! {len(assessment_result["eligible_schemes"])} schemes identified for {fra_data["head_name"]}'))
            
            return redirect(url_for('assessment_results'))
            
        except Exception as e:
            flash(('error', f'Assessment failed: {str(e)}'))
            return render_template('unified_assessment.html')
    
    return render_template('unified_assessment.html')

@app.route('/assessment_results')
def assessment_results():
    """Display assessment results"""
    if not session.get("user"):
        return redirect(url_for("login"))
    if not _is_admin_user():
        return "Unauthorized", 403
    
    assessment_result = session.get('last_assessment')
    assessment_file = session.get('assessment_file')
    
    if not assessment_result:
        flash(('error', 'No assessment results found. Please run an assessment first.'))
        return redirect(url_for('unified_assessment'))
    
    return render_template('assessment_results.html', 
                         assessment=assessment_result, 
                         assessment_file=assessment_file)

@app.route('/download_assessment')
def download_assessment():
    """Download assessment report as JSON"""
    if not session.get("user"):
        return redirect(url_for("login"))
    if not _is_admin_user():
        return "Unauthorized", 403
    
    assessment_file = session.get('assessment_file')
    if not assessment_file or not os.path.exists(assessment_file):
        flash(('error', 'Assessment file not found.'))
        return redirect(url_for('unified_assessment'))
    
    from flask import send_file
    return send_file(assessment_file, as_attachment=True, 
                    download_name=f"fra_assessment_{session.get('last_assessment', {}).get('head_name', 'unknown')}.json")

@app.route("/dashboard")
def dashboard():
    user = session.get("user")
    role = session.get("role")
    if not user:
        return redirect(url_for("login"))
    return render_template("dashboard.html", user=user, role=role, claims=PATTA_CLAIMS, enumerate=enumerate)

@app.route('/upload', methods=['POST'])
def upload_patta():
    user = session.get("user")
    role = session.get("role")
    if role != "official":
        return "Unauthorized", 403
    claim_id = request.form.get("claim_id")
    file = request.files.get("document")
    if not claim_id or not file:
        flash("Claim ID and document are required.")
        return redirect(url_for("dashboard"))
    for claim in PATTA_CLAIMS:
        if claim["id"] == claim_id:
            # Simulate saving the file (in production, save to disk or database)
            claim["document"] = file.filename
            claim["status"] = "Verified"
            claim["verified_by"] = user
            flash(f"Patta document for {claim_id} uploaded & verified!")
            return redirect(url_for("dashboard"))
    flash(f"Claim ID {claim_id} not found.")
    return redirect(url_for("dashboard"))

@app.route('/api/claims', methods=['GET'])
def api_claims():
    role = session.get("role")
    if role == "public":
        # Only minimal view for public
        return jsonify([
            {
                "id": c["id"],
                "applicant_name": c["applicant_name"],
                "village": c["village"],
                "district": c["district"],
                "state": c["state"],
                "coordinates": c["coordinates"]
            } for c in PATTA_CLAIMS
        ])
    else:
        # Officials get full data
        return jsonify(PATTA_CLAIMS)

# ====== Dashboard API endpoints (to avoid 404s) ======
@app.route("/api/fra_data")
def api_fra_data():
    return jsonify(TEST_VILLAGES)

@app.route("/api/classification_stats")
def api_classification_stats():
    return jsonify(TEST_STATS)

@app.route("/api/dss_recommendation/<village>")
def api_dss_recommendation(village):
    # Minimal mocked recommendation
    return jsonify({
        "village_info": TEST_VILLAGES["features"][0]["properties"],
        "recommendations": [
            {
                "scheme": "PM-KISAN",
                "priority": "High",
                "reasons": ["Sufficient agricultural area", "Approved claim"],
                "benefit": "Rs. 6,000 annual support",
                "ministry": "Ministry of Agriculture",
                "eligibility_score": 85.0
            }
        ]
    })

@app.route("/api/system_status")
def api_system_status():
    return jsonify({
        "status": "online",
        "villages_loaded": len(TEST_VILLAGES.get("features", [])),
        "stats_loaded": len(TEST_STATS.keys()),
        "timestamp": "2025-09-01T12:31:00"
    })

if __name__ == "__main__":
    app.run(debug=True)
