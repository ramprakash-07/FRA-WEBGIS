"""
Enhanced WebGIS Application for FRA-SENTINEL
Complete Flask application with all features integrated
"""

import os
import json
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from flask_cors import CORS
from werkzeug.utils import secure_filename
import sqlite3
from typing import Dict, List, Optional

# Import custom modules
from database import init_database, get_db, db_manager
from queue import init_message_queue, enqueue_ocr_job, enqueue_batch_job, get_queue_stats
from tiles import tile_bp, generate_tiles_for_layer
from models import init_model_registry, get_current_models, list_available_models
from dss.enhanced_dss_engine import analyze_village_dss, get_convergence_analysis
from digitization.enhanced_ocr import process_document, batch_process_documents
from asset_mapping.train_classify import load_or_create_satellite_image, classify_entire_image

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure Flask application"""
    
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'jpg', 'jpeg', 'png', 'tiff', 'bmp'}
    
    # Enable CORS
    CORS(app)
    
    # Initialize components
    init_database()
    init_message_queue()
    init_model_registry()
    
    # Register blueprints
    app.register_blueprint(tile_bp)
    
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    return app

app = create_app()

# Utility functions
def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def get_db_connection():
    """Get database connection"""
    return sqlite3.connect('fra_atlas.db')

# Routes
@app.route('/')
def index():
    """Main dashboard"""
    return render_template('dashboard.html')

@app.route('/atlas')
def atlas():
    """FRA Atlas WebGIS"""
    return render_template('atlas.html')

@app.route('/admin')
def admin():
    """Admin panel"""
    return render_template('admin_panel.html')

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'components': {
            'database': db_manager.test_connection(),
            'message_queue': True,
            'model_registry': True
        }
    })

@app.route('/api/villages')
def get_villages():
    """Get all villages"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT v.id, v.name, v.code, b.name as block_name, 
                   d.name as district_name, s.name as state_name,
                   v.population, v.tribal_population_pct, v.forest_cover_pct,
                   v.water_bodies_count, v.agricultural_land_pct
            FROM villages v
            JOIN blocks b ON v.block_id = b.id
            JOIN districts d ON b.district_id = d.id
            JOIN states s ON d.state_id = s.id
            ORDER BY v.name
        """)
        
        villages = []
        for row in cursor.fetchall():
            villages.append({
                'id': row[0],
                'name': row[1],
                'code': row[2],
                'block_name': row[3],
                'district_name': row[4],
                'state_name': row[5],
                'population': row[6],
                'tribal_population_pct': row[7],
                'forest_cover_pct': row[8],
                'water_bodies_count': row[9],
                'agricultural_land_pct': row[10]
            })
        
        conn.close()
        return jsonify(villages)
        
    except Exception as e:
        logger.error(f"Error fetching villages: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/patta-holders')
def get_patta_holders():
    """Get patta holders with filters"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get query parameters
        village_id = request.args.get('village_id')
        claim_type = request.args.get('claim_type')
        status = request.args.get('status')
        limit = request.args.get('limit', 100)
        offset = request.args.get('offset', 0)
        
        # Build query
        query = """
            SELECT p.id, p.file_id, p.holder_name, p.father_husband_name,
                   p.tribal_group, p.claim_type, p.status, p.area_claimed,
                   p.area_vested, v.name as village_name, p.uploaded_at
            FROM patta_holders p
            JOIN villages v ON p.village_id = v.id
            WHERE 1=1
        """
        
        params = []
        
        if village_id:
            query += " AND p.village_id = ?"
            params.append(village_id)
        
        if claim_type:
            query += " AND p.claim_type = ?"
            params.append(claim_type)
        
        if status:
            query += " AND p.status = ?"
            params.append(status)
        
        query += " ORDER BY p.uploaded_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        
        patta_holders = []
        for row in cursor.fetchall():
            patta_holders.append({
                'id': row[0],
                'file_id': row[1],
                'holder_name': row[2],
                'father_husband_name': row[3],
                'tribal_group': row[4],
                'claim_type': row[5],
                'status': row[6],
                'area_claimed': row[7],
                'area_vested': row[8],
                'village_name': row[9],
                'uploaded_at': row[10]
            })
        
        conn.close()
        return jsonify(patta_holders)
        
    except Exception as e:
        logger.error(f"Error fetching patta holders: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/progress')
def get_progress():
    """Get progress data"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get progress by quarter
        cursor.execute("""
            SELECT quarter, year,
                   SUM(ifr_filed) as total_ifr_filed,
                   SUM(ifr_granted) as total_ifr_granted,
                   SUM(cr_filed) as total_cr_filed,
                   SUM(cr_granted) as total_cr_granted,
                   SUM(cfr_filed) as total_cfr_filed,
                   SUM(cfr_granted) as total_cfr_granted,
                   SUM(total_area_vested) as total_area_vested
            FROM progress_tracking
            GROUP BY quarter, year
            ORDER BY year DESC, quarter DESC
        """)
        
        progress_data = []
        for row in cursor.fetchall():
            progress_data.append({
                'quarter': row[0],
                'year': row[1],
                'ifr_filed': row[2],
                'ifr_granted': row[3],
                'cr_filed': row[4],
                'cr_granted': row[5],
                'cfr_filed': row[6],
                'cfr_granted': row[7],
                'total_area_vested': row[8]
            })
        
        conn.close()
        return jsonify(progress_data)
        
    except Exception as e:
        logger.error(f"Error fetching progress: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dss/analyze', methods=['POST'])
def analyze_village():
    """Analyze village using DSS"""
    try:
        data = request.get_json()
        village_id = data.get('village_id')
        village_data = data.get('village_data')
        
        if not village_id or not village_data:
            return jsonify({'error': 'village_id and village_data are required'}), 400
        
        result = analyze_village_dss(village_id, village_data)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"DSS analysis error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dss/convergence', methods=['POST'])
def analyze_convergence():
    """Analyze convergence across villages"""
    try:
        data = request.get_json()
        villages_data = data.get('villages_data', [])
        
        if not villages_data:
            return jsonify({'error': 'villages_data is required'}), 400
        
        result = get_convergence_analysis(villages_data)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Convergence analysis error: {e}")
        return jsonify({'error': str(e)}), 500

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
            filename = secure_filename(file.filename)
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
                'processing_time': result['processing_time']
            })
        
        return jsonify({'error': 'Invalid file type'}), 400
        
    except Exception as e:
        logger.error(f"File upload error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/batch-upload', methods=['POST'])
def batch_upload():
    """Upload multiple files for batch processing"""
    try:
        files = request.files.getlist('files')
        
        if not files:
            return jsonify({'error': 'No files provided'}), 400
        
        filepaths = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                filepaths.append(filepath)
        
        if not filepaths:
            return jsonify({'error': 'No valid files uploaded'}), 400
        
        # Process files in batch
        results = batch_process_documents(filepaths)
        
        return jsonify({
            'total_files': len(filepaths),
            'successful': len([r for r in results if r['success']]),
            'failed': len([r for r in results if not r['success']]),
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Batch upload error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/asset-mapping/<int:village_id>')
def get_asset_mapping(village_id):
    """Get asset mapping for a village"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT village_id, model_version, classification_date,
                   farmland_pct, forest_pct, water_pct, homestead_pct,
                   confidence_score, total_pixels
            FROM asset_mapping
            WHERE village_id = ?
            ORDER BY classification_date DESC
            LIMIT 1
        """, (village_id,))
        
        row = cursor.fetchone()
        if row:
            result = {
                'village_id': row[0],
                'model_version': row[1],
                'classification_date': row[2],
                'farmland_pct': row[3],
                'forest_pct': row[4],
                'water_pct': row[5],
                'homestead_pct': row[6],
                'confidence_score': row[7],
                'total_pixels': row[8]
            }
        else:
            result = None
        
        conn.close()
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Asset mapping error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/models')
def get_models():
    """Get available ML models"""
    try:
        models = list_available_models()
        current_models = get_current_models()
        
        return jsonify({
            'available_models': models,
            'current_models': current_models
        })
        
    except Exception as e:
        logger.error(f"Models API error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/queue/stats')
def get_queue_stats_api():
    """Get message queue statistics"""
    try:
        stats = get_queue_stats()
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Queue stats error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-tiles', methods=['POST'])
def generate_tiles():
    """Generate map tiles for a layer"""
    try:
        data = request.get_json()
        layer = data.get('layer')
        min_zoom = data.get('min_zoom', 1)
        max_zoom = data.get('max_zoom', 10)
        
        if not layer:
            return jsonify({'error': 'layer is required'}), 400
        
        count = generate_tiles_for_layer(layer, min_zoom, max_zoom)
        
        return jsonify({
            'layer': layer,
            'tiles_generated': count,
            'min_zoom': min_zoom,
            'max_zoom': max_zoom
        })
        
    except Exception as e:
        logger.error(f"Tile generation error: {e}")
        return jsonify({'error': str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# CLI commands
@app.cli.command()
def init_db():
    """Initialize database"""
    init_database()
    print("Database initialized successfully!")

@app.cli.command()
def seed_data():
    """Seed database with sample data"""
    from demo_data import seed_database
    seed_database()
    print("Sample data seeded successfully!")

@app.cli.command()
def run_tests():
    """Run test suite"""
    import subprocess
    result = subprocess.run(['python', '-m', 'pytest', 'tests/', '-v'], 
                          capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)









