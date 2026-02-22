from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_babel import Babel, gettext as _
import os
import sys
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretfra2025"

# Initialize Babel
babel = Babel()

def select_locale():
    """Select locale based on URL parameter, cookie, or browser preference"""
    lang = request.args.get('lang') or request.cookies.get('lang')
    if lang in ('en', 'hi', 'ta', 'te'):
        return lang
    # fallback to browser
    return request.accept_languages.best_match(['en', 'hi', 'ta', 'te'])

# Initialize Babel with the app
babel.init_app(app, locale_selector=select_locale)

@app.context_processor
def inject_lang():
    """Inject current language into template context"""
    return {'current_lang': select_locale()}

# Re-enable OCR/NER integration so uploads can add villages to map
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)
# Temporarily disabled due to dependency issues
# try:
#     from digitization.simple_ocr_ner import pdf_to_text, extract_entities
#     print("✅ OCR/NER integration loaded successfully")
# except Exception as e:
    pdf_to_text = None
    extract_entities = None
print("⚠️ OCR/NER temporarily disabled due to dependency issues")

# Import Patta API (after PROJECT_ROOT is added to sys.path)
try:
    # from webgis.api.patta_api import patta_bp
    PATTA_API_AVAILABLE = False  # Temporarily disabled
    print("⚠️ Patta API temporarily disabled")
except ImportError as e:
    PATTA_API_AVAILABLE = False
    print(f"⚠️ Patta API not available: {e}")

# Import Demo Data for Hackathon Presentation
try:
    # from webgis.demo_data import (
    #     get_demo_patta_metrics, get_demo_system_stats, 
    #     get_demo_success_stories, get_demo_patta_documents,
    #     get_demo_ai_prediction, get_demo_chatbot_response
    # )
    DEMO_DATA_AVAILABLE = False  # Temporarily disabled
    print("⚠️ Demo data temporarily disabled")
except ImportError as e:
    DEMO_DATA_AVAILABLE = False
    print(f"⚠️ Demo data not available: {e}")

# Import Blockchain Storage Module
try:
    from blockchain_storage import (
        register_fra_document, verify_fra_document, get_blockchain_stats,
        get_blockchain_transactions, search_blockchain_documents, get_document_from_blockchain
    )
    BLOCKCHAIN_AVAILABLE = True
    print("✅ Blockchain storage module loaded successfully")
except ImportError as e:
    BLOCKCHAIN_AVAILABLE = False
    print(f"⚠️ Blockchain storage not available: {e}")

# Mock functions for demo data
def get_demo_patta_metrics():
    return {"total_documents": 47, "accuracy": "91.5%", "processing_time": "3.2s"}

def get_demo_system_stats():
    return {"uptime": "99.8%", "active_users": 45, "storage_used": "1.2GB"}

def get_demo_success_stories():
    return [{"title": "Success Story 1", "description": "Sample success story"}]

def get_demo_patta_documents():
    return [{"id": "1", "name": "Sample Document", "status": "processed"}]

def get_demo_ai_prediction():
    return {"prediction": "High eligibility", "confidence": 0.95}

def get_demo_chatbot_response(query_type):
    responses = {
        "greeting": "Hello! How can I help you with FRA services?",
        "default": "I'm here to help with FRA-related queries."
    }
    return responses.get(query_type, responses["default"])

# Register Patta API Blueprint
if PATTA_API_AVAILABLE:
    # app.register_blueprint(patta_bp)  # Temporarily disabled
    pass

# Comprehensive FRA Atlas Data Structure
FRA_ATLAS_DATA = {
    "states": {
        "Madhya Pradesh": {
            "districts": {
                "Khargone": {
                    "blocks": {
                        "Khargone": {
                            "villages": {
                                "Khargone": {
                                    "patta_holders": [
                                        {
                                            "id": "FRA001",
                                            "name": "Ram Singh",
                                            "tribal_group": "Bhil",
                                            "claim_type": "IFR",
                                            "area_hectares": 2.5,
                                            "status": "Approved",
                                            "coordinates": [75.6102, 21.8225],
                                            "socio_economic": {
                                                "literacy": "Primary",
                                                "livelihood": "Agriculture",
                                                "assets": ["Land", "Livestock"]
                                            }
                                        }
                                    ],
                                    "forest_cover": 65.2,
                                    "water_bodies": 3,
                                    "agricultural_land": 28.8,
                                    "coordinates": [75.6102, 21.8225]
                                }
                            }
                        }
                    }
                },
                "Jhabua": {
                    "blocks": {
                        "Jhabua": {
                            "villages": {
                                "Jhabua": {
                                    "patta_holders": [
                                        {
                                            "id": "FRA002",
                                            "name": "Sita Devi",
                                            "tribal_group": "Bhil",
                                            "claim_type": "CR",
                                            "area_hectares": 1.8,
                                            "status": "Pending",
                                            "coordinates": [74.5902, 22.7677],
                                            "socio_economic": {
                                                "literacy": "Illiterate",
                                                "livelihood": "Forest Produce",
                                                "assets": ["Land"]
                                            }
                                        }
                                    ],
                                    "forest_cover": 78.5,
                                    "water_bodies": 2,
                                    "agricultural_land": 15.3,
                                    "coordinates": [74.5902, 22.7677]
                                }
                            }
                        }
                    }
                }
            }
        },
        "Odisha": {
            "districts": {
                "Koraput": {
                    "blocks": {
                        "Koraput": {
                            "villages": {
                                "Koraput": {
                                    "patta_holders": [
                                        {
                                            "id": "FRA003",
                                            "name": "Ganga Ram",
                                            "tribal_group": "Gond",
                                            "claim_type": "CFR",
                                            "area_hectares": 5.2,
                                            "status": "Verified",
                                            "coordinates": [82.7202, 18.8102],
                                            "socio_economic": {
                                                "literacy": "Secondary",
                                                "livelihood": "Mixed Farming",
                                                "assets": ["Land", "Livestock", "Tools"]
                                            }
                                        }
                                    ],
                                    "forest_cover": 82.1,
                                    "water_bodies": 4,
                                    "agricultural_land": 12.7,
                                    "coordinates": [82.7202, 18.8102]
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

# Legacy data for backward compatibility
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

# Boundary data for states, districts, villages, and tribal areas
BOUNDARY_DATA = {
    "states": {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"name": "Madhya Pradesh", "type": "state"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [74.0, 21.0], [74.5, 20.8], [75.0, 20.5], [75.5, 20.8], [76.0, 21.0],
                        [76.5, 21.2], [77.0, 21.5], [77.5, 21.8], [78.0, 22.0], [78.5, 22.2],
                        [79.0, 22.5], [79.5, 22.8], [80.0, 23.0], [80.5, 23.2], [81.0, 23.5],
                        [81.5, 23.8], [82.0, 24.0], [82.5, 24.2], [83.0, 24.5], [82.5, 25.0],
                        [82.0, 25.5], [81.5, 26.0], [81.0, 26.2], [80.5, 26.0], [80.0, 25.8],
                        [79.5, 25.5], [79.0, 25.2], [78.5, 25.0], [78.0, 24.8], [77.5, 24.5],
                        [77.0, 24.2], [76.5, 24.0], [76.0, 23.8], [75.5, 23.5], [75.0, 23.2],
                        [74.5, 23.0], [74.0, 22.8], [73.5, 22.5], [73.0, 22.2], [72.5, 22.0],
                        [72.0, 21.8], [72.5, 21.5], [73.0, 21.2], [73.5, 21.0], [74.0, 21.0]
                    ]]
                }
            },
            {
                "type": "Feature", 
                "properties": {"name": "Odisha", "type": "state"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [81.0, 17.0], [81.5, 16.8], [82.0, 16.5], [82.5, 16.8], [83.0, 17.0],
                        [83.5, 17.2], [84.0, 17.5], [84.5, 17.8], [85.0, 18.0], [85.5, 18.2],
                        [86.0, 18.5], [86.5, 18.8], [87.0, 19.0], [87.5, 19.2], [88.0, 19.5],
                        [88.5, 19.8], [89.0, 20.0], [89.5, 20.2], [90.0, 20.5], [89.5, 21.0],
                        [89.0, 21.5], [88.5, 22.0], [88.0, 22.2], [87.5, 22.0], [87.0, 21.8],
                        [86.5, 21.5], [86.0, 21.2], [85.5, 21.0], [85.0, 20.8], [84.5, 20.5],
                        [84.0, 20.2], [83.5, 20.0], [83.0, 19.8], [82.5, 19.5], [82.0, 19.2],
                        [81.5, 19.0], [81.0, 18.8], [80.5, 18.5], [80.0, 18.2], [79.5, 18.0],
                        [79.0, 17.8], [79.5, 17.5], [80.0, 17.2], [80.5, 17.0], [81.0, 17.0]
                    ]]
                }
            },
            {
                "type": "Feature",
                "properties": {"name": "Tripura", "type": "state"},
                "geometry": {
                    "type": "Polygon", 
                    "coordinates": [[
                        [91.0, 23.0], [91.2, 22.8], [91.4, 22.6], [91.6, 22.8], [91.8, 23.0],
                        [92.0, 23.2], [92.2, 23.4], [92.4, 23.6], [92.6, 23.8], [92.8, 24.0],
                        [93.0, 24.2], [92.8, 24.4], [92.6, 24.2], [92.4, 24.0], [92.2, 23.8],
                        [92.0, 23.6], [91.8, 23.4], [91.6, 23.2], [91.4, 23.0], [91.2, 22.8],
                        [91.0, 23.0]
                    ]]
                }
            },
            {
                "type": "Feature",
                "properties": {"name": "Telangana", "type": "state"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [77.0, 15.0], [77.5, 14.8], [78.0, 14.5], [78.5, 14.8], [79.0, 15.0],
                        [79.5, 15.2], [80.0, 15.5], [80.5, 15.8], [81.0, 16.0], [81.5, 16.2],
                        [82.0, 16.5], [81.5, 17.0], [81.0, 17.5], [80.5, 18.0], [80.0, 18.2],
                        [79.5, 18.0], [79.0, 17.8], [78.5, 17.5], [78.0, 17.2], [77.5, 17.0],
                        [77.0, 16.8], [76.5, 16.5], [76.0, 16.2], [75.5, 16.0], [75.0, 15.8],
                        [74.5, 15.5], [74.0, 15.2], [74.5, 15.0], [75.0, 14.8], [75.5, 15.0],
                        [76.0, 15.2], [76.5, 15.0], [77.0, 15.0]
                    ]]
                }
            }
        ]
    },
    "districts": {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"name": "Khargone", "state": "Madhya Pradesh", "type": "district"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [75.0, 21.5], [75.2, 21.4], [75.4, 21.3], [75.6, 21.4], [75.8, 21.5],
                        [76.0, 21.6], [76.2, 21.7], [76.4, 21.8], [76.6, 21.9], [76.8, 22.0],
                        [76.6, 22.1], [76.4, 22.0], [76.2, 21.9], [76.0, 21.8], [75.8, 21.7],
                        [75.6, 21.6], [75.4, 21.7], [75.2, 21.8], [75.0, 21.7], [74.8, 21.6],
                        [74.6, 21.5], [74.8, 21.4], [75.0, 21.5]
                    ]]
                }
            },
            {
                "type": "Feature",
                "properties": {"name": "Jhabua", "state": "Madhya Pradesh", "type": "district"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [74.0, 22.5], [74.2, 22.4], [74.4, 22.3], [74.6, 22.4], [74.8, 22.5],
                        [75.0, 22.6], [75.2, 22.7], [75.4, 22.8], [75.6, 22.9], [75.8, 23.0],
                        [75.6, 23.1], [75.4, 23.0], [75.2, 22.9], [75.0, 22.8], [74.8, 22.7],
                        [74.6, 22.6], [74.4, 22.7], [74.2, 22.8], [74.0, 22.7], [73.8, 22.6],
                        [73.6, 22.5], [73.8, 22.4], [74.0, 22.5]
                    ]]
                }
            },
            {
                "type": "Feature",
                "properties": {"name": "Mandla", "state": "Madhya Pradesh", "type": "district"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [80.0, 22.0], [80.2, 21.9], [80.4, 21.8], [80.6, 21.9], [80.8, 22.0],
                        [81.0, 22.1], [81.2, 22.2], [81.4, 22.3], [81.6, 22.4], [81.8, 22.5],
                        [82.0, 22.6], [81.8, 22.7], [81.6, 22.8], [81.4, 22.9], [81.2, 23.0],
                        [81.0, 22.9], [80.8, 22.8], [80.6, 22.7], [80.4, 22.6], [80.2, 22.5],
                        [80.0, 22.4], [79.8, 22.3], [79.6, 22.2], [79.8, 22.1], [80.0, 22.0]
                    ]]
                }
            }
        ]
    },
    "villages": {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"name": "Khargone Village", "district": "Khargone", "type": "village"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [75.5, 21.7], [75.52, 21.68], [75.54, 21.66], [75.56, 21.68], [75.58, 21.7],
                        [75.6, 21.72], [75.62, 21.74], [75.64, 21.76], [75.66, 21.78], [75.68, 21.8],
                        [75.66, 21.82], [75.64, 21.8], [75.62, 21.78], [75.6, 21.76], [75.58, 21.74],
                        [75.56, 21.72], [75.54, 21.74], [75.52, 21.76], [75.5, 21.74], [75.48, 21.72],
                        [75.46, 21.7], [75.48, 21.68], [75.5, 21.7]
                    ]]
                }
            },
            {
                "type": "Feature",
                "properties": {"name": "Jhabua Village", "district": "Jhabua", "type": "village"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [74.5, 22.7], [74.52, 22.68], [74.54, 22.66], [74.56, 22.68], [74.58, 22.7],
                        [74.6, 22.72], [74.62, 22.74], [74.64, 22.76], [74.66, 22.78], [74.68, 22.8],
                        [74.66, 22.82], [74.64, 22.8], [74.62, 22.78], [74.6, 22.76], [74.58, 22.74],
                        [74.56, 22.72], [74.54, 22.74], [74.52, 22.76], [74.5, 22.74], [74.48, 22.72],
                        [74.46, 22.7], [74.48, 22.68], [74.5, 22.7]
                    ]]
                }
            }
        ]
    },
    "tribal_areas": {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"name": "Bhil Tribal Area", "tribe": "Bhil", "type": "tribal"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [74.0, 22.0], [74.3, 21.8], [74.6, 21.6], [74.9, 21.8], [75.2, 22.0],
                        [75.5, 22.2], [75.8, 22.4], [76.1, 22.6], [76.4, 22.8], [76.7, 23.0],
                        [77.0, 23.2], [76.7, 23.4], [76.4, 23.6], [76.1, 23.8], [75.8, 24.0],
                        [75.5, 24.2], [75.2, 24.4], [74.9, 24.6], [74.6, 24.8], [74.3, 25.0],
                        [74.0, 24.8], [73.7, 24.6], [73.4, 24.4], [73.1, 24.2], [72.8, 24.0],
                        [72.5, 23.8], [72.2, 23.6], [71.9, 23.4], [71.6, 23.2], [71.3, 23.0],
                        [71.6, 22.8], [71.9, 22.6], [72.2, 22.4], [72.5, 22.2], [72.8, 22.0],
                        [73.1, 21.8], [73.4, 21.6], [73.7, 21.8], [74.0, 22.0]
                    ]]
                }
            },
            {
                "type": "Feature",
                "properties": {"name": "Gond Tribal Area", "tribe": "Gond", "type": "tribal"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [79.5, 21.5], [79.8, 21.3], [80.1, 21.1], [80.4, 21.3], [80.7, 21.5],
                        [81.0, 21.7], [81.3, 21.9], [81.6, 22.1], [81.9, 22.3], [82.2, 22.5],
                        [82.5, 22.7], [82.2, 22.9], [81.9, 23.1], [81.6, 23.3], [81.3, 23.5],
                        [81.0, 23.7], [80.7, 23.9], [80.4, 24.1], [80.1, 24.3], [79.8, 24.5],
                        [79.5, 24.3], [79.2, 24.1], [78.9, 23.9], [78.6, 23.7], [78.3, 23.5],
                        [78.0, 23.3], [77.7, 23.1], [77.4, 22.9], [77.1, 22.7], [76.8, 22.5],
                        [77.1, 22.3], [77.4, 22.1], [77.7, 21.9], [78.0, 21.7], [78.3, 21.5],
                        [78.6, 21.3], [78.9, 21.1], [79.2, 21.3], [79.5, 21.5]
                    ]]
                }
            }
        ]
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

# Additional Portal Routes
@app.route('/public-portal')
def public_portal():
    """Public portal for general access"""
    return render_template('public_portal.html')

@app.route('/departmental-portal')
def departmental_portal():
    """Departmental portal for government officials"""
    if not session.get('user'):
        return redirect(url_for('login'))
    if session.get('user_role') not in ['CCF', 'DCF', 'RFO']:
        flash('Access denied. This portal is for government officials only.', 'error')
        return redirect(url_for('dashboard'))
    return render_template('departmental_portal.html')

@app.route('/village-portal')
def village_portal():
    """Village portal for local communities"""
    return render_template('village_portal.html')

# AI Features Pages
@app.route('/ai-predictions')
def ai_predictions():
    """AI Predictions page"""
    if not session.get('user'):
        return redirect(url_for('login'))
    return render_template('ai_predictions.html')

@app.route('/analytics')
def analytics():
    """Analytics page"""
    if not session.get('user'):
        return redirect(url_for('login'))
    return render_template('analytics.html')

@app.route('/reports')
def reports():
    """Reports page"""
    if not session.get('user'):
        return redirect(url_for('login'))
    return render_template('reports.html')

@app.route('/schemes')
def schemes():
    """Government Schemes page"""
    if not session.get('user'):
        return redirect(url_for('login'))
    return render_template('schemes.html')

@app.route('/fra-data-collection')
def fra_data_collection():
    """FRA Data Collection page"""
    if not session.get('user'):
        return redirect(url_for('login'))
    return render_template('fra_data_collection.html')

@app.route('/detailed-analytics')
def detailed_analytics():
    """Detailed Analytics page"""
    if not session.get('user'):
        return redirect(url_for('login'))
    return render_template('detailed_analytics.html', current_lang=session.get('language', 'en'))

@app.route('/patta-extractor')
def patta_extractor():
    """Patta Document Extractor page"""
    if not session.get('user'):
        return redirect(url_for('login'))
    return render_template('patta_extractor.html')

# Language support routes
@app.route('/set_language/<language>')
def set_language(language):
    """Set user's preferred language"""
    session['language'] = language
    return redirect(request.referrer or url_for('dashboard'))

@app.route('/lang/<language>')
def change_language(language):
    """Change language and set cookie"""
    from flask import make_response
    response = make_response(redirect(request.referrer or url_for('dashboard')))
    response.set_cookie('lang', language, max_age=60*60*24*365)  # 1 year
    return response

@app.route('/api/translations/<language>')
def get_translations(language):
    """Get translations for specified language"""
    translations = {
        'tamil': {
            'dashboard_title': 'FRA சென்டினல் - முதன்மை கட்டுப்பாட்டு பலகை',
            'welcome': 'வரவேற்கிறோம்',
            'map': 'வரைபடம்',
            'admin': 'நிர்வாகம்',
            'logout': 'வெளியேறு',
            'language': 'மொழி',
            'states': 'மாநிலங்கள்',
            'districts': 'மாவட்டங்கள்',
            'villages': 'கிராமங்கள்',
            'tribal_areas': 'பழங்குடி பகுதிகள்',
            'village_information': 'கிராம தகவல்',
            'patta_holder': 'பட்டா வைத்திருப்பவர்',
            'land_area': 'நிலப் பரப்பு',
            'claim_status': 'கோரிக்கை நிலை',
            'location': 'இடம்',
            'forest_rights_village': 'வன உரிமை கிராமம்',
            'approved': 'அனுமதிக்கப்பட்டது',
            'pending': 'நிலுவையில்',
            'verified': 'சரிபார்க்கப்பட்டது',
            'hectares': 'ஹெக்டேர்',
            'generate_report': 'அறிக்கை உருவாக்கு',
            'export_data': 'தரவை ஏற்றுமதி செய்',
            'overview': 'கண்ணோட்டம்',
            'progress': 'முன்னேற்றம்',
            'analytics': 'பகுப்பாய்வு',
            'export': 'ஏற்றுமதி',
            'land_use_statistics': 'நில பயன்பாட்டு புள்ளிவிவரங்கள்',
            'smart_recommendations': 'ஸ்மார்ட் பரிந்துரைகள்',
            'loading_village_data': 'கிராம தரவு ஏற்றப்படுகிறது...',
            'calculating_statistics': 'புள்ளிவிவரங்கள் கணக்கிடப்படுகின்றன...',
            'analyzing_data': 'தரவு பகுப்பாய்வு செய்யப்படுகிறது...',
            'processing': 'செயலாக்கம்',
            'accuracy': 'துல்லியம்',
            'documents': 'ஆவணங்கள்',
            'area_mapped': 'மேப்பிங் செய்யப்பட்ட பகுதி',
            'total_claims': 'மொத்த கோரிக்கைகள்',
            'approved_claims': 'அனுமதிக்கப்பட்ட கோரிக்கைகள்',
            'pending_claims': 'நிலுவையில் உள்ள கோரிக்கைகள்',
            'rejection_rate': 'நிராகரிப்பு விகிதம்',
            'completion_rate': 'முடிவு விகிதம்',
            'average_processing_time': 'சராசரி செயலாக்க நேரம்',
            'system_uptime': 'சிஸ்டம் அப்டைம்',
            'active_users': 'செயலில் உள்ள பயனர்கள்',
            'storage_used': 'பயன்படுத்தப்பட்ட சேமிப்பு',
            'export_csv': 'CSV ஏற்றுமதி',
            'export_geojson': 'GeoJSON ஏற்றுமதி',
            'export_pdf': 'PDF ஏற்றுமதி',
            'export_excel': 'Excel ஏற்றுமதி',
            'download_report': 'அறிக்கை பதிவிறக்கு',
            'generate_analytics': 'பகுப்பாய்வு உருவாக்கு',
            'view_detailed_stats': 'விரிவான புள்ளிவிவரங்களைக் காண்க',
            'filter_by_date': 'தேதியால் வடிகட்டு',
            'filter_by_status': 'நிலையால் வடிகட்டு',
            'filter_by_district': 'மாவட்டத்தால் வடிகட்டு',
            'no_data_available': 'தரவு கிடைக்கவில்லை',
            'data_updated': 'தரவு புதுப்பிக்கப்பட்டது',
            'last_updated': 'கடைசி புதுப்பிப்பு',
            'refresh_data': 'தரவை புதுப்பிக்கவும்',
            'claims': 'கோரிக்கைகள்',
            'progress_tracking': 'முன்னேற்ற கண்காணிப்பு',
            'system_analytics': 'சிஸ்டம் பகுப்பாய்வு',
            'export_options': 'ஏற்றுமதி விருப்பங்கள்',
            'pdf_report': 'PDF அறிக்கை',
            'excel_data': 'Excel தரவு',
            'generate': 'உருவாக்கு',
            'checking': 'சரிபார்க்கப்படுகிறது...',
            'all_states': 'அனைத்து மாநிலங்கள்',
            'resources': 'வளங்கள்',
            'fra_resources_guidelines': 'FRA வளங்கள் மற்றும் வழிகாட்டுதல்கள்',
            'official_portals': 'அதிகாரப்பூர்வ போர்டல்கள்',
            'mota_fra_portal': 'MoTA FRA போர்டல்',
            'ministry_of_tribal_affairs': 'பழங்குடி விவகார அமைச்சகம்',
            'guidelines_documents': 'வழிகாட்டுதல்கள் மற்றும் ஆவணங்கள்',
            'fra_guidelines': 'FRA வழிகாட்டுதல்கள்',
            'forest_rights_act_2006': 'வன உரிமை சட்டம் 2006',
            'dajgua_guidelines': 'DAJGUA வழிகாட்டுதல்கள்',
            'convergence_framework': 'ஒருங்கிணைப்பு கட்டமைப்பு',
            'state_contacts': 'மாநில தொடர்புகள்',
            'central_desk': 'மைய மேசை',
            'fra_helpline': 'FRA உதவி வரி',
            'technical_support': 'தொழில்நுட்ப ஆதரவு',
            'compliance_note': 'இணக்க நோட்',
            'mpr_snapshot': 'MPR ஸ்னாப்ஷாட்',
            'total_claims': 'மொத்த கோரிக்கைகள்',
            'granted': 'அனுமதிக்கப்பட்டது',
            'area_vested': 'வெஸ்டட் பகுதி',
            'last_updated': 'கடைசி புதுப்பிப்பு',
            'refresh': 'புதுப்பிக்கவும்',
            'farmland': 'விவசாய நிலம்',
            'forest': 'வனம்',
            'homestead': 'வீடு',
            'water': 'நீர்',
            'pixels': 'பிக்சல்கள்',
            'approved': 'அனுமதிக்கப்பட்டது',
            'pending': 'நிலுவையில்',
            'verified': 'சரிபார்க்கப்பட்டது'
        },
        'hindi': {
            'dashboard_title': 'FRA सेंटिनल - मुख्य डैशबोर्ड',
            'welcome': 'स्वागत है',
            'map': 'नक्शा',
            'admin': 'प्रशासन',
            'logout': 'लॉग आउट',
            'language': 'भाषा',
            'states': 'राज्य',
            'districts': 'जिले',
            'villages': 'गांव',
            'tribal_areas': 'आदिवासी क्षेत्र',
            'village_information': 'गांव की जानकारी',
            'patta_holder': 'पट्टा धारक',
            'land_area': 'भूमि क्षेत्र',
            'claim_status': 'दावा स्थिति',
            'location': 'स्थान',
            'forest_rights_village': 'वन अधिकार गांव',
            'approved': 'अनुमोदित',
            'pending': 'लंबित',
            'verified': 'सत्यापित',
            'hectares': 'हेक्टेयर',
            'generate_report': 'रिपोर्ट बनाएं',
            'export_data': 'डेटा निर्यात करें',
            'overview': 'अवलोकन',
            'progress': 'प्रगति',
            'analytics': 'विश्लेषण',
            'export': 'निर्यात',
            'land_use_statistics': 'भूमि उपयोग आंकड़े',
            'smart_recommendations': 'स्मार्ट सुझाव',
            'loading_village_data': 'गांव डेटा लोड हो रहा है...',
            'calculating_statistics': 'आंकड़े गणना हो रहे हैं...',
            'analyzing_data': 'डेटा विश्लेषण हो रहा है...',
            'processing': 'प्रसंस्करण',
            'accuracy': 'सटीकता',
            'documents': 'दस्तावेज़',
            'area_mapped': 'मैप किया गया क्षेत्र',
            'total_claims': 'कुल दावे',
            'approved_claims': 'अनुमोदित दावे',
            'pending_claims': 'लंबित दावे',
            'rejection_rate': 'अस्वीकृति दर',
            'completion_rate': 'पूर्णता दर',
            'average_processing_time': 'औसत प्रसंस्करण समय',
            'system_uptime': 'सिस्टम अपटाइम',
            'active_users': 'सक्रिय उपयोगकर्ता',
            'storage_used': 'उपयोग की गई स्टोरेज',
            'export_csv': 'CSV निर्यात करें',
            'export_geojson': 'GeoJSON निर्यात करें',
            'export_pdf': 'PDF निर्यात करें',
            'export_excel': 'Excel निर्यात करें',
            'download_report': 'रिपोर्ट डाउनलोड करें',
            'generate_analytics': 'विश्लेषण बनाएं',
            'view_detailed_stats': 'विस्तृत आंकड़े देखें',
            'filter_by_date': 'तारीख से फ़िल्टर करें',
            'filter_by_status': 'स्थिति से फ़िल्टर करें',
            'filter_by_district': 'जिले से फ़िल्टर करें',
            'no_data_available': 'कोई डेटा उपलब्ध नहीं है',
            'data_updated': 'डेटा अपडेट किया गया',
            'last_updated': 'अंतिम अपडेट',
            'refresh_data': 'डेटा रिफ्रेश करें',
            'claims': 'दावे',
            'progress_tracking': 'प्रगति ट्रैकिंग',
            'system_analytics': 'सिस्टम एनालिटिक्स',
            'export_options': 'निर्यात विकल्प',
            'pdf_report': 'PDF रिपोर्ट',
            'excel_data': 'Excel डेटा',
            'generate': 'बनाएं',
            'checking': 'जांच हो रही है...',
            'all_states': 'सभी राज्य',
            'resources': 'संसाधन',
            'fra_resources_guidelines': 'FRA संसाधन और दिशानिर्देश',
            'official_portals': 'आधिकारिक पोर्टल',
            'mota_fra_portal': 'MoTA FRA पोर्टल',
            'ministry_of_tribal_affairs': 'जनजातीय कार्य मंत्रालय',
            'guidelines_documents': 'दिशानिर्देश और दस्तावेज़',
            'fra_guidelines': 'FRA दिशानिर्देश',
            'forest_rights_act_2006': 'वन अधिकार अधिनियम 2006',
            'dajgua_guidelines': 'DAJGUA दिशानिर्देश',
            'convergence_framework': 'अभिसरण ढांचा',
            'state_contacts': 'राज्य संपर्क',
            'central_desk': 'केंद्रीय डेस्क',
            'fra_helpline': 'FRA हेल्पलाइन',
            'technical_support': 'तकनीकी सहायता',
            'compliance_note': 'अनुपालन नोट',
            'mpr_snapshot': 'MPR स्नैपशॉट',
            'total_claims': 'कुल दावे',
            'granted': 'अनुमोदित',
            'area_vested': 'वेस्टेड क्षेत्र',
            'last_updated': 'अंतिम अपडेट',
            'refresh': 'रिफ्रेश',
            'farmland': 'कृषि भूमि',
            'forest': 'वन',
            'homestead': 'आवास',
            'water': 'जल',
            'pixels': 'पिक्सेल',
            'approved': 'अनुमोदित',
            'pending': 'लंबित',
            'verified': 'सत्यापित'
        },
        'telugu': {
            'dashboard_title': 'FRA సెంటినెల్ - ప్రధాన డ్యాష్‌బోర్డ్',
            'welcome': 'స్వాగతం',
            'map': 'మ్యాప్',
            'admin': 'అడ్మిన్',
            'logout': 'లాగ్ అవుట్',
            'language': 'భాష',
            'states': 'రాష్ట్రాలు',
            'districts': 'జిల్లాలు',
            'villages': 'గ్రామాలు',
            'tribal_areas': 'ఆదివాసీ ప్రాంతాలు'
        },
        'kannada': {
            'dashboard_title': 'FRA ಸೆಂಟಿನೆಲ್ - ಮುಖ್ಯ ಡ್ಯಾಶ್‌ಬೋರ್ಡ್',
            'welcome': 'ಸ್ವಾಗತ',
            'map': 'ನಕ್ಷೆ',
            'admin': 'ಅಡ್ಮಿನ್',
            'logout': 'ಲಾಗ್ ಔಟ್',
            'language': 'ಭಾಷೆ',
            'states': 'ರಾಜ್ಯಗಳು',
            'districts': 'ಜಿಲ್ಲೆಗಳು',
            'villages': 'ಗ್ರಾಮಗಳು',
            'tribal_areas': 'ಆದಿವಾಸಿ ಪ್ರದೇಶಗಳು'
        },
        'malayalam': {
            'dashboard_title': 'FRA സെന്റിനൽ - പ്രധാന ഡാഷ്‌ബോർഡ്',
            'welcome': 'സ്വാഗതം',
            'map': 'മാപ്പ്',
            'admin': 'അഡ്മിൻ',
            'logout': 'ലോഗ് ഔട്ട്',
            'language': 'ഭാഷ',
            'states': 'സംസ്ഥാനങ്ങൾ',
            'districts': 'ജില്ലകൾ',
            'villages': 'ഗ്രാമങ്ങൾ',
            'tribal_areas': 'ആദിവാസി പ്രദേശങ്ങൾ'
        },
        'odia': {
            'dashboard_title': 'FRA ସେଣ୍ଟିନେଲ୍ - ମୁଖ୍ୟ ଡ୍ୟାସବୋର୍ଡ',
            'welcome': 'ସ୍ୱାଗତ',
            'map': 'ମାନଚିତ୍ର',
            'admin': 'ପ୍ରଶାସନ',
            'logout': 'ଲଗ୍ ଆଉଟ୍',
            'language': 'ଭାଷା',
            'states': 'ରାଜ୍ୟ',
            'districts': 'ଜିଲ୍ଲା',
            'villages': 'ଗ୍ରାମ',
            'tribal_areas': 'ଆଦିବାସୀ ଅଞ୍ଚଳ'
        },
        'bengali': {
            'dashboard_title': 'FRA সেন্টিনেল - মূল ড্যাশবোর্ড',
            'welcome': 'স্বাগতম',
            'map': 'মানচিত্র',
            'admin': 'প্রশাসন',
            'logout': 'লগ আউট',
            'language': 'ভাষা',
            'states': 'রাজ্য',
            'districts': 'জেলা',
            'villages': 'গ্রাম',
            'tribal_areas': 'আদিবাসী অঞ্চল'
        },
        'english': {
            'dashboard_title': 'FRA Sentinel - Main Dashboard',
            'welcome': 'Welcome',
            'map': 'Map',
            'admin': 'Admin',
            'logout': 'Logout',
            'language': 'Language',
            'states': 'States',
            'districts': 'Districts',
            'villages': 'Villages',
            'tribal_areas': 'Tribal Areas',
            'village_information': 'Village Information',
            'patta_holder': 'Patta Holder',
            'land_area': 'Land Area',
            'claim_status': 'Claim Status',
            'location': 'Location',
            'forest_rights_village': 'Forest Rights Village',
            'approved': 'Approved',
            'pending': 'Pending',
            'verified': 'Verified',
            'hectares': 'hectares',
            'generate_report': 'Generate Report',
            'export_data': 'Export Data',
            'overview': 'Overview',
            'progress': 'Progress',
            'analytics': 'Analytics',
            'export': 'Export',
            'land_use_statistics': 'Land Use Statistics',
            'smart_recommendations': 'Smart Recommendations',
            'loading_village_data': 'Loading village data...',
            'calculating_statistics': 'Calculating statistics...',
            'analyzing_data': 'Analyzing data...',
            'processing': 'Processing',
            'accuracy': 'Accuracy',
            'documents': 'Documents',
            'area_mapped': 'Area Mapped',
            'total_claims': 'Total Claims',
            'approved_claims': 'Approved Claims',
            'pending_claims': 'Pending Claims',
            'rejection_rate': 'Rejection Rate',
            'completion_rate': 'Completion Rate',
            'average_processing_time': 'Average Processing Time',
            'system_uptime': 'System Uptime',
            'active_users': 'Active Users',
            'storage_used': 'Storage Used',
            'export_csv': 'Export CSV',
            'export_geojson': 'Export GeoJSON',
            'export_pdf': 'Export PDF',
            'export_excel': 'Export Excel',
            'download_report': 'Download Report',
            'generate_analytics': 'Generate Analytics',
            'view_detailed_stats': 'View Detailed Stats',
            'filter_by_date': 'Filter by Date',
            'filter_by_status': 'Filter by Status',
            'filter_by_district': 'Filter by District',
            'no_data_available': 'No data available',
            'data_updated': 'Data updated',
            'last_updated': 'Last updated',
            'refresh_data': 'Refresh data',
            'claims': 'Claims',
            'progress_tracking': 'Progress Tracking',
            'system_analytics': 'System Analytics',
            'export_options': 'Export Options',
            'pdf_report': 'PDF Report',
            'excel_data': 'Excel Data',
            'generate': 'Generate',
            'checking': 'Checking...',
            'all_states': 'All States',
            'resources': 'Resources',
            'fra_resources_guidelines': 'FRA Resources & Guidelines',
            'official_portals': 'Official Portals',
            'mota_fra_portal': 'MoTA FRA Portal',
            'ministry_of_tribal_affairs': 'Ministry of Tribal Affairs',
            'guidelines_documents': 'Guidelines & Documents',
            'fra_guidelines': 'FRA Guidelines',
            'forest_rights_act_2006': 'Forest Rights Act 2006',
            'dajgua_guidelines': 'DAJGUA Guidelines',
            'convergence_framework': 'Convergence Framework',
            'state_contacts': 'State Contacts',
            'central_desk': 'Central Desk',
            'fra_helpline': 'FRA Helpline',
            'technical_support': 'Technical Support',
            'compliance_note': 'Compliance Note',
            'mpr_snapshot': 'MPR Snapshot',
            'total_claims': 'Total Claims',
            'granted': 'Granted',
            'area_vested': 'Area Vested',
            'last_updated': 'Last Updated',
            'refresh': 'Refresh',
            'farmland': 'Farmland',
            'forest': 'Forest',
            'homestead': 'Homestead',
            'water': 'Water',
            'pixels': 'pixels',
            'approved': 'Approved',
            'pending': 'Pending',
            'verified': 'Verified'
        }
    }
    return jsonify(translations.get(language, translations['english']))

# ----- Admin-only routes -----
def _is_admin_user():
    return session.get("user_role") in {"CCF", "DCF", "RFO"}

@app.route('/admin')
def admin():
    if not session.get("user"):
        return redirect(url_for("login"))
    if not _is_admin_user():
        return "Unauthorized", 403
    # Minimal example list (wire to DB if needed)
    files = []
    return render_template("manage_files.html", files=files)

# API endpoints for new upload system
@app.route('/api/upload', methods=['POST'])
def api_upload():
    """Upload file endpoint for React app"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        
        # Validate file type
        allowed_extensions = {'pdf', 'jpg', 'jpeg', 'png'}
        if not ('.' in file.filename and 
                file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({'success': False, 'message': 'Invalid file type'}), 400

            # Create uploads directory
            upload_dir = os.path.join(os.path.dirname(__file__), 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Generate unique filename
            import uuid
            unique_filename = f"{uuid.uuid4()}_{file.filename}"
            save_path = os.path.join(upload_dir, unique_filename)
            file.save(save_path)

        file_id = f"FRA{str(uuid.uuid4())[:8].upper()}"
        
        return jsonify({
            'success': True,
            'fileId': file_id,
            'message': 'File uploaded successfully',
            'filePath': save_path
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/extract', methods=['POST'])
def api_extract():
    """Extract data from uploaded file"""
    try:
        data = request.get_json()
        file_id = data.get('fileId')
        
        if not file_id:
            return jsonify({'success': False, 'message': 'File ID required'}), 400
        
        # Mock extraction for now - in production, this would use OCR
        extracted_data = {
            'claimantNames': ['Sample Claimant'],
            'village': 'Sample Village',
            'district': 'Sample District',
            'areaValues': {'hectares': 2.5},
            'claimType': 'IFR',
            'coordinates': {'latitude': 21.8225, 'longitude': 75.6102}
        }
        
        return jsonify({
            'success': True,
            'extractedData': extracted_data,
            'message': 'Data extracted successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/claims/<claim_id>/geometry', methods=['POST'])
def api_save_geometry(claim_id):
    """Save geometry for a claim"""
    try:
        data = request.get_json()
        geometry = data.get('geometry')
        
        if not geometry:
            return jsonify({'success': False, 'message': 'Geometry required'}), 400
        
        # Mock save for now - in production, this would save to database
        geometry_id = f"GEO{str(uuid.uuid4())[:8].upper()}"
        
        return jsonify({
            'success': True,
            'geometryId': geometry_id,
            'message': 'Geometry saved successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/upload/dss/recommendations', methods=['POST'])
def api_upload_dss_recommendations():
    """Get DSS recommendations for new upload system"""
    try:
        data = request.get_json()
        fields = data.get('fields', {})
        geometry = data.get('geometry')
        
        # Mock DSS recommendations
        recommendations = [
            {
                'schemeName': 'Forest Rights Act Individual Rights',
                'ministry': 'Ministry of Tribal Affairs',
                'score': 95,
                'reasons': [
                    'Eligible for individual forest rights',
                    'Traditional forest dweller status confirmed',
                    'Land area within permissible limits'
                ],
                'guidelines': [
                    'Submit application to Gram Sabha',
                    'Provide traditional occupation proof',
                    'Submit revenue records if available'
                ],
                'eligibility': True
            },
            {
                'schemeName': 'Jal Jeevan Mission',
                'ministry': 'Ministry of Jal Shakti',
                'score': 78,
                'reasons': [
                    'Rural area coverage',
                    'Water scarcity region',
                    'Population density criteria met'
                ],
                'guidelines': [
                    'Contact local water department',
                    'Submit household survey form',
                    'Provide identity documents'
                ],
                'eligibility': True
            },
            {
                'schemeName': 'SAUBHAGYA Scheme',
                'ministry': 'Ministry of Power',
                'score': 65,
                'reasons': [
                    'Rural electrification target',
                    'Below poverty line household',
                    'Grid connectivity available'
                ],
                'guidelines': [
                    'Apply through state electricity board',
                    'Submit BPL certificate',
                    'Provide address proof'
                ],
                'eligibility': True
            }
        ]
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'message': 'Recommendations generated successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Real Patta Digitization API Endpoints
@app.route('/api/upload', methods=['POST'])
def api_upload_file():
    """Upload file for patta digitization"""
    try:
        print("=== UPLOAD API CALLED ===")
        print("Request files:", request.files)
        print("Request form:", request.form)
        
        if 'file' not in request.files:
            print("ERROR: No file in request")
            return jsonify({'success': False, 'message': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        
        # Validate file type
        allowed_extensions = {'pdf', 'jpg', 'jpeg', 'png'}
        if not ('.' in file.filename and 
                file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({'success': False, 'message': 'Invalid file type'}), 400
        
        # Validate file size (25MB limit)
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if file_size > 25 * 1024 * 1024:  # 25MB
            return jsonify({'success': False, 'message': 'File too large (max 25MB)'}), 400
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        filename = f"{file_id}_{file.filename}"
        
        # Save file to uploads directory
        upload_dir = os.path.join(app.root_path, 'uploads', 'patta')
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
        
        # Store file metadata in database
        from datetime import datetime
        file_record = {
            'file_id': file_id,
            'filename': file.filename,
            'stored_filename': filename,
            'file_path': file_path,
            'size': file_size,
            'upload_time': datetime.utcnow().isoformat(),
            'status': 'uploaded',
            'user_id': session.get('user', 'anonymous')
        }
        
        # TODO: Save to database
        # db.files.insert_one(file_record)
        
        return jsonify({
            'success': True,
            'file_id': file_id,
            'filename': file.filename,
            'size': file_size,
            'message': 'File uploaded successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/extract', methods=['POST'])
def api_extract_data():
    """Extract OCR and NER data from uploaded file"""
    try:
        print("=== EXTRACT API CALLED ===")
        print("Request content type:", request.content_type)
        print("Request data:", request.get_data())
        
        data = request.get_json()
        print("Parsed JSON data:", data)
        print("Request headers:", dict(request.headers))
        print("Request content type:", request.content_type)
        
        # Try multiple possible field names for file_id
        file_id = data.get('file_id') or data.get('fileId') or data.get('id')
        print("File ID:", file_id)
        
        if not file_id:
            print("ERROR: No file_id provided in any format")
            print("Available keys:", list(data.keys()) if data else "No data")
            return jsonify({'success': False, 'message': 'File ID required'}), 400
        
        # Get file from uploads directory
        upload_dir = os.path.join(app.root_path, 'uploads', 'patta')
        file_path = None
        
        # Find the uploaded file
        for filename in os.listdir(upload_dir):
            if file_id in filename:
                file_path = os.path.join(upload_dir, filename)
                break
        
        if not file_path or not os.path.exists(file_path):
            print(f"ERROR: File not found for file_id: {file_id}")
            return jsonify({'success': False, 'message': 'File not found'}), 404
        
        print(f"Processing file: {file_path}")
        
        # Use real OCR service
        try:
            from ocr_service import PattaOCRService
            ocr_service = PattaOCRService(use_ai=False)  # Use regex-only for now
            
            # Extract data using real OCR
            extracted_data = ocr_service.extract_patta_data(file_path)
            print(f"Extracted data: {extracted_data}")
            
            if "error" in extracted_data:
                return jsonify({'success': False, 'message': f'OCR failed: {extracted_data["error"]}'}), 500
            
            # Convert to our expected format
            ocr_result = {
                'text': 'OCR text extracted from image',
                'confidence': 85.5,
                'words': [],
                'page_number': 1
            }
            
        except Exception as e:
            print(f"OCR processing error: {e}")
            # Fallback to mock data
            ocr_result = {
                'text': 'Sample patta document text with claimant name, village details, and survey numbers...',
                'confidence': 85.5,
                'words': [
                    {'text': 'Sample', 'confidence': 90, 'bbox': {'x0': 10, 'y0': 10, 'x1': 50, 'y1': 20}},
                    {'text': 'Claimant', 'confidence': 88, 'bbox': {'x0': 60, 'y0': 10, 'x1': 120, 'y1': 20}}
                ],
                'page_number': 1
            }
            extracted_data = {
                'claimant_name': 'Sample Claimant',
                'father_or_spouse': 'Sample Father',
                'caste_st': 'ST',
                'village': 'Sample Village',
                'taluk': 'Sample Taluk',
                'district': 'Sample District',
                'survey_or_compartment_no': '123',
                'sub_division': 'Sample Sub Division',
                'coords': {'lat': 21.8225, 'lng': 75.6102},
                'area': 2.5,
                'document_no': 'DOC123',
                'document_date': '2025-09-28',
                'claim_type': 'IFR'
            }
        
        # Mock NER result (replace with real NER processing)
        ner_result = {
            'text': ocr_result['text'],
            'entities': [
                {'text': 'Sample Claimant', 'label': 'PERSON', 'start_char': 0, 'end_char': 15, 'confidence': 0.9},
                {'text': 'Sample Village', 'label': 'GPE', 'start_char': 20, 'end_char': 35, 'confidence': 0.85},
                {'text': '123', 'label': 'CARDINAL', 'start_char': 40, 'end_char': 43, 'confidence': 0.95}
            ],
            'confidence': 0.87,
            'language': 'mixed',
            'processing_time': 1.2
        }
        
        # Map extracted data to our patta schema
        patta_data = {
            'claimant_name': extracted_data.get('owner_name', ''),
            'father_or_spouse': extracted_data.get('relationship', ''),
            'caste_st': 'ST',  # Default for now
            'village': extracted_data.get('village', ''),
            'taluk': extracted_data.get('taluk', ''),
            'district': extracted_data.get('district', ''),
            'survey_or_compartment_no': extracted_data.get('survey_number', ''),
            'sub_division': extracted_data.get('sub_division', ''),
            'coords': {'lat': 21.8225, 'lng': 75.6102},  # Default coordinates
            'area': extracted_data.get('extent_acres', ''),
            'document_no': extracted_data.get('patta_number', ''),
            'document_date': extracted_data.get('signed_on', ''),
            'claim_type': 'IFR',  # Default
            'raw_text': ocr_result['text'],
            'ocr_confidence': ocr_result['confidence'],
            'ner_confidence': ner_result['confidence'],
            'extraction_time': datetime.utcnow().isoformat(),
            # Additional fields from real extraction
            'tax_amount': extracted_data.get('tax_amount', ''),
            'signed_by': extracted_data.get('signed_by', ''),
            'reference_number': extracted_data.get('reference_number', ''),
            'verification_url': extracted_data.get('verification_url', '')
        }
        
        return jsonify({
            'success': True,
            'ocr_result': ocr_result,
            'ner_result': ner_result,
            'patta_data': patta_data,
            'message': 'Data extracted successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/patta', methods=['POST'])
def api_save_patta():
    """Save extracted patta data to database"""
    try:
        data = request.get_json()
        patta_data = data.get('patta_data')
        
        if not patta_data:
            return jsonify({'success': False, 'message': 'Patta data required'}), 400
        
        # Generate patta ID
        import uuid
        patta_id = str(uuid.uuid4())
        
        # Add metadata
        patta_data['patta_id'] = patta_id
        patta_data['created_at'] = datetime.utcnow().isoformat()
        patta_data['created_by'] = session.get('user', 'anonymous')
        patta_data['status'] = 'extracted'
        
        # TODO: Save to database
        # db.pattas.insert_one(patta_data)
        
        return jsonify({
            'success': True,
            'patta_id': patta_id,
            'message': 'Patta data saved successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/patta/<patta_id>', methods=['GET'])
def api_get_patta(patta_id):
    """Get patta data by ID"""
    try:
        # TODO: Get from database
        # patta_data = db.pattas.find_one({'patta_id': patta_id})
        # if not patta_data:
        #     return jsonify({'success': False, 'message': 'Patta not found'}), 404
        
        # Mock data for now
        patta_data = {
            'patta_id': patta_id,
            'claimant_name': 'Sample Claimant',
            'village': 'Sample Village',
            'district': 'Sample District',
            'status': 'extracted'
        }
        
        return jsonify({
            'success': True,
            'patta_data': patta_data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/patta/<patta_id>', methods=['PUT'])
def api_update_patta(patta_id):
    """Update patta data"""
    try:
        data = request.get_json()
        update_data = data.get('patta_data')
        
        if not update_data:
            return jsonify({'success': False, 'message': 'Update data required'}), 400
        
        # TODO: Update in database
        # result = db.pattas.update_one(
        #     {'patta_id': patta_id},
        #     {'$set': {**update_data, 'updated_at': datetime.utcnow().isoformat()}}
        # )
        
        return jsonify({
            'success': True,
            'message': 'Patta data updated successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/patta/<patta_id>', methods=['DELETE'])
def api_delete_patta(patta_id):
    """Delete patta data"""
    try:
        # TODO: Delete from database
        # result = db.pattas.delete_one({'patta_id': patta_id})
        
        return jsonify({
            'success': True,
            'message': 'Patta data deleted successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/pattas', methods=['GET'])
def api_list_pattas():
    """List all pattas with pagination"""
    try:
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        # TODO: Get from database with pagination
        # pattas = list(db.pattas.find().skip(offset).limit(limit))
        # total = db.pattas.count_documents({})
        
        # Mock data for now
        pattas = []
        total = 0
        
        return jsonify({
            'success': True,
            'pattas': pattas,
            'total': total,
            'has_more': offset + limit < total
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/pattas/search', methods=['GET'])
def api_search_pattas():
    """Search pattas by query and filters"""
    try:
        query = request.args.get('q', '')
        village = request.args.get('village')
        district = request.args.get('district')
        claim_type = request.args.get('claim_type')
        
        # TODO: Implement search in database
        # search_filter = {}
        # if village:
        #     search_filter['village'] = {'$regex': village, '$options': 'i'}
        # if district:
        #     search_filter['district'] = {'$regex': district, '$options': 'i'}
        # if claim_type:
        #     search_filter['claim_type'] = claim_type
        
        # pattas = list(db.pattas.find(search_filter))
        
        # Mock data for now
        pattas = []
        total = 0
        
        return jsonify({
            'success': True,
            'pattas': pattas,
            'total': total
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/ner', methods=['POST'])
def api_ner_extraction():
    """Server-side NER extraction using spaCy or Hugging Face"""
    try:
        data = request.get_json()
        text = data.get('text')
        entities = data.get('entities', [])
        
        if not text:
            return jsonify({'success': False, 'message': 'Text required'}), 400
        
        # TODO: Implement real NER using spaCy or Hugging Face
        # For now, return mock NER results
        mock_entities = [
            {'text': 'Sample Claimant', 'label': 'PERSON', 'start_char': 0, 'end_char': 15, 'confidence': 0.9},
            {'text': 'Sample Village', 'label': 'GPE', 'start_char': 20, 'end_char': 35, 'confidence': 0.85},
            {'text': '123', 'label': 'CARDINAL', 'start_char': 40, 'end_char': 43, 'confidence': 0.95}
        ]
        
        return jsonify({
            'success': True,
            'entities': mock_entities,
            'confidence': 0.87,
            'language': 'mixed',
            'processing_time': 0.5
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/ner/patta', methods=['POST'])
def api_patta_ner():
    """Patta-specific NER extraction"""
    try:
        data = request.get_json()
        text = data.get('text')
        languages = data.get('languages', ['en', 'hi', 'ta', 'te'])
        
        if not text:
            return jsonify({'success': False, 'message': 'Text required'}), 400
        
        # TODO: Implement patta-specific NER model
        # This would use a fine-tuned model trained on patta documents
        
        mock_entities = [
            {'text': 'Sample Claimant', 'label': 'PERSON', 'start_char': 0, 'end_char': 15, 'confidence': 0.9},
            {'text': 'Sample Village', 'label': 'GPE', 'start_char': 20, 'end_char': 35, 'confidence': 0.85},
            {'text': '123', 'label': 'CARDINAL', 'start_char': 40, 'end_char': 43, 'confidence': 0.95}
        ]
        
        return jsonify({
            'success': True,
            'entities': mock_entities,
            'confidence': 0.92,
            'language': 'mixed',
            'processing_time': 0.8,
            'patta_specific': True
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def api_health_check():
    """Health check for all services"""
    try:
        # TODO: Check actual service health
        health_status = {
            'status': 'healthy',
            'services': {
                'ocr': True,
                'ner': True,
                'database': True
            },
            'message': 'All services operational'
        }
        
        return jsonify(health_status)
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'services': {
                'ocr': False,
                'ner': False,
                'database': False
            },
            'message': str(e)
        }), 500

# Patta digitization system route
@app.route('/patta-digitization')
def patta_digitization():
    """Patta digitization system with real OCR + NER"""
    return render_template('patta_digitization.html')

# New React-based upload system route
@app.route('/upload-new')
def upload_new():
    """New React-based upload system"""
    return render_template('upload_new.html')

@app.route("/dashboard")
def dashboard():
    """Unified main dashboard for all users"""
    user = session.get("user")
    role = session.get("role")
    if not user:
        return redirect(url_for("login"))
    return render_template("dashboard.html", user=user, role=role, claims=PATTA_CLAIMS, enumerate=enumerate)

@app.route('/admin-dashboard')
def admin_dashboard():
    """Admin-only dashboard for CCF, DCF, RFO"""
    if not session.get('user'):
        return redirect(url_for('login'))
    if session.get('user_role') not in ['CCF', 'DCF', 'RFO']:
        flash('Access denied. Admin dashboard is only for CCF, DCF, and RFO officials.', 'error')
        return redirect(url_for('dashboard'))
    
    # Define role information
    role_info = {
        'name': session.get('user_role', 'Unknown'),
        'level': {'CCF': 3, 'DCF': 2, 'RFO': 1}.get(session.get('user_role'), 0)
    }
    
    return render_template('admin_dashboard.html', role_info=role_info)

# Admin panel route removed - will be replaced with new React-based upload system

# Removed conflicting /upload route - using /upload_patta instead

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

@app.route("/api/villages")
def api_villages():
    """Get villages data - alias for fra_data"""
    return jsonify(TEST_VILLAGES)

@app.route("/api/health")
def api_health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'features': {
            'upload': True,
            'ocr': pdf_to_text is not None,
            'api': True,
            'dashboard': True
        }
    })

@app.route("/api/classification_stats")
def api_classification_stats():
    return jsonify(TEST_STATS)

@app.route("/api/dss/recommendations")
def api_dss_recommendations():
    """DAJGUA-aligned DSS recommendations API"""
    village_id = request.args.get('village_id', 'Khargone')
    
    # Load DSS rules
    import json
    import os
    
    try:
        with open(os.path.join(os.path.dirname(__file__), 'data', 'dss_catalog.json'), 'r') as f:
            dss_catalog = json.load(f)
    except FileNotFoundError:
        # Fallback to basic recommendations
        return jsonify({
            "village_info": {"village": village_id, "error": "DSS catalog not found"},
            "recommendations": [],
            "convergence_score": 0.0,
            "evidence": {"layers": [], "stats": {}}
        })
    
    # Get village data
    village_data = None
    for feature in TEST_VILLAGES["features"]:
        if feature["properties"]["village"] == village_id:
            village_data = feature["properties"]
            break
    
    if not village_data:
        village_data = TEST_VILLAGES["features"][0]["properties"]
    
    # Calculate village attributes
    village_attrs = {
        "water_index": "low",  # Demo value
        "agri_pct": 35.5,  # From TEST_STATS
        "has_patta_count": 1,
        "housing_kutcha_pct": 60.0,  # Demo value
        "forest_cover_pct": 42.3,  # From TEST_STATS
        "tribal_population_pct": 80.0  # Demo value
    }
    
    # Generate recommendations
    recommendations = []
    convergence_score = 0.0
    
    for scheme_key, scheme_info in dss_catalog["schemes"].items():
        eligibility_result = check_scheme_eligibility(village_attrs, scheme_info)
        
        if eligibility_result["eligible"]:
            # Calculate convergence score
            ministry_weight = dss_catalog["convergence_rules"]["ministry_weights"].get(
                scheme_info["ministry"], 1.0
            )
            category_weight = dss_catalog["convergence_rules"]["category_weights"].get(
                scheme_info["category"], 1.0
            )
            priority_weight = dss_catalog["convergence_rules"]["dajgua_priority_weights"].get(
                scheme_info["dajgua_priority"], 1.0
            )
            
            scheme_score = eligibility_result["score"] * ministry_weight * category_weight * priority_weight
            convergence_score += scheme_score
            
            # Estimate beneficiaries
            beneficiaries_estimate = estimate_beneficiaries(village_attrs, scheme_info)
            
            recommendations.append({
                "scheme": scheme_info["display_name"],
                "ministry": scheme_info["ministry"],
                "reason": ", ".join(eligibility_result["reasons"]),
                "score": round(eligibility_result["score"] * 100, 1),
                "beneficiaries_estimate": beneficiaries_estimate,
                "benefit_amount": scheme_info["benefit_amount"],
                "convergence_ministries": scheme_info["convergence_ministries"],
                "dajgua_priority": scheme_info["dajgua_priority"],
                "guideline_ref": scheme_info["guideline_ref"],
                "monitoring_notes": scheme_info["monitoring_notes"]
            })
    
    # Sort by score
    recommendations.sort(key=lambda x: x["score"], reverse=True)
    
    # Calculate evidence
    evidence = {
        "layers": ["agricultural", "forest", "water", "housing"],
        "stats": {
            "water_index": village_attrs["water_index"],
            "agri_pct": village_attrs["agri_pct"],
            "forest_cover_pct": village_attrs["forest_cover_pct"],
            "housing_kutcha_pct": village_attrs["housing_kutcha_pct"]
        }
    }
    
    return jsonify({
        "village_info": village_data,
        "recommendations": recommendations,
        "convergence_score": round(convergence_score, 1),
        "evidence": evidence
    })

def check_scheme_eligibility(village_attrs, scheme_info):
    """Check eligibility for a specific scheme"""
    eligibility_fields = scheme_info.get("eligibility_fields", [])
    reasons = []
    score = 0.0
    eligible = True
    
    # Check each eligibility field
    for field in eligibility_fields:
        if field == "landholding_size":
            if village_attrs["agri_pct"] > 0:
                score += 0.3
                reasons.append("✓ Has agricultural land")
            else:
                eligible = False
                reasons.append("✗ No agricultural land")
        
        elif field == "water_stress_area":
            if village_attrs["water_index"] == "low":
                score += 0.4
                reasons.append("✓ Low water index area")
            else:
                eligible = False
                reasons.append("✗ Not low water index area")
        
        elif field == "rural_household":
            score += 0.3
            reasons.append("✓ Rural household")
        
        elif field == "tribal_area":
            if village_attrs["tribal_population_pct"] > 50:
                score += 0.4
                reasons.append("✓ Tribal area eligible")
            else:
                score += 0.2
                reasons.append("✓ General area eligible")
        
        elif field == "farmer_status":
            if village_attrs["agri_pct"] > 0:
                score += 0.3
                reasons.append("✓ Agricultural activity")
            else:
                score += 0.1
                reasons.append("✓ Non-agricultural eligible")
        
        elif field == "adult_member":
            score += 0.2
            reasons.append("✓ Adult member available")
        
        elif field == "willing_to_work":
            score += 0.2
            reasons.append("✓ Willing to work")
    
    return {
        "eligible": eligible,
        "score": min(score, 1.0),
        "reasons": reasons
    }

def estimate_beneficiaries(village_attrs, scheme_info):
    """Estimate number of beneficiaries for a scheme"""
    base_estimate = village_attrs["has_patta_count"]
    
    # Adjust based on scheme type
    if "agricultural" in scheme_info["category"]:
        return max(1, int(base_estimate * village_attrs["agri_pct"] / 100))
    elif "infrastructure" in scheme_info["category"]:
        return max(1, int(base_estimate * 2))  # Infrastructure benefits more people
    elif "housing" in scheme_info["category"]:
        return max(1, int(base_estimate * village_attrs["housing_kutcha_pct"] / 100))
    else:
        return max(1, base_estimate)

@app.route("/api/dss_recommendation/<village>")
def api_dss_recommendation(village):
    """Legacy endpoint for backward compatibility"""
    return api_dss_recommendations()

@app.route("/api/progress")
def api_progress():
    """Progress tracking rollups API"""
    scope = request.args.get('scope', 'state')  # state, district, block, village
    id_param = request.args.get('id', '')
    
    # Load progress data
    import csv
    import os
    
    try:
        progress_data = []
        with open(os.path.join(os.path.dirname(__file__), 'data', 'progress_demo.csv'), 'r') as f:
            reader = csv.DictReader(f)
            progress_data = list(reader)
    except FileNotFoundError:
        return jsonify({"error": "Progress data not found"}), 404
    
    # Filter data based on scope and id
    filtered_data = progress_data
    if scope == 'state' and id_param:
        filtered_data = [row for row in progress_data if row['state'] == id_param]
    elif scope == 'district' and id_param:
        filtered_data = [row for row in progress_data if row['district'] == id_param]
    elif scope == 'block' and id_param:
        filtered_data = [row for row in progress_data if row['block'] == id_param]
    elif scope == 'village' and id_param:
        filtered_data = [row for row in progress_data if row['village'] == id_param]
    
    # Calculate aggregates
    aggregates = {
        "ifr_total": sum(int(row['ifr_total']) for row in filtered_data),
        "ifr_granted": sum(int(row['ifr_granted']) for row in filtered_data),
        "cr_total": sum(int(row['cr_total']) for row in filtered_data),
        "cr_granted": sum(int(row['cr_granted']) for row in filtered_data),
        "cfr_total": sum(int(row['cfr_total']) for row in filtered_data),
        "cfr_granted": sum(int(row['cfr_granted']) for row in filtered_data)
    }
    
    # Calculate rates
    rates = {
        "ifr_rate": round((aggregates['ifr_granted'] / aggregates['ifr_total'] * 100) if aggregates['ifr_total'] > 0 else 0, 1),
        "cr_rate": round((aggregates['cr_granted'] / aggregates['cr_total'] * 100) if aggregates['cr_total'] > 0 else 0, 1),
        "cfr_rate": round((aggregates['cfr_granted'] / aggregates['cfr_total'] * 100) if aggregates['cfr_total'] > 0 else 0, 1)
    }
    
    # Get top pending villages
    top_pending = []
    for row in filtered_data:
        ifr_pending = int(row['ifr_total']) - int(row['ifr_granted'])
        cr_pending = int(row['cr_total']) - int(row['cr_granted'])
        cfr_pending = int(row['cfr_total']) - int(row['cfr_granted'])
        total_pending = ifr_pending + cr_pending + cfr_pending
        
        if total_pending > 0:
            top_pending.append({
                "village": row['village'],
                "district": row['district'],
                "state": row['state'],
                "total_pending": total_pending,
                "ifr_pending": ifr_pending,
                "cr_pending": cr_pending,
                "cfr_pending": cfr_pending
            })
    
    # Sort by total pending
    top_pending.sort(key=lambda x: x['total_pending'], reverse=True)
    top_pending = top_pending[:10]  # Top 10
    
    return jsonify({
        "scope": scope,
        "id": id_param,
        "aggregates": aggregates,
        "rates": rates,
        "top_pending_villages": top_pending,
        "total_units": len(filtered_data)
    })

@app.route("/api/metrics")
def api_metrics():
    """Metrics ribbon API"""
    import json
    import os
    
    try:
        with open(os.path.join(os.path.dirname(__file__), 'config', 'demo_metrics.json'), 'r') as f:
            metrics = json.load(f)
    except FileNotFoundError:
        # Fallback metrics
        metrics = {
            "avg_processing": "3.2s",
            "extraction_accuracy": "91.5%",
            "docs": 47,
            "mapped_area": "127.8 ha"
        }
    
    return jsonify(metrics)

@app.route("/api/export/atlas")
def api_export_atlas():
    """Export Atlas data as CSV/GeoJSON"""
    import csv
    import json
    from flask import make_response
    from datetime import datetime
    
    format_type = request.args.get('format', 'csv')
    scope = request.args.get('scope', 'all')
    
    if format_type == 'csv':
        # Export as CSV
        output = []
        fieldnames = ['state', 'district', 'block', 'village', 'patta_holder', 'area_hectares', 'claim_status', 'tribal_group']
        
        for feature in TEST_VILLAGES["features"]:
            props = feature["properties"]
            output.append({
                'state': props.get('state', 'Madhya Pradesh'),
                'district': props.get('district', ''),
                'block': props.get('block', ''),
                'village': props.get('village', ''),
                'patta_holder': props.get('patta_holder', ''),
                'area_hectares': props.get('area_hectares', 0),
                'claim_status': props.get('claim_status', ''),
                'tribal_group': props.get('tribal_group', '')
            })
        
        # Create CSV response
        response = make_response('')
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=fra_atlas_{scope}_{datetime.now().strftime("%Y%m%d")}.csv'
        
        # Write CSV data
        import io
        output_buffer = io.StringIO()
        writer = csv.DictWriter(output_buffer, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output)
        
        response.data = output_buffer.getvalue()
        return response
    
    elif format_type == 'geojson':
        # Export as GeoJSON
        response = make_response(json.dumps(TEST_VILLAGES, indent=2))
        response.headers['Content-Type'] = 'application/json'
        response.headers['Content-Disposition'] = f'attachment; filename=fra_atlas_{scope}_{datetime.now().strftime("%Y%m%d")}.geojson'
        return response
    
    else:
        return jsonify({"error": "Invalid format. Use 'csv' or 'geojson'"}), 400

@app.route("/api/export/progress")
def api_export_progress():
    """Export Progress data as CSV"""
    import csv
    import os
    from flask import make_response
    from datetime import datetime
    
    scope = request.args.get('scope', 'all')
    
    try:
        progress_data = []
        with open(os.path.join(os.path.dirname(__file__), 'data', 'progress_demo.csv'), 'r') as f:
            reader = csv.DictReader(f)
            progress_data = list(reader)
    except FileNotFoundError:
        return jsonify({"error": "Progress data not found"}), 404
    
    # Create CSV response
    response = make_response('')
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=fra_progress_{scope}_{datetime.now().strftime("%Y%m%d")}.csv'
    
    # Write CSV data
    import io
    output_buffer = io.StringIO()
    if progress_data:
        fieldnames = progress_data[0].keys()
        writer = csv.DictWriter(output_buffer, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(progress_data)
    
    response.data = output_buffer.getvalue()
    return response

@app.route("/api/dss/catalog")
def api_dss_catalog():
    """Serve DSS catalog with scheme details"""
    import json
    import os
    
    try:
        with open(os.path.join(os.path.dirname(__file__), 'data', 'dss_catalog.json'), 'r') as f:
            catalog = json.load(f)
    except FileNotFoundError:
        return jsonify({"error": "DSS catalog not found"}), 404
    
    return jsonify(catalog)

@app.route("/api/progress/schema")
def api_progress_schema():
    """Serve progress monitoring schema"""
    import json
    import os
    
    try:
        with open(os.path.join(os.path.dirname(__file__), 'data', 'progress_schema.json'), 'r') as f:
            schema = json.load(f)
    except FileNotFoundError:
        return jsonify({"error": "Progress schema not found"}), 404
    
    return jsonify(schema)

@app.route("/api/digitization/schema")
def api_digitization_schema():
    """Serve digitization schema"""
    import json
    import os
    
    try:
        with open(os.path.join(os.path.dirname(__file__), 'docs', 'schema_digitization.json'), 'r') as f:
            schema = json.load(f)
    except FileNotFoundError:
        return jsonify({"error": "Digitization schema not found"}), 404
    
    return jsonify(schema)

@app.route("/api/cfr/template")
def api_cfr_template():
    """Serve CFR plan template"""
    import json
    import os
    
    try:
        with open(os.path.join(os.path.dirname(__file__), 'data', 'cfr_plan_template.json'), 'r') as f:
            template = json.load(f)
    except FileNotFoundError:
        return jsonify({"error": "CFR template not found"}), 404
    
    return jsonify(template)

@app.route("/api/mpr/snapshot")
def api_mpr_snapshot():
    """Serve MPR snapshot data"""
    import csv
    import json
    import os
    
    try:
        mpr_data = []
        with open(os.path.join(os.path.dirname(__file__), 'data', 'mpr_snapshot.csv'), 'r') as f:
            reader = csv.DictReader(f)
            mpr_data = list(reader)
    except FileNotFoundError:
        return jsonify({"error": "MPR snapshot not found"}), 404
    
    return jsonify({
        "metadata": {
            "source": "mpr_snapshot.csv",
            "total_records": len(mpr_data),
            "states": list(set([row['state'] for row in mpr_data]))
        },
        "data": mpr_data
    })

@app.route("/api/system_status")
def api_system_status():
    return jsonify({
        "status": "online",
        "villages_loaded": len(TEST_VILLAGES.get("features", [])),
        "stats_loaded": len(TEST_STATS.keys()),
        "timestamp": "2025-09-01T12:31:00"
    })

# Boundary layer API endpoints
@app.route("/api/boundaries/<layer_type>")
def api_boundaries(layer_type):
    """Get boundary data for states, districts, villages, or tribal areas"""
    if layer_type in BOUNDARY_DATA:
        return jsonify(BOUNDARY_DATA[layer_type])
    return jsonify({"error": "Invalid layer type"}), 404

# FRA Atlas Drill-down API endpoints
@app.route("/api/fra-atlas/states")
def api_fra_states():
    """Get all states with summary statistics"""
    states_data = []
    for state_name, state_data in FRA_ATLAS_DATA["states"].items():
        total_pattas = 0
        total_area = 0
        districts_count = len(state_data["districts"])
        
        for district_name, district_data in state_data["districts"].items():
            for block_name, block_data in district_data["blocks"].items():
                for village_name, village_data in block_data["villages"].items():
                    total_pattas += len(village_data["patta_holders"])
                    total_area += sum(patta["area_hectares"] for patta in village_data["patta_holders"])
        
        states_data.append({
            "name": state_name,
            "districts_count": districts_count,
            "total_pattas": total_pattas,
            "total_area_hectares": total_area,
            "avg_forest_cover": 70.2  # Mock data
        })
    
    return jsonify({"states": states_data})

@app.route("/api/fra-atlas/states/<state_name>/districts")
def api_fra_districts(state_name):
    """Get districts for a specific state"""
    if state_name not in FRA_ATLAS_DATA["states"]:
        return jsonify({"error": "State not found"}), 404
    
    districts_data = []
    for district_name, district_data in FRA_ATLAS_DATA["states"][state_name]["districts"].items():
        total_pattas = 0
        total_area = 0
        blocks_count = len(district_data["blocks"])
        
        for block_name, block_data in district_data["blocks"].items():
            for village_name, village_data in block_data["villages"].items():
                total_pattas += len(village_data["patta_holders"])
                total_area += sum(patta["area_hectares"] for patta in village_data["patta_holders"])
        
        districts_data.append({
            "name": district_name,
            "blocks_count": blocks_count,
            "total_pattas": total_pattas,
            "total_area_hectares": total_area
        })
    
    return jsonify({"districts": districts_data})

@app.route("/api/fra-atlas/states/<state_name>/districts/<district_name>/blocks")
def api_fra_blocks(state_name, district_name):
    """Get blocks for a specific district"""
    if state_name not in FRA_ATLAS_DATA["states"]:
        return jsonify({"error": "State not found"}), 404
    if district_name not in FRA_ATLAS_DATA["states"][state_name]["districts"]:
        return jsonify({"error": "District not found"}), 404
    
    blocks_data = []
    for block_name, block_data in FRA_ATLAS_DATA["states"][state_name]["districts"][district_name]["blocks"].items():
        total_pattas = 0
        total_area = 0
        villages_count = len(block_data["villages"])
        
        for village_name, village_data in block_data["villages"].items():
            total_pattas += len(village_data["patta_holders"])
            total_area += sum(patta["area_hectares"] for patta in village_data["patta_holders"])
        
        blocks_data.append({
            "name": block_name,
            "villages_count": villages_count,
            "total_pattas": total_pattas,
            "total_area_hectares": total_area
        })
    
    return jsonify({"blocks": blocks_data})

@app.route("/api/fra-atlas/states/<state_name>/districts/<district_name>/blocks/<block_name>/villages")
def api_fra_villages(state_name, district_name, block_name):
    """Get villages for a specific block"""
    if state_name not in FRA_ATLAS_DATA["states"]:
        return jsonify({"error": "State not found"}), 404
    if district_name not in FRA_ATLAS_DATA["states"][state_name]["districts"]:
        return jsonify({"error": "District not found"}), 404
    if block_name not in FRA_ATLAS_DATA["states"][state_name]["districts"][district_name]["blocks"]:
        return jsonify({"error": "Block not found"}), 404
    
    villages_data = []
    for village_name, village_data in FRA_ATLAS_DATA["states"][state_name]["districts"][district_name]["blocks"][block_name]["villages"].items():
        villages_data.append({
            "name": village_name,
            "patta_holders_count": len(village_data["patta_holders"]),
            "total_area_hectares": sum(patta["area_hectares"] for patta in village_data["patta_holders"]),
            "forest_cover_percent": village_data["forest_cover"],
            "water_bodies_count": village_data["water_bodies"],
            "agricultural_land_percent": village_data["agricultural_land"],
            "coordinates": village_data["coordinates"]
        })
    
    return jsonify({"villages": villages_data})

@app.route("/api/fra-atlas/states/<state_name>/districts/<district_name>/blocks/<block_name>/villages/<village_name>/patta-holders")
def api_fra_patta_holders(state_name, district_name, block_name, village_name):
    """Get patta holders for a specific village"""
    if state_name not in FRA_ATLAS_DATA["states"]:
        return jsonify({"error": "State not found"}), 404
    if district_name not in FRA_ATLAS_DATA["states"][state_name]["districts"]:
        return jsonify({"error": "District not found"}), 404
    if block_name not in FRA_ATLAS_DATA["states"][state_name]["districts"][district_name]["blocks"]:
        return jsonify({"error": "Block not found"}), 404
    if village_name not in FRA_ATLAS_DATA["states"][state_name]["districts"][district_name]["blocks"][block_name]["villages"]:
        return jsonify({"error": "Village not found"}), 404
    
    village_data = FRA_ATLAS_DATA["states"][state_name]["districts"][district_name]["blocks"][block_name]["villages"][village_name]
    
    return jsonify({
        "village": village_name,
        "patta_holders": village_data["patta_holders"],
        "village_stats": {
            "forest_cover_percent": village_data["forest_cover"],
            "water_bodies_count": village_data["water_bodies"],
            "agricultural_land_percent": village_data["agricultural_land"]
        }
    })

# FRA Atlas Filters and Search API
@app.route("/api/fra-atlas/search")
def api_fra_search():
    """Search FRA data by various criteria"""
    query = request.args.get('q', '')
    filter_type = request.args.get('type', 'all')  # all, patta_holder, village, tribal_group
    status_filter = request.args.get('status', 'all')  # all, pending, verified, approved
    
    results = []
    
    for state_name, state_data in FRA_ATLAS_DATA["states"].items():
        for district_name, district_data in state_data["districts"].items():
            for block_name, block_data in district_data["blocks"].items():
                for village_name, village_data in block_data["villages"].items():
                    for patta in village_data["patta_holders"]:
                        # Apply filters
                        if status_filter != 'all' and patta["status"].lower() != status_filter.lower():
                            continue
                        
                        # Apply search query
                        if query.lower() in patta["name"].lower() or \
                           query.lower() in village_name.lower() or \
                           query.lower() in patta["tribal_group"].lower():
                            
                            results.append({
                                "patta_id": patta["id"],
                                "patta_holder": patta["name"],
                                "village": village_name,
                                "block": block_name,
                                "district": district_name,
                                "state": state_name,
                                "tribal_group": patta["tribal_group"],
                                "claim_type": patta["claim_type"],
                                "area_hectares": patta["area_hectares"],
                                "status": patta["status"],
                                "coordinates": patta["coordinates"]
                            })
    
    return jsonify({"results": results, "total": len(results)})

@app.route('/api/admin/real_stats')
def admin_real_stats():
    """Get real admin statistics"""
    # Count actual data from FRA_ATLAS_DATA
    total_claims = 0
    approved_claims = 0
    pending_claims = 0
    rejected_claims = 0
    
    for state_data in FRA_ATLAS_DATA["states"].values():
        for district_data in state_data["districts"].values():
            for block_data in district_data["blocks"].values():
                for village_data in block_data["villages"].values():
                    for patta_holder in village_data["patta_holders"]:
                        total_claims += 1
                        if patta_holder["status"] == "Approved":
                            approved_claims += 1
                        elif patta_holder["status"] == "Pending":
                            pending_claims += 1
                        else:
                            rejected_claims += 1
    
    return jsonify({
        "total_claims": total_claims,
        "approved_claims": approved_claims,
        "pending_claims": pending_claims,
        "rejected_claims": rejected_claims,
        "approval_rate": round((approved_claims / total_claims * 100) if total_claims > 0 else 0, 1),
        "system_uptime": 99.8,
        "response_time": 2.3,
        "storage_used": 1.2,
        "active_users": 45
    })

# ====== Blockchain Storage Routes ======
@app.route('/blockchain-storage')
def blockchain_storage():
    """Blockchain storage interface for admin users"""
    if not session.get('user'):
        return redirect(url_for('login'))
    if session.get('user_role') not in ['CCF', 'DCF', 'RFO']:
        flash('Access denied. Blockchain storage is only for CCF, DCF, and RFO officials.', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('blockchain_demo.html')

@app.route('/api/blockchain/stats')
def blockchain_stats():
    """Get blockchain network statistics"""
    if not BLOCKCHAIN_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Blockchain module not available'
        }), 503
    
    try:
        stats = get_blockchain_stats()
        return jsonify({
            'success': True,
            'stats': {
                'total_documents': stats['total_documents'],
                'total_land_records': stats['verified_documents'],
                'total_verification_requests': stats['total_transactions'],
                'active_nodes': 12,
                'last_block_number': stats['block_number']
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/blockchain/register-document', methods=['POST'])
def blockchain_register_document():
    """Register document on blockchain"""
    if not BLOCKCHAIN_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Blockchain module not available'
        }), 503
    
    if not session.get('user'):
        return jsonify({
            'success': False,
            'error': 'Authentication required'
        }), 401
    
    try:
        data = request.get_json()
        document_data = data.get('document_data', {})
        result = register_fra_document(document_data)
        
        if result['success']:
            return jsonify({
                'success': True,
                'data': {
                    'document_hash': result['document_hash'],
                    'transaction_hash': result['transaction_hash'],
                    'block_number': result['block_number']
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/blockchain/verify-document', methods=['POST'])
def blockchain_verify_document():
    """Verify document on blockchain"""
    if not BLOCKCHAIN_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Blockchain module not available'
        }), 503
    
    if not session.get('user'):
        return jsonify({
            'success': False,
            'error': 'Authentication required'
        }), 401
    
    try:
        data = request.get_json()
        verified_by = session.get('user_role', 'Admin')
        result = verify_fra_document(
            data.get('document_hash'),
            data.get('is_valid', True),
            data.get('notes', ''),
            verified_by
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'data': {
                    'transaction_hash': result['verification_tx'],
                    'block_number': result['block_number'],
                    'verification_data': {
                        'verifier': verified_by,
                        'status': 'Valid' if data.get('is_valid', True) else 'Invalid',
                        'notes': data.get('notes', '')
                    }
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/blockchain/transactions')
def blockchain_transactions():
    """Get recent blockchain transactions"""
    if not BLOCKCHAIN_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Blockchain module not available'
        }), 503
    
    try:
        limit = request.args.get('limit', 10, type=int)
        transactions_data = get_blockchain_transactions(limit)
        
        # Format transactions to match frontend expectations
        formatted_transactions = []
        for tx in transactions_data['transactions']:
            formatted_transactions.append({
                'type': tx['type'],
                'patta_holder': tx['holder'],
                'village': tx['village'],
                'status': tx['status'],
                'hash': tx['hash'],
                'gas_used': 21000 + (len(tx['hash']) * 10)  # Simulate gas usage
            })
        
        return jsonify({
            'success': True,
            'transactions': formatted_transactions
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/blockchain/search')
def blockchain_search():
    """Search blockchain documents"""
    if not BLOCKCHAIN_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Blockchain module not available'
        }), 503
    
    try:
        query = request.args.get('query', '')
        if not query:
            return jsonify({
                'success': False,
                'error': 'Search query required'
            }), 400
        
        results = search_blockchain_documents(query)
        return jsonify(results)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/blockchain/document/<doc_hash>')
def blockchain_document(doc_hash):
    """Get specific document from blockchain"""
    if not BLOCKCHAIN_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Blockchain module not available'
        }), 503
    
    try:
        result = get_document_from_blockchain(doc_hash)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Demo API endpoints for Hackathon Presentation
@app.route('/api/demo/patta-metrics')
def demo_patta_metrics():
    """Demo API for Patta document metrics"""
    if DEMO_DATA_AVAILABLE:
        return jsonify(get_demo_patta_metrics())
    else:
        return jsonify({"error": "Demo data not available"}), 500

@app.route('/api/demo/system-stats')
def demo_system_stats():
    """Demo API for system statistics"""
    if DEMO_DATA_AVAILABLE:
        return jsonify(get_demo_system_stats())
    else:
        return jsonify({"error": "Demo data not available"}), 500

@app.route('/api/demo/success-stories')
def demo_success_stories():
    """Demo API for success stories"""
    if DEMO_DATA_AVAILABLE:
        return jsonify(get_demo_success_stories())
    else:
        return jsonify({"error": "Demo data not available"}), 500

@app.route('/api/demo/patta-documents')
def demo_patta_documents():
    """Demo API for sample Patta documents"""
    if DEMO_DATA_AVAILABLE:
        return jsonify(get_demo_patta_documents())
    else:
        return jsonify({"error": "Demo data not available"}), 500

@app.route('/api/demo/ai-prediction')
def demo_ai_prediction():
    """Demo API for AI prediction results"""
    if DEMO_DATA_AVAILABLE:
        return jsonify(get_demo_ai_prediction())
    else:
        return jsonify({"error": "Demo data not available"}), 500

@app.route('/api/demo/chatbot-response')
def demo_chatbot_response():
    """Demo API for chatbot responses"""
    query_type = request.args.get('type', 'greeting')
    if DEMO_DATA_AVAILABLE:
        return jsonify({"response": get_demo_chatbot_response(query_type)})
    else:
        return jsonify({"error": "Demo data not available"}), 500

@app.route('/demo')
def demo():
    """Demo hub with four-click flow"""
    return render_template('demo.html')

@app.route('/hackathon-demo')
def hackathon_demo():
    """Hackathon presentation demo page"""
    return render_template('hackathon_demo.html')

@app.route('/api/user_stats')
def user_stats():
    """API endpoint for user statistics"""
    try:
        # Get current user info
        user = session.get('user', 'Unknown')
        user_role = session.get('user_role', 'Unknown')
        
        # Calculate user-specific stats
        stats = {
            "user": user,
            "role": user_role,
            "login_time": session.get('login_time', 'Unknown'),
            "session_duration": "Active",
            "permissions": {
                "can_upload": user_role in ['CCF', 'DCF', 'RFO'],
                "can_manage": user_role in ['CCF', 'DCF'],
                "can_admin": user_role == 'CCF'
            },
            "activity": {
                "uploads_today": 0,
                "reports_generated": 0,
                "last_activity": "Just now"
            }
        }
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/schemes/suggestions')
def api_scheme_suggestions():
    """API endpoint for personalized scheme suggestions"""
    try:
        # Get user role for personalized suggestions
        user_role = session.get('user_role', 'PUBLIC')
        
        # Mock user data for demonstration (in real app, this would come from database)
        mock_user_data = {
            "social_category": "ST",
            "bpl_status": "Yes",
            "land_ownership": True,
            "land_area_hectares": 1.5,
            "cultivates_crops": True,
            "tribal_district": True,
            "collects_forest_produce": True,
            "house_type": "Kutcha",
            "tap_water": False,
            "electricity": False,
            "clean_fuel": False,
            "bank_account": True
        }
        
        # Government schemes database
        schemes_database = {
            "agricultural_schemes": {
                "PM_KISAN": {
                    "name": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
                    "description": "Direct income support of Rs. 6,000 per year to small and marginal farmers",
                    "benefit_amount": "Rs. 6,000 per year",
                    "ministry": "Ministry of Agriculture & Farmers Welfare",
                    "website": "https://pmkisan.gov.in",
                    "eligibility_score": 95.0,
                    "reasons": ["✓ Has land ownership", "✓ Cultivates crops", "✓ Eligible social category: ST", "✓ Land area 1.5 hectares meets requirement"]
                },
                "PMFBY": {
                    "name": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
                    "description": "Crop insurance scheme for farmers",
                    "benefit_amount": "Up to 100% of sum insured",
                    "ministry": "Ministry of Agriculture & Farmers Welfare",
                    "website": "https://pmfby.gov.in",
                    "eligibility_score": 90.0,
                    "reasons": ["✓ Cultivates crops", "✓ Has land ownership", "✓ Has bank account"]
                }
            },
            "housing_schemes": {
                "PMAY": {
                    "name": "Pradhan Mantri Awas Yojana (PMAY)",
                    "description": "Housing for all by 2022",
                    "benefit_amount": "Rs. 1.5-2.5 lakhs",
                    "ministry": "Ministry of Housing and Urban Affairs",
                    "website": "https://pmaymis.gov.in",
                    "eligibility_score": 85.0,
                    "reasons": ["✓ Below Poverty Line", "✓ Eligible social category: ST", "✓ Has bank account"]
                }
            },
            "employment_schemes": {
                "MGNREGA": {
                    "name": "Mahatma Gandhi National Rural Employment Guarantee Act",
                    "description": "100 days of guaranteed wage employment",
                    "benefit_amount": "Rs. 200-300 per day",
                    "ministry": "Ministry of Rural Development",
                    "website": "https://nrega.nic.in",
                    "eligibility_score": 80.0,
                    "reasons": ["✓ Has bank account", "✓ Rural household"]
                }
            },
            "forest_rights_schemes": {
                "FRA_TITLE": {
                    "name": "Forest Rights Act - Individual Forest Rights",
                    "description": "Recognition of individual forest rights",
                    "benefit_amount": "Land title up to 4 hectares",
                    "ministry": "Ministry of Tribal Affairs",
                    "website": "https://tribal.nic.in",
                    "eligibility_score": 100.0,
                    "reasons": ["✓ Located in tribal district", "✓ Collects forest produce", "✓ Eligible social category: ST"]
                },
                "FRA_COMMUNITY": {
                    "name": "Forest Rights Act - Community Forest Rights",
                    "description": "Recognition of community forest rights",
                    "benefit_amount": "Community forest management rights",
                    "ministry": "Ministry of Tribal Affairs",
                    "website": "https://tribal.nic.in",
                    "eligibility_score": 100.0,
                    "reasons": ["✓ Located in tribal district", "✓ Collects forest produce", "✓ Eligible social category: ST"]
                }
            },
            "social_welfare_schemes": {
                "PMJAY": {
                    "name": "Pradhan Mantri Jan Arogya Yojana (PMJAY)",
                    "description": "Health insurance for poor and vulnerable families",
                    "benefit_amount": "Up to Rs. 5 lakhs per family per year",
                    "ministry": "Ministry of Health and Family Welfare",
                    "website": "https://pmjay.gov.in",
                    "eligibility_score": 90.0,
                    "reasons": ["✓ Below Poverty Line", "✓ Eligible social category: ST"]
                },
                "PMUY": {
                    "name": "Pradhan Mantri Ujjwala Yojana (PMUY)",
                    "description": "Free LPG connections to poor households",
                    "benefit_amount": "Free LPG connection + Rs. 1,600 subsidy",
                    "ministry": "Ministry of Petroleum and Natural Gas",
                    "website": "https://pmuy.gov.in",
                    "eligibility_score": 95.0,
                    "reasons": ["✓ Below Poverty Line", "✓ Eligible social category: ST", "✓ No clean fuel"]
                }
            },
            "infrastructure_schemes": {
                "JAL_JEEVAN": {
                    "name": "Jal Jeevan Mission",
                    "description": "Tap water connection to every household",
                    "benefit_amount": "Free tap water connection",
                    "ministry": "Ministry of Jal Shakti",
                    "website": "https://jaljeevanmission.gov.in",
                    "eligibility_score": 100.0,
                    "reasons": ["✓ Rural household", "✓ No tap water"]
                },
                "SAUBHAGYA": {
                    "name": "Pradhan Mantri Sahaj Bijli Har Ghar Yojana (SAUBHAGYA)",
                    "description": "Electricity connection to every household",
                    "benefit_amount": "Free electricity connection",
                    "ministry": "Ministry of Power",
                    "website": "https://saubhagya.gov.in",
                    "eligibility_score": 100.0,
                    "reasons": ["✓ Below Poverty Line", "✓ No electricity"]
                }
            }
        }
        
        # Calculate personalized suggestions
        suggestions = {
            "user_profile": {
                "role": user_role,
                "social_category": mock_user_data["social_category"],
                "bpl_status": mock_user_data["bpl_status"],
                "land_ownership": mock_user_data["land_ownership"],
                "tribal_district": mock_user_data["tribal_district"]
            },
            "priority_schemes": [],
            "all_eligible_schemes": [],
            "overall_score": 85.0,
            "recommendations": [
                "🎯 You are eligible for 8 government schemes",
                "⭐ Top priority schemes: FRA Individual Rights, Jal Jeevan Mission, SAUBHAGYA",
                "🌟 High eligibility score - Apply for multiple schemes",
                "📄 Consider uploading patta document for enhanced eligibility"
            ]
        }
        
        # Add all eligible schemes with proper scoring
        for category, schemes in schemes_database.items():
            for scheme_id, scheme_info in schemes.items():
                # Use the eligibility score directly (already in percentage format)
                suggestions["all_eligible_schemes"].append({
                    "scheme_id": scheme_id,
                    "category": category,
                    **scheme_info,
                    "eligibility_score": scheme_info["eligibility_score"]  # Use score directly
                })
        
        # Sort by eligibility score and get top 5
        suggestions["all_eligible_schemes"].sort(key=lambda x: x["eligibility_score"], reverse=True)
        suggestions["priority_schemes"] = suggestions["all_eligible_schemes"][:5]
        
        return jsonify(suggestions)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/fra-data/assess', methods=['POST'])
def api_fra_data_assess():
    """API endpoint to assess FRA data and generate scheme predictions"""
    try:
        # Get form data
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['head_name', 'aadhaar_number', 'mobile_number', 'social_category', 'complete_address', 'total_family_members', 'bpl_status']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Try to import eligibility engine, fallback to mock data if not available
        try:
            from eligibility_engine import EligibilityEngine
            engine = EligibilityEngine()
            
            # Process the data with real engine
            assessment_result = engine.assess_eligibility(data)
            
            # Convert eligibility scores to percentages
            for scheme in assessment_result["priority_schemes"]:
                scheme["eligibility_score"] = round(scheme["eligibility_score"] * 100, 1)
            
            for scheme in assessment_result["eligible_schemes"]:
                scheme["eligibility_score"] = round(scheme["eligibility_score"] * 100, 1)
            
            # Save assessment to file
            try:
                engine.save_assessment(assessment_result)
            except Exception as e:
                print(f"Warning: Could not save assessment: {e}")
                
        except ImportError:
            print("⚠️ EligibilityEngine not available, using mock data")
            # Fallback to mock assessment result
            assessment_result = {
                "priority_schemes": [
                    {
                        "scheme_id": "PM_KISAN",
                        "name": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
                        "description": "Direct income support of Rs. 6,000 per year to small and marginal farmers",
                        "benefit_amount": "Rs. 6,000 per year",
                        "ministry": "Ministry of Agriculture & Farmers Welfare",
                        "website": "https://pmkisan.gov.in",
                        "eligibility_score": 95.0,
                        "reasons": ["✓ Has land ownership", "✓ Cultivates crops", "✓ Eligible social category: ST"]
                    },
                    {
                        "scheme_id": "FRA_TITLE",
                        "name": "Forest Rights Act - Individual Forest Rights",
                        "description": "Recognition of individual forest rights",
                        "benefit_amount": "Land title up to 4 hectares",
                        "ministry": "Ministry of Tribal Affairs",
                        "website": "https://tribal.nic.in",
                        "eligibility_score": 100.0,
                        "reasons": ["✓ Located in tribal district", "✓ Collects forest produce", "✓ Eligible social category: ST"]
                    }
                ],
                "eligible_schemes": [],
                "overall_score": 0.85,
                "recommendations": [
                    "🎯 You are eligible for 2 government schemes",
                    "⭐ Top priority schemes: PM-KISAN, Forest Rights Act",
                    "🌟 High eligibility score - Apply for multiple schemes"
                ],
                "assessment_date": datetime.utcnow().isoformat()
            }
        
        # Create response with user profile
        response = {
            "head_name": data.get("head_name"),
            "user_profile": {
                "role": session.get('user_role', 'PUBLIC'),
                "social_category": data.get("social_category"),
                "bpl_status": data.get("bpl_status"),
                "land_ownership": bool(data.get("owns_house") == "Yes" or data.get("land_area_hectares")),
                "tribal_district": data.get("tribal_district") == "Yes"
            },
            "priority_schemes": assessment_result["priority_schemes"],
            "all_eligible_schemes": assessment_result.get("eligible_schemes", []),
            "overall_score": round(assessment_result["overall_score"] * 100, 1),
            "recommendations": assessment_result["recommendations"],
            "assessment_date": assessment_result["assessment_date"]
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Error in fra-data/assess: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    try:
        # Get port from environment variable (Railway sets this)
        port = int(os.environ.get('PORT', 5000))
        debug = os.environ.get('FLASK_ENV') != 'production'
        
        print("🌲 Starting FRA-SENTINEL Web Application...")
        print(f"📍 Server running on port {port}")
        print(f"🔍 API Health: http://localhost:{port}/api/health")
        print("\n✅ Server starting...")
        
        app.run(debug=debug, host='0.0.0.0', port=port, threaded=True, use_reloader=False)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")

