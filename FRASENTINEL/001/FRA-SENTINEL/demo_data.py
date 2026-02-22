"""
Sample Data and Database Seeds for FRA-SENTINEL
Comprehensive test data for all components
"""

import os
import json
import sqlite3
import random
from datetime import datetime, timedelta
from typing import List, Dict
import numpy as np

def seed_database():
    """Seed database with comprehensive sample data"""
    
    conn = sqlite3.connect('fra_atlas.db')
    cursor = conn.cursor()
    
    try:
        # Clear existing data
        cursor.execute("DELETE FROM patta_holders")
        cursor.execute("DELETE FROM progress_tracking")
        cursor.execute("DELETE FROM asset_mapping")
        cursor.execute("DELETE FROM dss_recommendations")
        cursor.execute("DELETE FROM villages")
        cursor.execute("DELETE FROM blocks")
        cursor.execute("DELETE FROM districts")
        cursor.execute("DELETE FROM states")
        
        # Insert states
        states_data = [
            ('Madhya Pradesh', 'MP'),
            ('Odisha', 'OR'),
            ('Tripura', 'TR'),
            ('Telangana', 'TS'),
            ('Jharkhand', 'JH'),
            ('Chhattisgarh', 'CG'),
            ('Maharashtra', 'MH'),
            ('Gujarat', 'GJ')
        ]
        
        for name, code in states_data:
            cursor.execute("INSERT INTO states (name, code) VALUES (?, ?)", (name, code))
        
        # Insert districts
        districts_data = [
            ('Khargone', 'KHG', 1),  # Madhya Pradesh
            ('Jhabua', 'JHA', 1),
            ('Dhar', 'DHA', 1),
            ('Koraput', 'KOR', 2),  # Odisha
            ('Rayagada', 'RAY', 2),
            ('West Tripura', 'WTR', 3),  # Tripura
            ('Adilabad', 'ADI', 4),  # Telangana
            ('Ranchi', 'RAN', 5),  # Jharkhand
            ('Bastar', 'BAS', 6),  # Chhattisgarh
            ('Nandurbar', 'NAN', 7),  # Maharashtra
            ('Dahod', 'DAH', 8)  # Gujarat
        ]
        
        for name, code, state_id in districts_data:
            cursor.execute("INSERT INTO districts (name, code, state_id) VALUES (?, ?, ?)", 
                         (name, code, state_id))
        
        # Insert blocks
        blocks_data = [
            ('Khargone Block', 'KHG01', 1),
            ('Kasrawad Block', 'KHG02', 1),
            ('Bhagwanpura Block', 'KHG03', 1),
            ('Jhabua Block', 'JHA01', 2),
            ('Petlawad Block', 'JHA02', 2),
            ('Dhar Block', 'DHA01', 3),
            ('Badnawar Block', 'DHA02', 3),
            ('Koraput Block', 'KOR01', 4),
            ('Rayagada Block', 'RAY01', 5),
            ('Agartala Block', 'WTR01', 6),
            ('Adilabad Block', 'ADI01', 7),
            ('Ranchi Block', 'RAN01', 8),
            ('Bastar Block', 'BAS01', 9),
            ('Nandurbar Block', 'NAN01', 10),
            ('Dahod Block', 'DAH01', 11)
        ]
        
        for name, code, district_id in blocks_data:
            cursor.execute("INSERT INTO blocks (name, code, district_id) VALUES (?, ?, ?)", 
                         (name, code, district_id))
        
        # Insert villages with realistic data
        villages_data = []
        village_names = [
            'Khargone', 'Kasrawad', 'Bhagwanpura', 'Jhabua', 'Petlawad',
            'Dhar', 'Badnawar', 'Koraput', 'Rayagada', 'Agartala',
            'Adilabad', 'Ranchi', 'Bastar', 'Nandurbar', 'Dahod',
            'Bhopal', 'Indore', 'Gwalior', 'Jabalpur', 'Ujjain',
            'Bhubaneswar', 'Cuttack', 'Rourkela', 'Sambalpur', 'Puri',
            'Agartala', 'Dharmanagar', 'Udaipur', 'Ambassa', 'Kailasahar',
            'Hyderabad', 'Warangal', 'Nizamabad', 'Karimnagar', 'Khammam',
            'Ranchi', 'Jamshedpur', 'Dhanbad', 'Bokaro', 'Deoghar',
            'Raipur', 'Bilaspur', 'Durg', 'Korba', 'Rajnandgaon',
            'Mumbai', 'Pune', 'Nagpur', 'Nashik', 'Aurangabad',
            'Ahmedabad', 'Surat', 'Vadodara', 'Rajkot', 'Bhavnagar'
        ]
        
        for i, village_name in enumerate(village_names):
            block_id = (i % 15) + 1
            population = random.randint(200, 2000)
            tribal_pct = random.uniform(20, 80)
            forest_pct = random.uniform(15, 70)
            water_bodies = random.randint(0, 5)
            agri_pct = random.uniform(20, 60)
            
            villages_data.append((
                village_name,
                f'V{i+1:03d}',
                block_id,
                population,
                tribal_pct,
                forest_pct,
                water_bodies,
                agri_pct
            ))
        
        cursor.executemany("""
            INSERT INTO villages (name, code, block_id, population, tribal_population_pct,
                                forest_cover_pct, water_bodies_count, agricultural_land_pct)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, villages_data)
        
        # Insert patta holders
        patta_holders_data = []
        holder_names = [
            'Ram Singh', 'Suresh Kumar', 'Lakshmi Devi', 'Mohan Lal', 'Geeta Bai',
            'Rajesh Kumar', 'Sunita Devi', 'Vikram Singh', 'Kamla Devi', 'Anil Kumar',
            'Pushpa Devi', 'Ramesh Kumar', 'Sita Devi', 'Harish Kumar', 'Meera Devi',
            'Jagdish Kumar', 'Usha Devi', 'Suresh Kumar', 'Kavita Devi', 'Ravi Kumar',
            'Anita Devi', 'Manoj Kumar', 'Sarita Devi', 'Vijay Kumar', 'Rekha Devi',
            'Amit Kumar', 'Priya Devi', 'Raj Kumar', 'Sunita Devi', 'Vikash Kumar',
            'Neha Devi', 'Rohit Kumar', 'Pooja Devi', 'Sandeep Kumar', 'Ritu Devi',
            'Ajay Kumar', 'Kiran Devi', 'Nitin Kumar', 'Shilpa Devi', 'Rakesh Kumar',
            'Deepa Devi', 'Mukesh Kumar', 'Seema Devi', 'Pankaj Kumar', 'Nisha Devi',
            'Arun Kumar', 'Rani Devi', 'Sanjay Kumar', 'Manju Devi', 'Vishal Kumar'
        ]
        
        tribal_groups = [
            'Bhil', 'Gond', 'Santal', 'Munda', 'Oraon', 'Khond', 'Sora', 'Gadaba',
            'Bondo', 'Dongria Kondh', 'Kutia Kondh', 'Paroja', 'Bhatra', 'Sabar',
            'Lodha', 'Mahali', 'Birhor', 'Asur', 'Korwa', 'Paharia'
        ]
        
        claim_types = ['IFR', 'CR', 'CFR']
        statuses = ['filed', 'under_verification', 'granted', 'rejected', 'appealed']
        
        for i in range(200):  # 200 patta holders
            village_id = random.randint(1, len(villages_data))
            holder_name = random.choice(holder_names)
            father_name = random.choice(holder_names)
            tribal_group = random.choice(tribal_groups)
            claim_type = random.choice(claim_types)
            status = random.choice(statuses)
            area_claimed = random.uniform(0.5, 5.0)
            area_vested = area_claimed * random.uniform(0.7, 1.0) if status == 'granted' else 0
            
            patta_holders_data.append((
                f'FILE_{i+1:06d}',
                holder_name,
                father_name,
                tribal_group,
                random.randint(2, 8),
                claim_type,
                'ST' if random.random() > 0.3 else 'OTFD',
                village_id,
                area_claimed,
                area_vested,
                status,
                f'SURV_{random.randint(100, 999)}',
                f'DAG_{random.randint(10, 99)}',
                f'KHAS_{random.randint(1000, 9999)}',
                f'PATTA_{random.randint(10000, 99999)}',
                f'document_{i+1}.pdf',
                random.randint(100000, 5000000),
                random.uniform(0.7, 0.95),
                'system',
                datetime.now() - timedelta(days=random.randint(1, 365))
            ))
        
        cursor.executemany("""
            INSERT INTO patta_holders (file_id, holder_name, father_husband_name, tribal_group,
                                     family_size, claim_type, claimant_category, village_id,
                                     area_claimed, area_vested, status,
                                     survey_number, dag_number, khasra_number, patta_number,
                                     document_file_name, document_file_size, extraction_accuracy,
                                     uploaded_by, uploaded_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, patta_holders_data)
        
        # Insert progress tracking data
        progress_data = []
        quarters = ['2023-Q1', '2023-Q2', '2023-Q3', '2023-Q4', '2024-Q1', '2024-Q2']
        
        for village_id in range(1, len(villages_data) + 1):
            for quarter in quarters:
                ifr_filed = random.randint(5, 25)
                ifr_granted = int(ifr_filed * random.uniform(0.6, 0.9))
                ifr_rejected = ifr_filed - ifr_granted - random.randint(0, 3)
                
                cr_filed = random.randint(2, 10)
                cr_granted = int(cr_filed * random.uniform(0.7, 0.95))
                cr_rejected = cr_filed - cr_granted
                
                cfr_filed = random.randint(1, 5)
                cfr_granted = int(cfr_filed * random.uniform(0.8, 1.0))
                cfr_rejected = cfr_filed - cfr_granted
                
                total_area_vested = (ifr_granted + cr_granted) * random.uniform(1.5, 3.0)
                cfr_managed_area = cfr_granted * random.uniform(50, 200)
                
                progress_data.append((
                    village_id,
                    quarter,
                    int(quarter.split('-')[0]),
                    ifr_filed,
                    ifr_granted,
                    ifr_rejected,
                    cr_filed,
                    cr_granted,
                    cr_rejected,
                    cfr_filed,
                    cfr_granted,
                    cfr_rejected,
                    total_area_vested,
                    cfr_managed_area,
                    f'Progress update for {quarter}'
                ))
        
        cursor.executemany("""
            INSERT INTO progress_tracking (village_id, quarter, year, ifr_filed, ifr_granted,
                                          ifr_rejected, cr_filed, cr_granted, cr_rejected,
                                          cfr_filed, cfr_granted, cfr_rejected,
                                          total_area_vested, cfr_managed_area, remarks)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, progress_data)
        
        # Insert asset mapping data
        asset_mapping_data = []
        
        for village_id in range(1, len(villages_data) + 1):
            farmland_pct = random.uniform(20, 60)
            forest_pct = random.uniform(15, 70)
            water_pct = random.uniform(2, 15)
            homestead_pct = random.uniform(5, 25)
            
            # Ensure percentages add up to ~100%
            total = farmland_pct + forest_pct + water_pct + homestead_pct
            farmland_pct = (farmland_pct / total) * 100
            forest_pct = (forest_pct / total) * 100
            water_pct = (water_pct / total) * 100
            homestead_pct = (homestead_pct / total) * 100
            
            confidence_score = random.uniform(0.75, 0.95)
            total_pixels = random.randint(1000000, 10000000)
            
            asset_mapping_data.append((
                village_id,
                '1.0',
                datetime.now() - timedelta(days=random.randint(1, 30)),
                farmland_pct,
                forest_pct,
                water_pct,
                homestead_pct,
                confidence_score,
                total_pixels
            ))
        
        cursor.executemany("""
            INSERT INTO asset_mapping (village_id, model_version, classification_date,
                                     farmland_pct, forest_pct, water_pct, homestead_pct,
                                     confidence_score, total_pixels)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, asset_mapping_data)
        
        # Insert DSS recommendations
        dss_recommendations_data = []
        schemes = [
            ('PM-KISAN', 'Agriculture', 'Income Support', '₹6000/year'),
            ('Jal Jeevan Mission', 'Jal Shakti', 'Water Supply', 'Infrastructure'),
            ('MGNREGA', 'Rural Development', 'Employment', '₹200/day'),
            ('DAJGUA', 'Tribal Affairs', 'Tribal Development', '₹50000/household'),
            ('PMGSY', 'Rural Development', 'Infrastructure', 'Road Infrastructure'),
            ('PMUY', 'Petroleum', 'Energy', 'LPG Connection')
        ]
        
        for village_id in range(1, len(villages_data) + 1):
            # Each village gets 2-4 recommendations
            num_recommendations = random.randint(2, 4)
            selected_schemes = random.sample(schemes, num_recommendations)
            
            for scheme_name, ministry, category, benefit in selected_schemes:
                eligibility_score = random.uniform(0.6, 0.95)
                priority = random.choice(['High', 'Medium', 'Low'])
                beneficiaries_estimate = random.randint(50, 500)
                convergence_score = random.uniform(0.7, 0.95)
                
                reasons = [
                    f'High {category.lower()} potential',
                    'Meets eligibility criteria',
                    'Priority area for development',
                    'Convergence opportunity available'
                ]
                
                dss_recommendations_data.append((
                    village_id,
                    scheme_name.replace(' ', '_').lower(),
                    scheme_name,
                    ministry,
                    category,
                    eligibility_score,
                    priority,
                    beneficiaries_estimate,
                    benefit,
                    convergence_score,
                    json.dumps(reasons),
                    datetime.now() - timedelta(days=random.randint(1, 30))
                ))
        
        cursor.executemany("""
            INSERT INTO dss_recommendations (village_id, scheme_key, scheme_name, ministry,
                                           category, eligibility_score, priority,
                                           beneficiaries_estimate, benefit_amount,
                                           convergence_score, reasons, recommendation_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, dss_recommendations_data)
        
        conn.commit()
        print(f"Database seeded successfully!")
        print(f"- {len(states_data)} states")
        print(f"- {len(districts_data)} districts")
        print(f"- {len(blocks_data)} blocks")
        print(f"- {len(villages_data)} villages")
        print(f"- {len(patta_holders_data)} patta holders")
        print(f"- {len(progress_data)} progress records")
        print(f"- {len(asset_mapping_data)} asset mapping records")
        print(f"- {len(dss_recommendations_data)} DSS recommendations")
        
    except Exception as e:
        conn.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        conn.close()

def create_sample_files():
    """Create sample files for testing"""
    
    # Create sample directory
    sample_dir = 'sample_data'
    os.makedirs(sample_dir, exist_ok=True)
    
    # Create sample patta documents
    sample_documents = [
        {
            'filename': 'sample_patta_1.pdf',
            'content': '''
            FOREST RIGHTS ACT - INDIVIDUAL FOREST RIGHTS
            Village: Khargone
            Name: Ram Singh
            Father: Suresh Singh
            Tribal Group: Bhil
            Claim Type: IFR
            Area: 2.5 hectares
            Survey No: 123/45
            Dag No: 67/89
            Khasra No: 1234
            Patta No: 56789
            Latitude: 21.8225
            Longitude: 75.6102
            Status: Granted
            '''
        },
        {
            'filename': 'sample_patta_2.pdf',
            'content': '''
            FOREST RIGHTS ACT - COMMUNITY RIGHTS
            Village: Jhabua
            Name: Lakshmi Devi
            Husband: Mohan Lal
            Tribal Group: Gond
            Claim Type: CR
            Area: 1.8 hectares
            Survey No: 234/56
            Dag No: 78/90
            Khasra No: 2345
            Patta No: 67890
            Latitude: 22.5000
            Longitude: 74.5000
            Status: Under Verification
            '''
        },
        {
            'filename': 'sample_patta_3.pdf',
            'content': '''
            FOREST RIGHTS ACT - COMMUNITY FOREST RIGHTS
            Village: Koraput
            Name: Rajesh Kumar
            Father: Vikram Singh
            Tribal Group: Santal
            Claim Type: CFR
            Area: 3.2 hectares
            Survey No: 345/67
            Dag No: 89/01
            Khasra No: 3456
            Patta No: 78901
            Latitude: 18.8000
            Longitude: 82.7000
            Status: Filed
            '''
        }
    ]
    
    for doc in sample_documents:
        filepath = os.path.join(sample_dir, doc['filename'])
        with open(filepath, 'w') as f:
            f.write(doc['content'])
        print(f"Created sample file: {filepath}")
    
    # Create sample configuration files
    config_files = {
        'sample_config.json': {
            'database': {
                'url': 'sqlite:///fra_atlas.db',
                'use_postgis': False
            },
            'ocr': {
                'tesseract_config': '--oem 3 --psm 6 -l eng+tam',
                'batch_size': 10,
                'max_retries': 3
            },
            'dss': {
                'ml_weight': 0.5,
                'threshold': 0.5
            },
            'tiles': {
                'tile_size': 256,
                'max_zoom': 18,
                'min_zoom': 1
            }
        },
        'sample_schemes.json': {
            'schemes': [
                {
                    'name': 'PM-KISAN',
                    'ministry': 'Agriculture',
                    'category': 'Income Support',
                    'eligibility_criteria': {
                        'land_holding': '<= 2 hectares',
                        'farmer_type': 'small_marginal'
                    },
                    'benefit_amount': '₹6000/year',
                    'convergence_score': 0.8,
                    'priority': 1
                },
                {
                    'name': 'Jal Jeevan Mission',
                    'ministry': 'Jal Shakti',
                    'category': 'Water Supply',
                    'eligibility_criteria': {
                        'water_scarcity': True,
                        'population': '>= 100'
                    },
                    'benefit_amount': 'Infrastructure',
                    'convergence_score': 0.9,
                    'priority': 2
                }
            ]
        }
    }
    
    for filename, content in config_files.items():
        filepath = os.path.join(sample_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(content, f, indent=2)
        print(f"Created config file: {filepath}")
    
    print(f"\nSample files created in: {sample_dir}")

def generate_test_data():
    """Generate comprehensive test data"""
    
    print("Generating FRA-SENTINEL test data...")
    
    # Seed database
    seed_database()
    
    # Create sample files
    create_sample_files()
    
    print("\n✅ Test data generation completed!")
    print("\nNext steps:")
    print("1. Run the application: python webgis/enhanced_app.py")
    print("2. Access the dashboard: http://localhost:5000")
    print("3. View the atlas: http://localhost:5000/atlas")
    print("4. Access admin panel: http://localhost:5000/admin")

if __name__ == "__main__":
    generate_test_data()
