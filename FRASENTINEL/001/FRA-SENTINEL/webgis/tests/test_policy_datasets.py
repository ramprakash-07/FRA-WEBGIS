#!/usr/bin/env python3
"""
Test Policy Datasets
Tests for policy-aligned datasets and API endpoints
"""

import json
import os
import sys
import unittest
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

class TestPolicyDatasets(unittest.TestCase):
    """Test policy datasets and their structure"""
    
    def setUp(self):
        """Set up test environment"""
        self.data_dir = PROJECT_ROOT / "data"
        self.docs_dir = PROJECT_ROOT / "docs"
        
    def test_dss_catalog_exists(self):
        """Test that DSS catalog exists and has required structure"""
        catalog_path = self.data_dir / "dss_catalog.json"
        self.assertTrue(catalog_path.exists(), "DSS catalog file not found")
        
        with open(catalog_path, 'r') as f:
            catalog = json.load(f)
        
        # Check metadata
        self.assertIn('metadata', catalog)
        self.assertIn('schemes', catalog)
        self.assertIn('convergence_rules', catalog)
        
        # Check schemes structure
        schemes = catalog['schemes']
        self.assertGreater(len(schemes), 0, "No schemes found in catalog")
        
        # Check required scheme fields
        required_fields = [
            'scheme_key', 'display_name', 'ministry', 'category',
            'dajgua_priority', 'eligibility_fields', 'evidence_expected',
            'guideline_ref', 'monitoring_notes', 'convergence_tags'
        ]
        
        for scheme_key, scheme_info in schemes.items():
            for field in required_fields:
                self.assertIn(field, scheme_info, f"Missing field '{field}' in scheme '{scheme_key}'")
    
    def test_progress_schema_exists(self):
        """Test that progress schema exists and has required structure"""
        schema_path = self.data_dir / "progress_schema.json"
        self.assertTrue(schema_path.exists(), "Progress schema file not found")
        
        with open(schema_path, 'r') as f:
            schema = json.load(f)
        
        # Check metadata
        self.assertIn('metadata', schema)
        self.assertIn('schema', schema)
        self.assertIn('calculated_fields', schema)
        self.assertIn('aggregation_levels', schema)
        
        # Check required schema fields
        required_fields = [
            'state', 'district', 'block', 'village',
            'ifr_filed', 'ifr_granted', 'ifr_rejected',
            'cr_filed', 'cr_granted', 'cr_rejected',
            'cfr_filed', 'cfr_granted', 'cfr_rejected',
            'total_area_vested', 'cfr_managed_area'
        ]
        
        for field in required_fields:
            self.assertIn(field, schema['schema'], f"Missing field '{field}' in progress schema")
    
    def test_digitization_schema_exists(self):
        """Test that digitization schema exists and has required structure"""
        schema_path = self.docs_dir / "schema_digitization.json"
        self.assertTrue(schema_path.exists(), "Digitization schema file not found")
        
        with open(schema_path, 'r') as f:
            schema = json.load(f)
        
        # Check metadata
        self.assertIn('metadata', schema)
        self.assertIn('schema', schema)
        self.assertIn('validation_rules', schema)
        self.assertIn('export_formats', schema)
        
        # Check required schema fields
        required_fields = [
            'claim_type', 'claimant_category', 'evidence_types',
            'form_type', 'committee_stage', 'survey_no', 'coords',
            'area_claimed', 'area_vested', 'status', 'holder_details',
            'location_details', 'document_details', 'compliance_flags'
        ]
        
        for field in required_fields:
            self.assertIn(field, schema['schema'], f"Missing field '{field}' in digitization schema")
    
    def test_cfr_plan_template_exists(self):
        """Test that CFR plan template exists and has required structure"""
        template_path = self.data_dir / "cfr_plan_template.json"
        self.assertTrue(template_path.exists(), "CFR plan template file not found")
        
        with open(template_path, 'r') as f:
            template = json.load(f)
        
        # Check metadata
        self.assertIn('metadata', template)
        self.assertIn('template', template)
        self.assertIn('sample_data', template)
        
        # Check required template fields
        required_fields = [
            'district', 'block', 'gram_panchayat', 'village',
            'cfr_title_details', 'interventions_list', 'budget_heads',
            'monitoring_notes', 'implementation_timeline'
        ]
        
        for field in required_fields:
            self.assertIn(field, template['template'], f"Missing field '{field}' in CFR template")
    
    def test_mpr_snapshot_exists(self):
        """Test that MPR snapshot exists and has required structure"""
        snapshot_path = self.data_dir / "mpr_snapshot.csv"
        self.assertTrue(snapshot_path.exists(), "MPR snapshot file not found")
        
        # Check CSV structure
        import csv
        with open(snapshot_path, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        self.assertGreater(len(rows), 0, "No data found in MPR snapshot")
        
        # Check required columns
        required_columns = [
            'state', 'district', 'block', 'village',
            'ifr_filed', 'ifr_granted', 'ifr_rejected',
            'cr_filed', 'cr_granted', 'cr_rejected',
            'cfr_filed', 'cfr_granted', 'cfr_rejected',
            'total_area_vested', 'cfr_managed_area'
        ]
        
        for column in required_columns:
            self.assertIn(column, reader.fieldnames, f"Missing column '{column}' in MPR snapshot")
    
    def test_policy_segments_exists(self):
        """Test that policy segments exist and have required structure"""
        segments_path = self.docs_dir / "policy_segments.json"
        self.assertTrue(segments_path.exists(), "Policy segments file not found")
        
        with open(segments_path, 'r') as f:
            segments = json.load(f)
        
        # Check metadata
        self.assertIn('metadata', segments)
        self.assertIn('segments', segments)
        
        # Check segments structure
        self.assertGreater(len(segments['segments']), 0, "No policy segments found")
        
        # Check required segment fields
        required_fields = ['source', 'section', 'anchor', 'text', 'tags']
        
        for segment in segments['segments']:
            for field in required_fields:
                self.assertIn(field, segment, f"Missing field '{field}' in policy segment")
    
    def test_annexure_v_compliance(self):
        """Test that progress data complies with Annexure V format"""
        snapshot_path = self.data_dir / "mpr_snapshot.csv"
        schema_path = self.data_dir / "progress_schema.json"
        
        # Load schema
        with open(schema_path, 'r') as f:
            schema = json.load(f)
        
        # Load snapshot
        import csv
        with open(snapshot_path, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        # Check Annexure V compliance
        annexure_v_fields = schema['export_formats']['annexure_v_csv']['columns']
        
        for field in annexure_v_fields:
            self.assertIn(field, reader.fieldnames, f"Missing Annexure V field '{field}' in MPR snapshot")
    
    def test_dajgua_scheme_coverage(self):
        """Test that DSS catalog covers required DAJGUA schemes"""
        catalog_path = self.data_dir / "dss_catalog.json"
        
        with open(catalog_path, 'r') as f:
            catalog = json.load(f)
        
        # Required DAJGUA schemes
        required_schemes = [
            'pm_kisan', 'jjm', 'mgnrega', 'pmay_g',
            'rkvy', 'pmmsy', 'nlm', 'rgsa'
        ]
        
        for scheme in required_schemes:
            self.assertIn(scheme, catalog['schemes'], f"Missing required DAJGUA scheme '{scheme}'")
    
    def test_guideline_references(self):
        """Test that all schemes have guideline references"""
        catalog_path = self.data_dir / "dss_catalog.json"
        
        with open(catalog_path, 'r') as f:
            catalog = json.load(f)
        
        for scheme_key, scheme_info in catalog['schemes'].items():
            self.assertIn('guideline_ref', scheme_info, f"Missing guideline reference for scheme '{scheme_key}'")
            self.assertIsInstance(scheme_info['guideline_ref'], str, f"Guideline reference must be string for scheme '{scheme_key}'")
            self.assertGreater(len(scheme_info['guideline_ref']), 0, f"Empty guideline reference for scheme '{scheme_key}'")

if __name__ == '__main__':
    unittest.main()












