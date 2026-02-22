import requests
import json
from datetime import datetime, timedelta
import numpy as np
from PIL import Image
import io
import base64

class SatelliteDataManager:
    def __init__(self):
        self.base_url = "https://services.sentinel-hub.com/ogc/wms/"
        self.sentinel_api = "https://scihub.copernicus.eu/dhus/search"
        
    def get_latest_imagery(self, lat, lon, date_range=30):
        """Get latest Sentinel-2 imagery for coordinates"""
        try:
            # Mock response for demo (replace with real API call)
            imagery_data = {
                'acquisition_date': (datetime.now() - timedelta(days=3)).isoformat(),
                'cloud_coverage': 8.5,
                'image_quality': 'PASSED',
                'processing_level': 'Level-2A',
                'tile_id': 'T43QFV',
                'satellite': 'Sentinel-2B',
                'resolution': '10m',
                'bands': ['B02', 'B03', 'B04', 'B08'],
                'metadata': {
                    'sun_elevation': 62.5,
                    'sun_azimuth': 158.2,
                    'viewing_angle': 7.8
                },
                'download_url': f'mock_url_for_lat_{lat}_lon_{lon}',
                'preview_url': self.generate_preview_url(lat, lon)
            }
            
            return imagery_data
            
        except Exception as e:
            print(f"Error fetching satellite data: {e}")
            return None
    
    def generate_preview_url(self, lat, lon):
        """Generate preview URL for satellite imagery"""
        # Mock URL generation
        return f"https://services.sentinel-hub.com/ogc/wms/preview?lat={lat}&lon={lon}"
    
    def calculate_vegetation_indices(self, lat, lon):
        """Calculate vegetation indices for the area"""
        # Mock calculations
        indices = {
            'ndvi': round(np.random.uniform(0.3, 0.8), 3),
            'evi': round(np.random.uniform(0.2, 0.6), 3),
            'savi': round(np.random.uniform(0.25, 0.7), 3),
            'ndwi': round(np.random.uniform(-0.1, 0.3), 3),
            'calculation_date': datetime.now().isoformat()
        }
        
        return indices
    
    def get_weather_data(self, lat, lon):
        """Get current weather data for the location"""
        # Mock weather data
        weather = {
            'temperature': round(np.random.uniform(25, 35), 1),
            'humidity': round(np.random.uniform(60, 85), 1),
            'precipitation': round(np.random.uniform(0, 10), 1),
            'wind_speed': round(np.random.uniform(5, 15), 1),
            'cloud_cover': round(np.random.uniform(10, 40), 1),
            'description': np.random.choice(['Partly Cloudy', 'Clear Sky', 'Scattered Clouds']),
            'timestamp': datetime.now().isoformat()
        }
        
        return weather

# Save this file
satellite_manager = SatelliteDataManager()
