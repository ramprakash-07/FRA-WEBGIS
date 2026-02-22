from flask import Flask, render_template, request, jsonify, session
import json
import os
from datetime import datetime
import hashlib
import sys

# Add patta_verification to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'patta_verification'))

try:
    from verification_api import verification_bp
    VERIFICATION_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Patta verification system not available: {e}")
    VERIFICATION_AVAILABLE = False

app = Flask(__name__)
app.secret_key = 'fra-sentinel-secret-key'

# Register verification blueprint if available
if VERIFICATION_AVAILABLE:
    app.register_blueprint(verification_bp)

# Create directories if they don't exist
os.makedirs('webgis/static/uploads', exist_ok=True)
os.makedirs('data/processed', exist_ok=True)

# Real FRA data from your research
FRA_DATA = {
    'Madhya Pradesh': {'claims': 58432, 'approved': 45678, 'rate': 78.2},
    'Odisha': {'claims': 52341, 'approved': 41256, 'rate': 78.8},
    'Telangana': {'claims': 34567, 'approved': 28934, 'rate': 83.7},
    'Tripura': {'claims': 23456, 'approved': 19876, 'rate': 84.7}
}

# Real government schemes 2025
SCHEMES = {
    'PM_KISAN': {'name': 'PM Kisan Samman Nidhi', 'budget': '60,000 crore', 'benefit': 'Rs. 6,000 annual'},
    'MGNREGA': {'name': 'MGNREGA', 'budget': '73,000 crore', 'benefit': '100 days employment'},
    'VAN_DHAN': {'name': 'Van Dhan Vikas', 'budget': '3,000 crore', 'benefit': 'Forest produce value addition'}
}

@app.route('/')
def dashboard():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>FRA SENTINEL - Enhanced</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <script src="https://cdn.plot.ly/plotly-2.26.0.min.js"></script>
        <style>
            body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
            .card { border-radius: 15px; box-shadow: 0 8px 30px rgba(0,0,0,0.12); margin: 15px 0; }
            .metric-card { background: linear-gradient(135deg, #2c5aa0, #28a745); color: white; }
            .upload-zone { border: 2px dashed #007bff; border-radius: 15px; padding: 40px; text-align: center; cursor: pointer; }
        </style>
    </head>
    <body>
        <nav class="navbar navbar-dark bg-primary">
            <div class="container-fluid">
                <span class="navbar-brand"><i class="fas fa-tree"></i> FRA SENTINEL - Enhanced</span>
                <select id="languageSelect" class="form-select" style="width: auto;">
                    <option value="en">English</option>
                    <option value="hi">हिंदी</option>
                    <option value="te">తెలుగు</option>
                    <option value="or">ଓଡ଼ିଆ</option>
                    <option value="bn">বাংলা</option>
                </select>
            </div>
        </nav>

        <div class="container-fluid mt-4">
            <!-- Metrics Row -->
            <div class="row">
                <div class="col-md-3">
                    <div class="card metric-card text-center">
                        <div class="card-body">
                            <h3><i class="fas fa-file-alt"></i></h3>
                            <h4>168,796</h4>
                            <p>Total Claims</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card metric-card text-center">
                        <div class="card-body">
                            <h3><i class="fas fa-check-circle"></i></h3>
                            <h4>80.4%</h4>
                            <p>Approval Rate</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card metric-card text-center">
                        <div class="card-body">
                            <h3><i class="fas fa-coins"></i></h3>
                            <h4>6</h4>
                            <p>Active Schemes</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card metric-card text-center">
                        <div class="card-body">
                            <h3><i class="fas fa-database"></i></h3>
                            <h4 id="processedCount">0</h4>
                            <p>Processed Docs</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Main Content -->
            <div class="row">
                <div class="col-lg-6">
                    <div class="card">
                        <div class="card-header bg-primary text-white">
                            <h5><i class="fas fa-cloud-upload-alt"></i> Document Upload</h5>
                        </div>
                        <div class="card-body">
                            <div class="upload-zone" onclick="document.getElementById('fileInput').click()">
                                <i class="fas fa-cloud-upload-alt fa-3x text-primary mb-3"></i>
                                <h5>Upload Patta Document</h5>
                                <p>PDF, PNG, JPG formats supported</p>
                                <input type="file" id="fileInput" style="display: none;" accept=".pdf,.png,.jpg,.jpeg">
                            </div>
                            
                            <!-- Verification Options -->
                            <div class="mt-3" id="verificationOptions" style="display: none;">
                                <div class="row">
                                    <div class="col-md-6">
                                        <label class="form-label">Verification Type:</label>
                                        <select class="form-select" id="verificationType">
                                            <option value="full">Full Verification</option>
                                            <option value="basic">Basic Verification</option>
                                            <option value="quick">Quick Verification</option>
                                        </select>
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label">State:</label>
                                        <select class="form-select" id="stateSelect">
                                            <option value="Tamil Nadu">Tamil Nadu</option>
                                            <option value="Andhra Pradesh">Andhra Pradesh</option>
                                            <option value="Telangana">Telangana</option>
                                            <option value="Karnataka">Karnataka</option>
                                        </select>
                                    </div>
                                </div>
                                <button class="btn btn-primary w-100 mt-3" onclick="uploadAndVerify()">
                                    <i class="fas fa-shield-alt"></i> Upload & Verify Document
                                </button>
                            </div>
                            
                            <div id="uploadResult" class="mt-3" style="display: none;"></div>
                        </div>
                    </div>
                </div>
                
                <div class="col-lg-6">
                    <div class="card">
                        <div class="card-header bg-success text-white">
                            <h5><i class="fas fa-robot"></i> DSS Recommendations</h5>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <label>Forest Cover %:</label>
                                <input type="range" id="forestCover" min="0" max="100" value="40" class="form-range">
                                <span id="forestValue">40%</span>
                            </div>
                            <div class="mb-3">
                                <label>Agricultural Land %:</label>
                                <input type="range" id="agriLand" min="0" max="100" value="35" class="form-range">
                                <span id="agriValue">35%</span>
                            </div>
                            <div class="mb-3">
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="tribalArea">
                                    <label class="form-check-label">Tribal Population Area</label>
                                </div>
                            </div>
                            <button class="btn btn-success w-100" onclick="getRecommendations()">
                                <i class="fas fa-search"></i> Get Scheme Recommendations
                            </button>
                            <div id="recommendations" class="mt-3"></div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Charts Row -->
            <div class="row mt-4">
                <div class="col-lg-6">
                    <div class="card">
                        <div class="card-header">
                            <h5><i class="fas fa-chart-bar"></i> FRA Implementation Statistics</h5>
                        </div>
                        <div class="card-body">
                            <div id="fraChart" style="height: 400px;"></div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-6">
                    <div class="card">
                        <div class="card-header">
                            <h5><i class="fas fa-money-bill-wave"></i> Government Schemes Budget 2025</h5>
                        </div>
                        <div class="card-body">
                            <div id="schemesChart" style="height: 400px;"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // Initialize
            document.addEventListener('DOMContentLoaded', function() {
                loadCharts();
                setupEventListeners();
                updateProcessedCount();
            });

            function setupEventListeners() {
                document.getElementById('fileInput').addEventListener('change', handleFileUpload);
                document.getElementById('forestCover').addEventListener('input', function() {
                    document.getElementById('forestValue').textContent = this.value + '%';
                });
                document.getElementById('agriLand').addEventListener('input', function() {
                    document.getElementById('agriValue').textContent = this.value + '%';
                });
            }

            function handleFileUpload(event) {
                const file = event.target.files[0];
                if (!file) return;

                // Show verification options
                document.getElementById('verificationOptions').style.display = 'block';
            }

            function uploadAndVerify() {
                const file = document.getElementById('fileInput').files[0];
                if (!file) {
                    alert('Please select a file first');
                    return;
                }

                const formData = new FormData();
                formData.append('file', file);
                formData.append('verification_type', document.getElementById('verificationType').value);
                formData.append('state', document.getElementById('stateSelect').value);

                // Show loading state
                document.getElementById('uploadResult').innerHTML = `
                    <div class="alert alert-info">
                        <i class="fas fa-spinner fa-spin"></i> Processing and verifying document...
                    </div>
                `;
                document.getElementById('uploadResult').style.display = 'block';

                fetch('/api/upload_document', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        let resultHtml = `
                            <div class="alert alert-success">
                                <h6>✅ Document Processed Successfully!</h6>
                                <p><strong>Hash:</strong> ${data.document_hash.substring(0, 16)}...</p>
                                <p><strong>Status:</strong> <span class="badge bg-success">${data.status}</span></p>
                        `;

                        if (data.verification_available && data.verification_results) {
                            const verification = data.verification_results;
                            const decision = verification.final_decision;
                            
                            let statusClass = 'secondary';
                            let statusIcon = '⏳';
                            
                            if (decision.status === 'ACCEPTED') {
                                statusClass = 'success';
                                statusIcon = '✅';
                            } else if (decision.status === 'REJECTED') {
                                statusClass = 'danger';
                                statusIcon = '❌';
                            } else if (decision.status === 'FLAGGED_FOR_REVIEW') {
                                statusClass = 'warning';
                                statusIcon = '⚠️';
                            }

                            resultHtml += `
                                <hr>
                                <h6>🔍 Verification Results:</h6>
                                <p><strong>Decision:</strong> <span class="badge bg-${statusClass}">${statusIcon} ${decision.status}</span></p>
                                <p><strong>Confidence:</strong> ${decision.confidence}%</p>
                            `;

                            if (decision.reasoning && decision.reasoning.length > 0) {
                                resultHtml += '<p><strong>Reasoning:</strong></p><ul>';
                                decision.reasoning.forEach(reason => {
                                    resultHtml += `<li>${reason}</li>`;
                                });
                                resultHtml += '</ul>';
                            }

                            if (decision.recommendations && decision.recommendations.length > 0) {
                                resultHtml += '<p><strong>Recommendations:</strong></p><ul>';
                                decision.recommendations.forEach(rec => {
                                    resultHtml += `<li>${rec}</li>`;
                                });
                                resultHtml += '</ul>';
                            }

                            // Show extracted data
                            if (verification.ocr_extraction && verification.ocr_extraction.fields) {
                                const fields = verification.ocr_extraction.fields;
                                resultHtml += '<hr><h6>📄 Extracted Data:</h6>';
                                resultHtml += '<div class="row">';
                                
                                const importantFields = ['patta_number', 'survey_number', 'district', 'village', 'owner_name'];
                                importantFields.forEach(field => {
                                    if (fields[field] && fields[field] !== 'Not Found') {
                                        const label = field.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
                                        resultHtml += `
                                            <div class="col-md-6 mb-2">
                                                <strong>${label}:</strong> ${fields[field]}
                                            </div>
                                        `;
                                    }
                                });
                                resultHtml += '</div>';
                            }
                        } else if (!data.verification_available) {
                            resultHtml += '<hr><p class="text-muted"><i class="fas fa-info-circle"></i> Verification system not available</p>';
                        }

                        resultHtml += '</div>';
                        document.getElementById('uploadResult').innerHTML = resultHtml;
                        updateProcessedCount();
                    } else {
                        document.getElementById('uploadResult').innerHTML = `
                            <div class="alert alert-danger">❌ ${data.error}</div>
                        `;
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    document.getElementById('uploadResult').innerHTML = `
                        <div class="alert alert-danger">❌ Error processing document: ${error.message}</div>
                    `;
                });
            }

            function getRecommendations() {
                const data = {
                    village_data: {
                        forest_percent: parseInt(document.getElementById('forestCover').value),
                        farmland_percent: parseInt(document.getElementById('agriLand').value),
                        tribal_population: document.getElementById('tribalArea').checked
                    },
                    language: 'en'
                };

                fetch('/api/get_recommendations', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                })
                .then(response => response.json())
                .then(data => {
                    let html = '<h6>📋 Recommended Schemes:</h6>';
                    data.recommendations.forEach(rec => {
                        const color = rec.eligibility === 'High' ? 'success' : 
                                     rec.eligibility === 'Medium' ? 'warning' : 'info';
                        html += `
                            <div class="alert alert-${color} mb-2">
                                <strong>${rec.name}</strong><br>
                                <small>${rec.description}</small><br>
                                <span class="badge bg-primary">Budget: ${rec.budget}</span>
                            </div>
                        `;
                    });
                    document.getElementById('recommendations').innerHTML = html;
                });
            }

            function loadCharts() {
                // FRA Statistics Chart
                const states = ['Madhya Pradesh', 'Odisha', 'Telangana', 'Tripura'];
                const claims = [58432, 52341, 34567, 23456];
                const approved = [45678, 41256, 28934, 19876];
                const rates = [78.2, 78.8, 83.7, 84.7];

                const trace1 = {x: states, y: claims, name: 'Claims Received', type: 'bar', marker: {color: 'lightblue'}};
                const trace2 = {x: states, y: approved, name: 'Claims Approved', type: 'bar', marker: {color: 'darkblue'}};
                const trace3 = {x: states, y: rates, name: 'Approval Rate (%)', type: 'scatter', mode: 'lines+markers', yaxis: 'y2', line: {color: 'red', width: 3}};

                Plotly.newPlot('fraChart', [trace1, trace2, trace3], {
                    title: 'FRA Implementation by State',
                    yaxis: {title: 'Number of Claims'},
                    yaxis2: {title: 'Approval Rate (%)', overlaying: 'y', side: 'right'}
                });

                // Schemes Budget Chart
                const schemes = ['PMGKAY', 'MGNREGA', 'Jal Jeevan', 'PM-KISAN', 'PM DEVINE', 'Van Dhan'];
                const budgets = [200000, 73000, 70000, 60000, 6600, 3000];

                Plotly.newPlot('schemesChart', [{
                    x: schemes,
                    y: budgets,
                    type: 'bar',
                    marker: {color: ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57', '#ff9ff3']}
                }], {
                    title: 'Government Schemes Budget 2025 (₹ Crores)',
                    yaxis: {title: 'Budget (₹ Crores)'}
                });
            }

            function updateProcessedCount() {
                fetch('/api/system_health')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('processedCount').textContent = data.statistics.processed_documents;
                });
            }
        </script>
    </body>
    </html>
    '''

@app.route('/api/upload_document', methods=['POST'])
def upload_document():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Get verification type from form data
    verification_type = request.form.get('verification_type', 'full')
    state = request.form.get('state', 'Tamil Nadu')
    
    # Process the file
    file_content = file.read()
    doc_hash = hashlib.sha256(file_content).hexdigest()
    
    # Save file info
    doc_info = {
        'document_hash': doc_hash,
        'filename': file.filename,
        'upload_time': datetime.now().isoformat(),
        'status': 'Processed',
        'file_size': len(file_content),
        'verification_type': verification_type,
        'state': state
    }
    
    # Save to data folder
    with open(f'data/processed/{doc_hash}.json', 'w') as f:
        json.dump(doc_info, f, indent=2)
    
    # If verification system is available, perform verification
    verification_results = None
    if VERIFICATION_AVAILABLE:
        try:
            # Save file temporarily for verification
            temp_path = f'data/processed/{doc_hash}_{file.filename}'
            with open(temp_path, 'wb') as f:
                f.write(file_content)
            
            # Perform verification
            from patta_verifier import PattaVerifier
            verifier = PattaVerifier()
            verification_results = verifier.verify_patta_document(temp_path, state)
            
            # Update document info with verification results
            doc_info['verification_results'] = verification_results
            doc_info['verification_status'] = verification_results.get('final_decision', {}).get('status', 'PENDING')
            doc_info['verification_confidence'] = verification_results.get('final_decision', {}).get('confidence', 0)
            
            # Save updated info
            with open(f'data/processed/{doc_hash}.json', 'w') as f:
                json.dump(doc_info, f, indent=2)
            
            # Clean up temp file
            try:
                os.remove(temp_path)
            except:
                pass
                
        except Exception as e:
            print(f"Verification error: {e}")
            doc_info['verification_error'] = str(e)
    
    response_data = {
        'success': True,
        'document_hash': doc_hash,
        'status': 'Processed',
        'message': 'Document uploaded successfully',
        'verification_available': VERIFICATION_AVAILABLE
    }
    
    if verification_results:
        response_data['verification_results'] = verification_results
        response_data['verification_status'] = verification_results.get('final_decision', {}).get('status', 'PENDING')
        response_data['verification_confidence'] = verification_results.get('final_decision', {}).get('confidence', 0)
    
    return jsonify(response_data)

@app.route('/api/get_recommendations', methods=['POST'])
def get_recommendations():
    data = request.get_json()
    village_data = data.get('village_data', {})
    
    recommendations = []
    forest_percent = village_data.get('forest_percent', 0)
    farmland_percent = village_data.get('farmland_percent', 0)
    tribal_population = village_data.get('tribal_population', False)
    
    # Generate recommendations based on criteria
    if farmland_percent > 15:
        recommendations.append({
            'scheme': 'PM_KISAN',
            'name': SCHEMES['PM_KISAN']['name'],
            'description': SCHEMES['PM_KISAN']['benefit'],
            'budget': SCHEMES['PM_KISAN']['budget'],
            'eligibility': 'High' if farmland_percent > 30 else 'Medium'
        })
    
    if tribal_population and forest_percent > 20:
        recommendations.append({
            'scheme': 'VAN_DHAN',
            'name': SCHEMES['VAN_DHAN']['name'],
            'description': SCHEMES['VAN_DHAN']['benefit'],
            'budget': SCHEMES['VAN_DHAN']['budget'],
            'eligibility': 'High'
        })
    
    # Always include MGNREGA
    recommendations.append({
        'scheme': 'MGNREGA',
        'name': SCHEMES['MGNREGA']['name'],
        'description': SCHEMES['MGNREGA']['benefit'],
        'budget': SCHEMES['MGNREGA']['budget'],
        'eligibility': 'Eligible'
    })
    
    return jsonify({
        'success': True,
        'recommendations': recommendations,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/system_health')
def system_health():
    processed_files = len([f for f in os.listdir('data/processed') if f.endswith('.json')]) if os.path.exists('data/processed') else 0
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'statistics': {
            'processed_documents': processed_files
        }
    })

if __name__ == '__main__':
    print("🚀 Starting Enhanced FRA-SENTINEL")
    print("📁 Using your existing project structure")
    print("✅ Access at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
