# Demo Data for Hackathon Presentation
# Pre-loaded sample data for instant demonstration

DEMO_PATTA_DOCUMENTS = [
    {
        "id": "DEMO001",
        "filename": "tamil_nadu_patta_sample.pdf",
        "state": "Tamil Nadu",
        "district": "Chennai",
        "taluk": "Tambaram",
        "village": "Sample Village",
        "owner_name": "ராஜேஷ் குமார்",
        "patta_number": "RTR1482/15",
        "survey_number": "321778",
        "area_hectares": 1.08,
        "status": "Approved",
        "confidence": 95.2,
        "processing_time": 2.8,
        "extracted_fields": {
            "name": "ராஜேஷ் குமார்",
            "father_or_husband": "அண்ணாதுரை",
            "patta_no": "RTR1482/15",
            "survey_no": "321778",
            "area": "1.08 hectares",
            "village": "Sample Village",
            "taluk": "Tambaram",
            "district": "Chennai",
            "date": "01/02/2016"
        }
    },
    {
        "id": "DEMO002",
        "filename": "madhya_pradesh_patta_sample.pdf",
        "state": "Madhya Pradesh",
        "district": "Khargone",
        "taluk": "Khargone",
        "village": "Khargone",
        "owner_name": "Ram Singh",
        "patta_number": "FRA001",
        "survey_number": "678/1",
        "area_hectares": 2.5,
        "status": "Approved",
        "confidence": 92.1,
        "processing_time": 3.2,
        "extracted_fields": {
            "name": "Ram Singh",
            "father_or_husband": "Mohan Singh",
            "patta_no": "FRA001",
            "survey_no": "678/1",
            "area": "2.5 hectares",
            "village": "Khargone",
            "taluk": "Khargone",
            "district": "Khargone",
            "date": "15/03/2024"
        }
    },
    {
        "id": "DEMO003",
        "filename": "odisha_patta_sample.pdf",
        "state": "Odisha",
        "district": "Koraput",
        "taluk": "Koraput",
        "village": "Sample Village",
        "owner_name": "Sita Devi",
        "patta_number": "ODR456/22",
        "survey_number": "123/45",
        "area_hectares": 1.8,
        "status": "Pending Review",
        "confidence": 87.3,
        "processing_time": 2.9,
        "extracted_fields": {
            "name": "Sita Devi",
            "father_or_husband": "Ramesh Kumar",
            "patta_no": "ODR456/22",
            "survey_no": "123/45",
            "area": "1.8 hectares",
            "village": "Sample Village",
            "taluk": "Koraput",
            "district": "Koraput",
            "date": "20/01/2024"
        }
    }
]

DEMO_ANALYTICS_METRICS = {
    "totalPattaDocs": 47,
    "successfulExtractions": 43,
    "extractionAccuracy": 91.5,
    "avgProcessingTime": 3.2,
    "pendingReviews": 4,
    "totalAreaProcessed": 127.8,
    "successfulBar": 43,
    "pendingBar": 4,
    "failedBar": 0,
    "monthlyTrends": {
        "january": {"processed": 12, "approved": 11, "rejected": 1},
        "february": {"processed": 15, "approved": 14, "rejected": 1},
        "march": {"processed": 20, "approved": 18, "rejected": 2}
    }
}

DEMO_AI_PREDICTIONS = {
    "landUsePrediction": {
        "suitabilityScore": 87,
        "recommendedUse": "Forest Rights Allocation",
        "successProbability": 92,
        "environmentalImpact": "Low",
        "economicViability": 89,
        "processingTime": 18
    },
    "successCalculator": {
        "applicationType": "Individual Forest Rights",
        "documentationQuality": "Excellent",
        "communitySupport": "Strong",
        "successRate": 94
    }
}

DEMO_CHATBOT_RESPONSES = {
    "greeting": "Hello! I'm your FRA Sentinel AI Assistant. I can help you with forest rights applications, document requirements, and processing status. How can I assist you today?",
    "patta_info": "A Patta is a landholding document issued by the government. For FRA claims, you need to submit your Patta along with supporting documents like identity proof, residence certificate, and land survey details. The processing time is typically 30-45 days.",
    "application_process": "To apply for forest rights, visit your local Forest Rights Committee or Gram Sabha. You'll need: 1) Identity proof, 2) Residence certificate, 3) Land documents, 4) Community verification. The application goes through multiple verification stages.",
    "status_check": "You can check your application status by visiting the FRA portal or contacting your local Forest Rights Committee. You'll need your application reference number. Status updates are provided at each stage of processing."
}

DEMO_SYSTEM_STATS = {
    "total_claims": 168796,
    "approved_claims": 135637,
    "approval_rate": 80.4,
    "active_schemes": 6,
    "processed_documents": 47,
    "system_uptime": 99.9,
    "average_processing_time": 3.2,
    "cost_savings": 2500000,  # ₹2.5 lakhs per month
    "communities_served": 200000000,  # 200M+ people
    "annual_impact": 50000000000  # ₹50,000 crore
}

DEMO_SUCCESS_STORIES = [
    {
        "title": "Empowering Tribal Communities in Madhya Pradesh",
        "description": "FRA Sentinel processed 1,247 claims in Khargone district, reducing processing time from 6 months to 18 days with 94% accuracy.",
        "impact": "₹2.5 lakhs cost savings per month, 200+ families empowered",
        "location": "Khargone, Madhya Pradesh"
    },
    {
        "title": "Digital Transformation in Tamil Nadu",
        "description": "AI-powered Patta verification helped process 892 Tamil Nadu documents with 90.9% accuracy, eliminating manual errors.",
        "impact": "70% faster processing, 95% user satisfaction",
        "location": "Chennai, Tamil Nadu"
    },
    {
        "title": "Sustainable Forest Management in Odisha",
        "description": "DSS recommendations helped allocate ₹3 crores in Van Dhan Vikas scheme, benefiting 150+ forest communities.",
        "impact": "Enhanced forest conservation, improved livelihoods",
        "location": "Koraput, Odisha"
    }
]

# Demo API endpoints for instant data loading
def get_demo_patta_metrics():
    """Returns demo Patta document metrics for analytics"""
    return DEMO_ANALYTICS_METRICS

def get_demo_system_stats():
    """Returns demo system statistics"""
    return DEMO_SYSTEM_STATS

def get_demo_success_stories():
    """Returns demo success stories"""
    return DEMO_SUCCESS_STORIES

def get_demo_patta_documents():
    """Returns demo Patta documents"""
    return DEMO_PATTA_DOCUMENTS

def get_demo_ai_prediction():
    """Returns demo AI prediction results"""
    return DEMO_AI_PREDICTIONS

def get_demo_chatbot_response(query_type):
    """Returns demo chatbot response"""
    return DEMO_CHATBOT_RESPONSES.get(query_type, "I'm here to help with your FRA-related queries. Please ask me anything about forest rights, applications, or document requirements.")
