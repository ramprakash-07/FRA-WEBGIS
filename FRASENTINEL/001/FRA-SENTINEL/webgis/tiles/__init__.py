"""
Tile Server for FRA-SENTINEL
Generates map tiles for efficient rendering at scale
Supports both PostGIS and SQLite backends
"""

import os
import math
import json
import logging
from typing import Dict, List, Tuple, Optional
from flask import Blueprint, request, Response, jsonify
from PIL import Image, ImageDraw, ImageFont
import io
import base64

logger = logging.getLogger(__name__)

# Create blueprint
tile_bp = Blueprint('tiles', __name__, url_prefix='/api/tiles')

# Tile configuration
TILE_SIZE = 256
MAX_ZOOM = 18
MIN_ZOOM = 1

def deg2num(lat_deg: float, lon_deg: float, zoom: int) -> Tuple[int, int]:
    """Convert lat/lon to tile coordinates"""
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return (xtile, ytile)

def num2deg(xtile: int, ytile: int, zoom: int) -> Tuple[float, float]:
    """Convert tile coordinates to lat/lon"""
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return (lat_deg, lon_deg)

class TileRenderer:
    """Renders map tiles for different data layers"""
    
    def __init__(self):
        self.colors = {
            'ifr': (0, 255, 0, 180),      # Green for IFR
            'cr': (0, 0, 255, 180),       # Blue for CR
            'cfr': (255, 0, 0, 180),      # Red for CFR
            'village': (128, 128, 128, 200), # Gray for villages
            'forest': (34, 139, 34, 150), # Forest green
            'water': (0, 191, 255, 150),  # Sky blue
            'agriculture': (255, 215, 0, 150), # Gold
            'homestead': (255, 165, 0, 150) # Orange
        }
    
    def render_patta_holders_tile(self, z: int, x: int, y: int, layer: str = 'ifr') -> Image.Image:
        """Render patta holders tile"""
        # Create transparent tile
        tile = Image.new('RGBA', (TILE_SIZE, TILE_SIZE), (0, 0, 0, 0))
        draw = ImageDraw.Draw(tile)
        
        # Get tile bounds
        lat_min, lon_min = num2deg(x, y + 1, z)
        lat_max, lon_max = num2deg(x + 1, y, z)
        
        # Query patta holders in tile bounds
        patta_holders = self._get_patta_holders_in_bounds(lat_min, lon_min, lat_max, lon_max, layer)
        
        # Render points
        for holder in patta_holders:
            # Convert lat/lon to pixel coordinates
            px, py = self._latlon_to_pixel(
                holder['latitude'], holder['longitude'],
                lat_min, lon_min, lat_max, lon_max
            )
            
            # Draw circle for patta holder
            color = self.colors.get(layer, (255, 0, 0, 180))
            radius = max(2, min(8, 12 - z))  # Size based on zoom level
            
            draw.ellipse(
                [px - radius, py - radius, px + radius, py + radius],
                fill=color,
                outline=(255, 255, 255, 255)
            )
        
        return tile
    
    def render_village_boundaries_tile(self, z: int, x: int, y: int) -> Image.Image:
        """Render village boundaries tile"""
        tile = Image.new('RGBA', (TILE_SIZE, TILE_SIZE), (0, 0, 0, 0))
        draw = ImageDraw.Draw(tile)
        
        # Get tile bounds
        lat_min, lon_min = num2deg(x, y + 1, z)
        lat_max, lon_max = num2deg(x + 1, y, z)
        
        # Query villages in tile bounds
        villages = self._get_villages_in_bounds(lat_min, lon_min, lat_max, lon_max)
        
        # Render village boundaries
        for village in villages:
            if village.get('geometry'):
                # Convert polygon coordinates to pixel coordinates
                polygon_pixels = self._polygon_to_pixels(
                    village['geometry'], lat_min, lon_min, lat_max, lon_max
                )
                
                if polygon_pixels:
                    # Draw polygon
                    color = self.colors['village']
                    draw.polygon(polygon_pixels, fill=color, outline=(255, 255, 255, 255))
        
        return tile
    
    def render_asset_mapping_tile(self, z: int, x: int, y: int) -> Image.Image:
        """Render asset mapping tile"""
        tile = Image.new('RGBA', (TILE_SIZE, TILE_SIZE), (0, 0, 0, 0))
        draw = ImageDraw.Draw(tile)
        
        # Get tile bounds
        lat_min, lon_min = num2deg(x, y + 1, z)
        lat_max, lon_max = num2deg(x + 1, y, z)
        
        # Query asset mapping data in tile bounds
        assets = self._get_asset_mapping_in_bounds(lat_min, lon_min, lat_max, lon_max)
        
        # Render asset polygons
        for asset in assets:
            if asset.get('geometry'):
                polygon_pixels = self._polygon_to_pixels(
                    asset['geometry'], lat_min, lon_min, lat_max, lon_max
                )
                
                if polygon_pixels:
                    # Determine color based on land use
                    land_use = asset.get('land_use', 'forest')
                    color = self.colors.get(land_use, self.colors['forest'])
                    
                    draw.polygon(polygon_pixels, fill=color)
        
        return tile
    
    def _latlon_to_pixel(self, lat: float, lon: float, lat_min: float, lon_min: float, 
                        lat_max: float, lon_max: float) -> Tuple[int, int]:
        """Convert lat/lon to pixel coordinates within tile"""
        x = int((lon - lon_min) / (lon_max - lon_min) * TILE_SIZE)
        y = int((lat_max - lat) / (lat_max - lat_min) * TILE_SIZE)
        return (x, y)
    
    def _polygon_to_pixels(self, geometry: Dict, lat_min: float, lon_min: float, 
                          lat_max: float, lon_max: float) -> List[Tuple[int, int]]:
        """Convert polygon geometry to pixel coordinates"""
        if geometry.get('type') != 'Polygon':
            return []
        
        coordinates = geometry.get('coordinates', [])
        if not coordinates:
            return []
        
        # Get exterior ring
        exterior_ring = coordinates[0]
        pixels = []
        
        for coord in exterior_ring:
            if len(coord) >= 2:
                lon, lat = coord[0], coord[1]
                px, py = self._latlon_to_pixel(lat, lon, lat_min, lon_min, lat_max, lat_max)
                pixels.append((px, py))
        
        return pixels
    
    def _get_patta_holders_in_bounds(self, lat_min: float, lon_min: float, 
                                   lat_max: float, lon_max: float, layer: str) -> List[Dict]:
        """Get patta holders within tile bounds"""
        # This would query the database in a real implementation
        # For demo, return sample data
        return [
            {
                'latitude': (lat_min + lat_max) / 2,
                'longitude': (lon_min + lon_max) / 2,
                'claim_type': layer.upper(),
                'holder_name': 'Sample Holder',
                'area_hectares': 2.5
            }
        ]
    
    def _get_villages_in_bounds(self, lat_min: float, lon_min: float, 
                              lat_max: float, lon_max: float) -> List[Dict]:
        """Get villages within tile bounds"""
        # This would query the database in a real implementation
        # For demo, return sample data
        return [
            {
                'name': 'Sample Village',
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [[
                        [lon_min, lat_min],
                        [lon_max, lat_min],
                        [lon_max, lat_max],
                        [lon_min, lat_max],
                        [lon_min, lat_min]
                    ]]
                }
            }
        ]
    
    def _get_asset_mapping_in_bounds(self, lat_min: float, lon_min: float, 
                                    lat_max: float, lon_max: float) -> List[Dict]:
        """Get asset mapping data within tile bounds"""
        # This would query the database in a real implementation
        # For demo, return sample data
        return [
            {
                'land_use': 'forest',
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [[
                        [lon_min, lat_min],
                        [lon_max, lat_min],
                        [lon_max, lat_max],
                        [lon_min, lat_max],
                        [lon_min, lat_min]
                    ]]
                }
            }
        ]

# Global tile renderer
tile_renderer = TileRenderer()

@tile_bp.route('/<layer>/<int:z>/<int:x>/<int:y>.png')
def get_tile(layer: str, z: int, x: int, y: int):
    """Get map tile"""
    try:
        # Validate zoom level
        if z < MIN_ZOOM or z > MAX_ZOOM:
            return Response("Invalid zoom level", status=400)
        
        # Render tile based on layer type
        if layer in ['ifr', 'cr', 'cfr']:
            tile = tile_renderer.render_patta_holders_tile(z, x, y, layer)
        elif layer == 'villages':
            tile = tile_renderer.render_village_boundaries_tile(z, x, y)
        elif layer == 'assets':
            tile = tile_renderer.render_asset_mapping_tile(z, x, y)
        else:
            return Response("Invalid layer", status=400)
        
        # Convert to PNG bytes
        img_buffer = io.BytesIO()
        tile.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        return Response(
            img_buffer.getvalue(),
            mimetype='image/png',
            headers={
                'Cache-Control': 'public, max-age=3600',  # Cache for 1 hour
                'Access-Control-Allow-Origin': '*'
            }
        )
    
    except Exception as e:
        logger.error(f"Tile rendering error: {e}")
        return Response("Tile rendering failed", status=500)

@tile_bp.route('/info')
def get_tile_info():
    """Get tile server information"""
    return jsonify({
        'tile_size': TILE_SIZE,
        'min_zoom': MIN_ZOOM,
        'max_zoom': MAX_ZOOM,
        'layers': {
            'ifr': 'Individual Forest Rights',
            'cr': 'Community Rights',
            'cfr': 'Community Forest Rights',
            'villages': 'Village Boundaries',
            'assets': 'Asset Mapping'
        },
        'attribution': 'FRA-SENTINEL',
        'bounds': [-180, -85, 180, 85]
    })

@tile_bp.route('/<layer>/bounds')
def get_layer_bounds(layer: str):
    """Get bounds for a specific layer"""
    # This would query the database for actual bounds
    # For demo, return India bounds
    return jsonify({
        'layer': layer,
        'bounds': [68.0, 6.0, 97.0, 37.0],  # India bounds
        'center': [82.5, 21.5],
        'zoom': 5
    })

# Tile cache management
class TileCache:
    """Simple in-memory tile cache"""
    
    def __init__(self, max_size: int = 1000):
        self.cache: Dict[str, bytes] = {}
        self.max_size = max_size
        self.access_times: Dict[str, float] = {}
    
    def get(self, key: str) -> Optional[bytes]:
        """Get tile from cache"""
        if key in self.cache:
            self.access_times[key] = time.time()
            return self.cache[key]
        return None
    
    def set(self, key: str, value: bytes):
        """Set tile in cache"""
        if len(self.cache) >= self.max_size:
            self._evict_oldest()
        
        self.cache[key] = value
        self.access_times[key] = time.time()
    
    def _evict_oldest(self):
        """Evict oldest accessed tile"""
        if not self.access_times:
            return
        
        oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        del self.cache[oldest_key]
        del self.access_times[oldest_key]

# Global tile cache
tile_cache = TileCache()

# Enhanced tile endpoint with caching
@tile_bp.route('/cached/<layer>/<int:z>/<int:x>/<int:y>.png')
def get_cached_tile(layer: str, z: int, x: int, y: int):
    """Get cached map tile"""
    cache_key = f"{layer}_{z}_{x}_{y}"
    
    # Check cache first
    cached_tile = tile_cache.get(cache_key)
    if cached_tile:
        return Response(
            cached_tile,
            mimetype='image/png',
            headers={
                'Cache-Control': 'public, max-age=3600',
                'Access-Control-Allow-Origin': '*',
                'X-Cache': 'HIT'
            }
        )
    
    # Generate tile
    try:
        if layer in ['ifr', 'cr', 'cfr']:
            tile = tile_renderer.render_patta_holders_tile(z, x, y, layer)
        elif layer == 'villages':
            tile = tile_renderer.render_village_boundaries_tile(z, x, y)
        elif layer == 'assets':
            tile = tile_renderer.render_asset_mapping_tile(z, x, y)
        else:
            return Response("Invalid layer", status=400)
        
        # Convert to PNG bytes
        img_buffer = io.BytesIO()
        tile.save(img_buffer, format='PNG')
        tile_bytes = img_buffer.getvalue()
        
        # Cache the tile
        tile_cache.set(cache_key, tile_bytes)
        
        return Response(
            tile_bytes,
            mimetype='image/png',
            headers={
                'Cache-Control': 'public, max-age=3600',
                'Access-Control-Allow-Origin': '*',
                'X-Cache': 'MISS'
            }
        )
    
    except Exception as e:
        logger.error(f"Cached tile rendering error: {e}")
        return Response("Tile rendering failed", status=500)

# Tile generation utilities
def generate_tiles_for_layer(layer: str, min_zoom: int = 1, max_zoom: int = 10):
    """Generate tiles for a layer at multiple zoom levels"""
    generated_count = 0
    
    for z in range(min_zoom, max_zoom + 1):
        # Calculate tile range for India bounds
        x_min, y_min = deg2num(37.0, 68.0, z)  # North-east
        x_max, y_max = deg2num(6.0, 97.0, z)   # South-west
        
        for x in range(x_min, x_max + 1):
            for y in range(y_min, y_max + 1):
                try:
                    cache_key = f"{layer}_{z}_{x}_{y}"
                    
                    # Generate tile
                    if layer in ['ifr', 'cr', 'cfr']:
                        tile = tile_renderer.render_patta_holders_tile(z, x, y, layer)
                    elif layer == 'villages':
                        tile = tile_renderer.render_village_boundaries_tile(z, x, y)
                    elif layer == 'assets':
                        tile = tile_renderer.render_asset_mapping_tile(z, x, y)
                    else:
                        continue
                    
                    # Convert to PNG and cache
                    img_buffer = io.BytesIO()
                    tile.save(img_buffer, format='PNG')
                    tile_bytes = img_buffer.getvalue()
                    
                    tile_cache.set(cache_key, tile_bytes)
                    generated_count += 1
                    
                except Exception as e:
                    logger.error(f"Error generating tile {layer}/{z}/{x}/{y}: {e}")
    
    logger.info(f"Generated {generated_count} tiles for layer {layer}")
    return generated_count

if __name__ == "__main__":
    # Test tile generation
    import time
    
    start_time = time.time()
    count = generate_tiles_for_layer('ifr', 1, 5)
    end_time = time.time()
    
    print(f"Generated {count} tiles in {end_time - start_time:.2f} seconds")
    print(f"Cache size: {len(tile_cache.cache)} tiles")









