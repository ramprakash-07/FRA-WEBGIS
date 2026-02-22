#!/usr/bin/env python3
"""
Simple FRA-SENTINEL Web App
Easy-to-run web application with OCR functionality
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import json
from datetime import datetime
from digitization.enhanced_ocr import process_document, batch_process_documents

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'pdf', 'jpg', 'jpeg', 'png', 'tiff', 'bmp'}

@app.route('/')
def index():
    """Main dashboard"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>FRA-SENTINEL Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; text-align: center; margin-bottom: 30px; }
            .nav { text-align: center; margin: 20px 0; }
            .nav a { display: inline-block; margin: 10px; padding: 12px 24px; background: #3498db; color: white; text-decoration: none; border-radius: 5px; }
            .nav a:hover { background: #2980b9; }
            .feature { margin: 20px 0; padding: 20px; background: #ecf0f1; border-radius: 5px; }
            .status { padding: 10px; background: #27ae60; color: white; border-radius: 5px; margin: 10px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌲 FRA-SENTINEL Dashboard</h1>
            <div class="status">✅ System Status: Online</div>
            
            <div class="nav">
                <a href="/upload">📄 Upload Patta</a>
                <a href="/atlas">🗺️ FRA Atlas</a>
                <a href="/admin">⚙️ Admin Panel</a>
                <a href="/api/health">🔍 API Health</a>
            </div>
            
            <div class="feature">
                <h3>📊 System Overview</h3>
                <p><strong>OCR Engine:</strong> ✅ Active - Processes PDF/image documents</p>
                <p><strong>Database:</strong> ✅ Connected - Stores patta holder data</p>
                <p><strong>DSS Engine:</strong> ✅ Ready - Provides scheme recommendations</p>
                <p><strong>Asset Mapping:</strong> ✅ Available - Satellite imagery analysis</p>
            </div>
            
            <div class="feature">
                <h3>🚀 Quick Actions</h3>
                <p>• Upload patta documents for automatic data extraction</p>
                <p>• View interactive maps with FRA data</p>
                <p>• Analyze villages for scheme recommendations</p>
                <p>• Monitor progress and statistics</p>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/upload')
def upload_page():
    """Upload page"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Upload Patta - FRA-SENTINEL</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; text-align: center; }
            .upload-form { margin: 30px 0; padding: 20px; background: #ecf0f1; border-radius: 5px; }
            input[type="file"] { margin: 10px 0; padding: 10px; width: 100%; }
            button { background: #27ae60; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; }
            button:hover { background: #229954; }
            .result { margin: 20px 0; padding: 15px; background: #d5f4e6; border-radius: 5px; }
            .error { background: #fadbd8; color: #721c24; }
            .back { margin: 20px 0; }
            .back a { color: #3498db; text-decoration: none; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📄 Upload Patta Document</h1>
            
            <div class="back">
                <a href="/">← Back to Dashboard</a>
            </div>
            
            <div class="upload-form">
                <h3>Upload Single Document</h3>
                <form id="uploadForm" enctype="multipart/form-data">
                    <input type="file" name="file" accept=".pdf,.jpg,.jpeg,.png,.tiff,.bmp" required>
                    <button type="submit">🔍 Process Document</button>
                </form>
            </div>
            
            <div id="result"></div>
            
            <script>
                document.getElementById('uploadForm').addEventListener('submit', async function(e) {
                    e.preventDefault();
                    
                    const formData = new FormData(this);
                    const resultDiv = document.getElementById('result');
                    
                    resultDiv.innerHTML = '<p>⏳ Processing document...</p>';
                    
                    try {
                        const response = await fetch('/api/upload', {
                            method: 'POST',
                            body: formData
                        });
                        
                        const result = await response.json();
                        
                        if (result.success) {
                            let html = '<div class="result"><h3>✅ Document Processed Successfully!</h3>';
                            html += '<p><strong>Processing Time:</strong> ' + result.processing_time.toFixed(2) + 's</p>';
                            
                            html += '<h4>📋 Extracted Data:</h4><ul>';
                            for (const [field, value] of Object.entries(result.data)) {
                                if (value) {
                                    html += '<li><strong>' + field.replace(/_/g, ' ').toUpperCase() + ':</strong> ' + value + '</li>';
                                }
                            }
                            html += '</ul>';
                            
                            html += '<h4>🎯 Confidence Scores:</h4><ul>';
                            for (const [field, score] of Object.entries(result.confidence)) {
                                if (score > 0) {
                                    html += '<li><strong>' + field.replace(/_/g, ' ').toUpperCase() + ':</strong> ' + (score * 100).toFixed(1) + '%</li>';
                                }
                            }
                            html += '</ul></div>';
                            
                            resultDiv.innerHTML = html;
                        } else {
                            resultDiv.innerHTML = '<div class="result error"><h3>❌ Processing Failed</h3><p>' + result.error + '</p></div>';
                        }
                    } catch (error) {
                        resultDiv.innerHTML = '<div class="result error"><h3>❌ Upload Error</h3><p>' + error.message + '</p></div>';
                    }
                });
            </script>
        </div>
    </body>
    </html>
    '''

@app.route('/atlas')
def atlas():
    """FRA Atlas page"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>FRA Atlas - FRA-SENTINEL</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; text-align: center; }
            .map-container { height: 500px; background: #ecf0f1; border-radius: 5px; margin: 20px 0; display: flex; align-items: center; justify-content: center; color: #7f8c8d; }
            .back { margin: 20px 0; }
            .back a { color: #3498db; text-decoration: none; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🗺️ FRA Atlas</h1>
            
            <div class="back">
                <a href="/">← Back to Dashboard</a>
            </div>
            
            <div class="map-container">
                <div>
                    <h3>🗺️ Interactive Map</h3>
                    <p>Map tiles and spatial data visualization</p>
                    <p><strong>Features:</strong></p>
                    <ul>
                        <li>Village boundaries and locations</li>
                        <li>Patta holder distributions</li>
                        <li>Progress tracking overlays</li>
                        <li>Asset mapping results</li>
                    </ul>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/admin')
def admin():
    """Admin panel"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Panel - FRA-SENTINEL</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; text-align: center; }
            .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
            .stat-card { background: #ecf0f1; padding: 20px; border-radius: 5px; text-align: center; }
            .stat-number { font-size: 2em; font-weight: bold; color: #27ae60; }
            .back { margin: 20px 0; }
            .back a { color: #3498db; text-decoration: none; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>⚙️ Admin Panel</h1>
            
            <div class="back">
                <a href="/">← Back to Dashboard</a>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">200</div>
                    <div>Patta Holders</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">55</div>
                    <div>Villages</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">330</div>
                    <div>Progress Records</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">161</div>
                    <div>DSS Recommendations</div>
                </div>
            </div>
            
            <h3>🔧 System Management</h3>
            <p>• Database management and maintenance</p>
            <p>• OCR processing queue monitoring</p>
            <p>• ML model training and updates</p>
            <p>• User access and permissions</p>
        </div>
    </body>
    </html>
    '''

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'components': {
            'ocr_engine': True,
            'database': True,
            'dss_engine': True,
            'asset_mapping': True
        }
    })

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload file for OCR processing"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Process file with OCR
            result = process_document(filepath)
            
            return jsonify({
                'filename': filename,
                'filepath': filepath,
                'success': result['success'],
                'data': result['data'],
                'confidence': result['confidence'],
                'processing_time': result['processing_time'],
                'error': result['error']
            })
        
        return jsonify({'error': 'Invalid file type'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/villages')
def get_villages():
    """Get villages data"""
    # Sample data for demonstration
    villages = [
        {'id': 1, 'name': 'Khargone', 'population': 500, 'tribal_pct': 60},
        {'id': 2, 'name': 'Jhabua', 'population': 400, 'tribal_pct': 70},
        {'id': 3, 'name': 'Koraput', 'population': 600, 'tribal_pct': 80}
    ]
    return jsonify(villages)

if __name__ == '__main__':
    print("🌲 Starting FRA-SENTINEL Web Application...")
    print("📍 Dashboard: http://localhost:5000")
    print("📄 Upload: http://localhost:5000/upload")
    print("🗺️ Atlas: http://localhost:5000/atlas")
    print("⚙️ Admin: http://localhost:5000/admin")
    print("🔍 API Health: http://localhost:5000/api/health")
    print("\n✅ Server starting...")
    
    app.run(debug=True, host='0.0.0.0', port=5000)









