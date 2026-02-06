#!/usr/bin/env python3
"""
Verify GeoJSON split files - Check struktur dan size
"""
import json
import os
import sys

def format_size(bytes):
    """Format bytes to human readable"""
    for unit in ['B', 'KB', 'MB']:
        if bytes < 1024:
            return f"{bytes:.1f} {unit}"
        bytes /= 1024
    return f"{bytes:.1f} GB"

def verify_geojson(file_path):
    """Verify and analyze a GeoJSON file"""
    if not os.path.exists(file_path):
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        size = os.path.getsize(file_path)
        
        # Analyze geometry
        geometry = data.get('geometry', {})
        geom_type = geometry.get('type', 'Unknown')
        
        # Count features/polygons
        if geom_type == 'Polygon':
            polygon_count = 1
        elif geom_type == 'MultiPolygon':
            polygon_count = len(geometry.get('coordinates', []))
        else:
            polygon_count = 0
        
        # Get properties
        properties = data.get('properties', {})
        
        return {
            'size': size,
            'geom_type': geom_type,
            'polygon_count': polygon_count,
            'properties': properties,
            'has_metadata': 'metadata' in data,
            'valid': True
        }
    except Exception as e:
        return {
            'error': str(e),
            'valid': False
        }

def main():
    if len(sys.argv) < 2:
        # Look for split files
        base_patterns = [
            'results/jawa_barat_split',
            'results/jawa_timur_split',
            'results/jawa_tengah_split'
        ]
        
        found_files = []
        for pattern in base_patterns:
            for side in ['left', 'right', 'north', 'south']:
                f = f"{pattern}_{side}.geojson"
                if os.path.exists(f):
                    found_files.append(f)
        
        if not found_files:
            print("❌ Tidak ada file split ditemukan")
            print("\nUsage: python3 verify_split.py <file1.geojson> [file2.geojson] ...")
            return 1
        
        files = found_files
    else:
        files = sys.argv[1:]
    
    print("\n" + "="*70)
    print("  📊 GeoJSON SPLIT VERIFICATION")
    print("="*70 + "\n")
    
    total_size = 0
    total_polygons = 0
    
    for file_path in files:
        print(f"📄 {file_path}")
        result = verify_geojson(file_path)
        
        if result is None:
            print(f"   ❌ File tidak ditemukan\n")
            continue
        
        if not result['valid']:
            print(f"   ❌ Error: {result['error']}\n")
            continue
        
        # Display info
        size = result['size']
        polygons = result['polygon_count']
        
        print(f"   Size: {format_size(size)}")
        print(f"   Geometry Type: {result['geom_type']}")
        print(f"   Polygon Count: {polygons}")
        
        # Properties
        props = result['properties']
        if props:
            print(f"   Properties:")
            if 'name' in props:
                print(f"      • Region: {props['name']}")
            if 'part' in props:
                print(f"      • Part: {props['part']}")
            if 'side' in props:
                print(f"      • Side: {props['side']}")
        
        if result['has_metadata']:
            print(f"   ✓ Metadata: Present")
        
        total_size += size
        total_polygons += polygons
        print()
    
    # Summary
    print("="*70)
    print("📈 SUMMARY")
    print("="*70)
    print(f"Files analyzed: {len(files)}")
    print(f"Total size: {format_size(total_size)}")
    print(f"Total polygons: {total_polygons}")
    print()
    
    if total_size < 100_000_000:  # Less than 100MB
        print("✅ File sizes terlihat OK untuk di-upload!")
    else:
        print("⚠️  File masih cukup besar, mungkin perlu split lebih lanjut")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
