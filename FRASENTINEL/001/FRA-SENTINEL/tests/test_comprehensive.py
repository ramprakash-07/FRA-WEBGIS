"""
Comprehensive Test Suite for FRA-SENTINEL
End-to-end testing for all components
"""

import os
import sys
import json
import unittest
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
import numpy as np
from datetime import datetime
import sqlite3

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class TestDatabaseManager(unittest.TestCase):
    """Test database functionality"""
    
    def setUp(self):
        self.test_db_path = tempfile.mktemp(suffix='.db')
        self.db_manager = None
    
    def tearDown(self):
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
    
    def test_database_connection(self):
        """Test database connection"""
        from webgis.database import DatabaseManager
        
        db_manager = DatabaseManager(f"sqlite:///{self.test_db_path}")
        self.assertTrue(db_manager.connect())
        self.assertTrue(db_manager.test_connection())
    
    def test_spatial_operations(self):
        """Test spatial operations"""
        from webgis.database import create_point, create_polygon
        
        # Test point creation
        point = create_point(75.5, 21.5)
        self.assertIsNotNone(point)
        
        # Test polygon creation
        coords = [(75.0, 21.0), (76.0, 21.0), (76.0, 22.0), (75.0, 22.0), (75.0, 21.0)]
        polygon = create_polygon(coords)
        self.assertIsNotNone(polygon)

class TestOCREngine(unittest.TestCase):
    """Test OCR functionality"""
    
    def setUp(self):
        self.ocr_engine = None
    
    def test_extraction_patterns(self):
        """Test regex patterns for data extraction"""
        from digitization.enhanced_ocr import EnhancedOCREngine
        
        ocr_engine = EnhancedOCREngine()
        
        # Test village name extraction
        test_text = "Village: Khargone District"
        village_patterns = ocr_engine.extraction_patterns['village_name']
        
        found = False
        for pattern in village_patterns:
            import re
            match = re.search(pattern, test_text, re.IGNORECASE)
            if match:
                found = True
                break
        
        self.assertTrue(found)
    
    def test_file_validation(self):
        """Test file format validation"""
        from digitization.enhanced_ocr import EnhancedOCREngine
        
        ocr_engine = EnhancedOCREngine()
        
        # Test supported formats
        self.assertIn('.pdf', ocr_engine.supported_formats)
        self.assertIn('.jpg', ocr_engine.supported_formats)
        self.assertIn('.png', ocr_engine.supported_formats)
        
        # Test unsupported format
        self.assertNotIn('.txt', ocr_engine.supported_formats)
    
    @patch('digitization.enhanced_ocr.pytesseract')
    def test_image_preprocessing(self, mock_tesseract):
        """Test image preprocessing"""
        from digitization.enhanced_ocr import EnhancedOCREngine
        import cv2
        
        ocr_engine = EnhancedOCREngine()
        
        # Create test image
        test_image = np.ones((100, 100, 3), dtype=np.uint8) * 255
        
        # Test preprocessing
        processed = ocr_engine._preprocess_image(test_image)
        
        self.assertIsNotNone(processed)
        self.assertEqual(len(processed.shape), 2)  # Should be grayscale

class TestDSSEngine(unittest.TestCase):
    """Test DSS functionality"""
    
    def setUp(self):
        self.dss_engine = None
    
    def test_scheme_loading(self):
        """Test scheme loading"""
        from dss.enhanced_dss_engine import MLDSSEngine
        
        dss_engine = MLDSSEngine()
        
        # Test schemes are loaded
        self.assertGreater(len(dss_engine.schemes), 0)
        
        # Test specific schemes
        scheme_names = [scheme.name for scheme in dss_engine.schemes]
        self.assertIn('PM-KISAN', scheme_names)
        self.assertIn('Jal Jeevan Mission', scheme_names)
        self.assertIn('MGNREGA', scheme_names)
        self.assertIn('DAJGUA', scheme_names)
    
    def test_village_analysis(self):
        """Test village analysis"""
        from dss.enhanced_dss_engine import VillageProfile, MLDSSEngine
        
        dss_engine = MLDSSEngine()
        
        # Create test village profile
        village_profile = VillageProfile(
            village_id=1,
            name="Test Village",
            population=500,
            tribal_population_pct=60,
            forest_cover_pct=45,
            water_bodies_count=1,
            agricultural_land_pct=55,
            fra_status="granted",
            existing_schemes=[],
            literacy_rate=65.0,
            poverty_rate=30.0,
            connectivity_score=0.3,
            infrastructure_score=0.4
        )
        
        # Test analysis
        result = dss_engine.analyze_village(village_profile)
        
        self.assertIsInstance(result, dict)
        self.assertIn('village_id', result)
        self.assertIn('recommendations', result)
        self.assertIn('total_schemes', result)
        self.assertIn('ml_confidence', result)
    
    def test_ml_model_training(self):
        """Test ML model training"""
        from dss.enhanced_dss_engine import MLDSSEngine
        
        dss_engine = MLDSSEngine()
        
        # Test that models are initialized
        self.assertGreater(len(dss_engine.ml_models), 0)
        self.assertGreater(len(dss_engine.scalers), 0)
        
        # Test specific models exist
        self.assertIn('PM-KISAN', dss_engine.ml_models)
        self.assertIn('Jal Jeevan Mission', dss_engine.ml_models)

class TestAssetMapping(unittest.TestCase):
    """Test asset mapping functionality"""
    
    def setUp(self):
        self.test_data = None
    
    def test_image_classification(self):
        """Test image classification"""
        from asset_mapping.train_classify import classify_entire_image, load_or_create_satellite_image
        
        # Test image loading
        img = load_or_create_satellite_image()
        self.assertIsNotNone(img)
        self.assertEqual(len(img.shape), 3)  # Should be 3D (bands, height, width)
        
        # Test classification
        from sklearn.ensemble import RandomForestClassifier
        import numpy as np
        
        # Create dummy classifier
        classifier = RandomForestClassifier(n_estimators=10, random_state=42)
        
        # Create dummy training data
        n_bands, height, width = img.shape
        X_dummy = np.random.rand(100, n_bands)
        y_dummy = np.random.randint(0, 4, 100)
        classifier.fit(X_dummy, y_dummy)
        
        # Test classification
        classified_img = classify_entire_image(img, classifier)
        
        self.assertIsNotNone(classified_img)
        self.assertEqual(len(classified_img.shape), 2)  # Should be 2D
    
    def test_statistics_calculation(self):
        """Test statistics calculation"""
        from asset_mapping.train_classify import calculate_statistics
        
        # Create test classified image
        test_img = np.array([[0, 1, 2, 3], [0, 1, 2, 3], [0, 1, 2, 3]])
        
        stats = calculate_statistics(test_img)
        
        self.assertIsInstance(stats, dict)
        self.assertIn('farmland', stats)
        self.assertIn('forest', stats)
        self.assertIn('water', stats)
        self.assertIn('homestead', stats)

class TestMessageQueue(unittest.TestCase):
    """Test message queue functionality"""
    
    def setUp(self):
        self.message_queue = None
    
    def test_job_creation(self):
        """Test job creation"""
        from webgis.queue import MessageQueue, Job, JobStatus
        
        queue = MessageQueue()
        
        # Test job creation
        job_id = queue.enqueue('test_job', {'data': 'test'}, priority=1)
        
        self.assertIsNotNone(job_id)
        self.assertIn(job_id, queue.jobs)
        
        job = queue.jobs[job_id]
        self.assertEqual(job.status, JobStatus.PENDING)
        self.assertEqual(job.priority, 1)
    
    def test_job_processing(self):
        """Test job processing"""
        from webgis.queue import MessageQueue
        
        queue = MessageQueue()
        
        # Register test handler
        def test_handler(data):
            return {'result': 'success', 'data': data}
        
        queue.register_handler('test_job', test_handler)
        
        # Enqueue job
        job_id = queue.enqueue('test_job', {'test': 'data'})
        
        # Process job
        job = queue.dequeue()
        self.assertIsNotNone(job)
        self.assertEqual(job.id, job_id)
        
        # Complete job
        queue.complete_job(job_id, {'result': 'success'})
        
        job = queue.get_job(job_id)
        self.assertEqual(job.status.value, 'completed')
    
    def test_queue_statistics(self):
        """Test queue statistics"""
        from webgis.queue import get_queue_stats
        
        stats = get_queue_stats()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('total_jobs', stats)
        self.assertIn('pending', stats)
        self.assertIn('processing', stats)
        self.assertIn('completed', stats)
        self.assertIn('failed', stats)

class TestTileServer(unittest.TestCase):
    """Test tile server functionality"""
    
    def setUp(self):
        self.tile_renderer = None
    
    def test_tile_coordinates(self):
        """Test tile coordinate conversion"""
        from webgis.tiles import deg2num, num2deg
        
        # Test coordinate conversion
        lat, lon = 21.5, 75.5
        x, y = deg2num(lat, lon, 10)
        
        self.assertIsInstance(x, int)
        self.assertIsInstance(y, int)
        
        # Test reverse conversion
        lat_back, lon_back = num2deg(x, y, 10)
        
        self.assertAlmostEqual(lat, lat_back, places=1)
        self.assertAlmostEqual(lon, lon_back, places=1)
    
    def test_tile_rendering(self):
        """Test tile rendering"""
        from webgis.tiles import TileRenderer
        
        renderer = TileRenderer()
        
        # Test tile creation
        tile = renderer.render_patta_holders_tile(10, 500, 300, 'ifr')
        
        self.assertIsNotNone(tile)
        self.assertEqual(tile.size, (256, 256))  # Standard tile size
    
    def test_color_schemes(self):
        """Test color schemes"""
        from webgis.tiles import TileRenderer
        
        renderer = TileRenderer()
        
        # Test color definitions
        self.assertIn('ifr', renderer.colors)
        self.assertIn('cr', renderer.colors)
        self.assertIn('cfr', renderer.colors)
        self.assertIn('village', renderer.colors)
        
        # Test color format (RGBA)
        for color in renderer.colors.values():
            self.assertEqual(len(color), 4)  # RGBA

class TestModelRegistry(unittest.TestCase):
    """Test model registry functionality"""
    
    def setUp(self):
        self.test_registry_path = tempfile.mkdtemp()
        self.model_registry = None
    
    def tearDown(self):
        if os.path.exists(self.test_registry_path):
            shutil.rmtree(self.test_registry_path)
    
    def test_model_registration(self):
        """Test model registration"""
        from webgis.models import ModelRegistry, ModelType, ModelStatus
        from sklearn.ensemble import RandomForestClassifier
        import numpy as np
        
        registry = ModelRegistry(self.test_registry_path)
        
        # Create test model
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        training_data = np.random.rand(100, 5)
        labels = np.random.randint(0, 3, 100)
        model.fit(training_data, labels)
        
        # Register model
        model_id = registry.register_model(
            name="test_model",
            model_type=ModelType.ASSET_MAPPING,
            model=model,
            training_data=training_data,
            metrics={'accuracy': 0.85},
            hyperparameters={'n_estimators': 10},
            description="Test model"
        )
        
        self.assertIsNotNone(model_id)
        self.assertIn(model_id, registry.models)
    
    def test_model_loading(self):
        """Test model loading"""
        from webgis.models import ModelRegistry, ModelType
        from sklearn.ensemble import RandomForestClassifier
        import numpy as np
        
        registry = ModelRegistry(self.test_registry_path)
        
        # Create and register test model
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        training_data = np.random.rand(100, 5)
        labels = np.random.randint(0, 3, 100)
        model.fit(training_data, labels)
        
        model_id = registry.register_model(
            name="test_model",
            model_type=ModelType.ASSET_MAPPING,
            model=model,
            training_data=training_data,
            metrics={'accuracy': 0.85},
            hyperparameters={'n_estimators': 10}
        )
        
        # Load model
        loaded_model = registry.get_model(model_id)
        
        self.assertIsNotNone(loaded_model)
        self.assertIsInstance(loaded_model, RandomForestClassifier)
    
    def test_model_listing(self):
        """Test model listing"""
        from webgis.models import ModelRegistry, ModelType
        from sklearn.ensemble import RandomForestClassifier
        import numpy as np
        
        registry = ModelRegistry(self.test_registry_path)
        
        # Register multiple models
        for i in range(3):
            model = RandomForestClassifier(n_estimators=10, random_state=42)
            training_data = np.random.rand(100, 5)
            labels = np.random.randint(0, 3, 100)
            model.fit(training_data, labels)
            
            registry.register_model(
                name=f"test_model_{i}",
                model_type=ModelType.ASSET_MAPPING,
                model=model,
                training_data=training_data,
                metrics={'accuracy': 0.85},
                hyperparameters={'n_estimators': 10}
            )
        
        # Test listing
        models = registry.list_models()
        self.assertEqual(len(models), 3)
        
        # Test filtering by type
        asset_models = registry.list_models(model_type=ModelType.ASSET_MAPPING)
        self.assertEqual(len(asset_models), 3)

class TestWebGISIntegration(unittest.TestCase):
    """Test WebGIS integration"""
    
    def setUp(self):
        self.app = None
    
    def test_app_creation(self):
        """Test Flask app creation"""
        from webgis.app import create_app
        
        app = create_app()
        
        self.assertIsNotNone(app)
        self.assertEqual(app.name, 'webgis')
    
    def test_api_endpoints(self):
        """Test API endpoints"""
        from webgis.app import create_app
        
        app = create_app()
        
        with app.test_client() as client:
            # Test health endpoint
            response = client.get('/api/health')
            self.assertEqual(response.status_code, 200)
            
            # Test villages endpoint
            response = client.get('/api/villages')
            self.assertEqual(response.status_code, 200)
            
            # Test patta holders endpoint
            response = client.get('/api/patta-holders')
            self.assertEqual(response.status_code, 200)

class TestEndToEnd(unittest.TestCase):
    """End-to-end integration tests"""
    
    def setUp(self):
        self.test_data_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        if os.path.exists(self.test_data_dir):
            shutil.rmtree(self.test_data_dir)
    
    def test_complete_workflow(self):
        """Test complete FRA workflow"""
        
        # 1. Test OCR processing
        from digitization.enhanced_ocr import EnhancedOCREngine
        
        ocr_engine = EnhancedOCREngine()
        
        # Create test document content
        test_text = """
        Village: Khargone
        Name: Ram Singh
        Father: Suresh Singh
        Claim Type: IFR
        Area: 2.5 hectares
        Survey No: 123/45
        """
        
        # Test entity extraction
        extracted_data = ocr_engine._extract_entities(test_text)
        
        self.assertIsNotNone(extracted_data.get('village_name'))
        self.assertIsNotNone(extracted_data.get('holder_name'))
        self.assertIsNotNone(extracted_data.get('claim_type'))
        
        # 2. Test DSS analysis
        from dss.enhanced_dss_engine import analyze_village_dss
        
        village_data = {
            'name': 'Khargone',
            'population': 500,
            'tribal_population_pct': 60,
            'forest_cover_pct': 45,
            'water_bodies_count': 1,
            'agricultural_land_pct': 55,
            'fra_status': 'granted',
            'existing_schemes': []
        }
        
        dss_result = analyze_village_dss(1, village_data)
        
        self.assertIsInstance(dss_result, dict)
        self.assertIn('recommendations', dss_result)
        
        # 3. Test asset mapping
        from asset_mapping.train_classify import load_or_create_satellite_image
        
        img = load_or_create_satellite_image()
        self.assertIsNotNone(img)
        
        # 4. Test convergence analysis
        from dss.enhanced_dss_engine import get_convergence_analysis
        
        villages_data = [village_data] * 5  # Multiple villages
        
        convergence_result = get_convergence_analysis(villages_data)
        
        self.assertIsInstance(convergence_result, dict)
        self.assertIn('total_villages', convergence_result)
        self.assertIn('scheme_distribution', convergence_result)

def run_all_tests():
    """Run all tests"""
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [
        TestDatabaseManager,
        TestOCREngine,
        TestDSSEngine,
        TestAssetMapping,
        TestMessageQueue,
        TestTileServer,
        TestModelRegistry,
        TestWebGISIntegration,
        TestEndToEnd
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result

if __name__ == "__main__":
    print("Running FRA-SENTINEL Test Suite...")
    print("=" * 50)
    
    result = run_all_tests()
    
    print("\n" + "=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)









