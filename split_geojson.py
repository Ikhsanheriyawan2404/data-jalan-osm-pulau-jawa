import json
import os

try:
    from shapely.geometry import LineString, shape
    from shapely.ops import split, unary_union
except ImportError as exc:
    raise SystemExit(
        "Shapely is required. Install it with: pip install shapely"
    ) from exc

def load_geojson(file_path):
    """Load GeoJSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_bounds(geom):
    """Get bounding box of geometry"""
    coords = []
    
    if geom['type'] == 'MultiPolygon':
        for polygon in geom['coordinates']:
            for ring in polygon:
                coords.extend(ring)
    elif geom['type'] == 'Polygon':
        for ring in geom['coordinates']:
            coords.extend(ring)
    
    # Extract all coordinates
    lons = [c[0] for c in coords]
    lats = [c[1] for c in coords]
    
    return min(lons), min(lats), max(lons), max(lats)

def _split_by_line(data, output_prefix, line, axis_value, sides):
    geometry = data["geometry"]
    properties = data["properties"]

    geom = shape(geometry)
    merged = unary_union(geom)
    result = split(merged, line)

    side_geoms = {sides[0]: [], sides[1]: []}
    for part in result.geoms:
        if part.is_empty:
            continue
        center = part.representative_point()
        if sides[0] == "left":
            key = sides[0] if center.x < axis_value else sides[1]
        else:
            key = sides[0] if center.y >= axis_value else sides[1]
        side_geoms[key].append(part)

    for idx, side in enumerate(sides, 1):
        if not side_geoms[side]:
            raise ValueError(f"No geometry created for side: {side}")

        merged_side = unary_union(side_geoms[side])
        output_data = {
            "type": "Feature",
            "metadata": data.get("metadata", {}),
            "properties": {
                **properties,
                "part": idx,
                "side": side,
                "original_region": properties.get("name", "Unknown"),
            },
            "geometry": json.loads(json.dumps(merged_side.__geo_interface__)),
        }

        output_file = f"{output_prefix}_{side}.geojson"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(f"✓ Created: {output_file}")


def split_geojson_by_longitude(input_file, output_prefix):
    """Split GeoJSON into two parts by longitude (vertical line)."""

    data = load_geojson(input_file)
    geometry = data["geometry"]

    min_lon, min_lat, max_lon, max_lat = get_bounds(geometry)
    center_lon = (min_lon + max_lon) / 2

    print(f"Bounds: lon({min_lon:.4f} - {max_lon:.4f}), lat({min_lat:.4f} - {max_lat:.4f})")
    print(f"Center longitude: {center_lon:.4f}")
    print("Split method: Vertical line (longitude)\n")

    line = LineString(
        [(center_lon, min_lat - 1.0), (center_lon, max_lat + 1.0)]
    )
    _split_by_line(data, output_prefix, line, center_lon, ("left", "right"))

def split_geojson_by_latitude(input_file, output_prefix):
    """Split GeoJSON into two parts by latitude (horizontal line)."""

    data = load_geojson(input_file)
    geometry = data["geometry"]

    min_lon, min_lat, max_lon, max_lat = get_bounds(geometry)
    center_lat = (min_lat + max_lat) / 2

    print(f"Bounds: lon({min_lon:.4f} - {max_lon:.4f}), lat({min_lat:.4f} - {max_lat:.4f})")
    print(f"Center latitude: {center_lat:.4f}")
    print("Split method: Horizontal line (latitude)\n")

    line = LineString(
        [(min_lon - 1.0, center_lat), (max_lon + 1.0, center_lat)]
    )
    _split_by_line(data, output_prefix, line, center_lat, ("north", "south"))

if __name__ == "__main__":
    import sys
    
    # Default file to process
    input_file = "provinsi-pulau-indonesia/jawa_barat_32.geojson"
    output_prefix = "results/jawa_barat_split"
    
    # Accept command line arguments
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_prefix = sys.argv[2]
    
    # Choose split method (longitude is default)
    split_method = "longitude"
    if len(sys.argv) > 3:
        split_method = sys.argv[3]
    
    print(f"🔄 Processing: {input_file}")
    print()
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_prefix) or '.', exist_ok=True)
    
    try:
        if split_method == "latitude":
            split_geojson_by_latitude(input_file, output_prefix)
        else:
            split_geojson_by_longitude(input_file, output_prefix)
        
        print("\n✅ Split completed successfully!")
        print(f"   Output files in: {os.path.dirname(output_prefix)}/")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
