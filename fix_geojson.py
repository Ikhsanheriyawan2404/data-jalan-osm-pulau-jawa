#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

try:
    from shapely.geometry import shape, mapping
    from shapely.validation import make_valid
except ImportError:
    print("ERROR: shapely not installed. Install with: pip3 install shapely")
    exit(1)


def _extract_polygons(geom) -> List:
    if geom.geom_type == "Polygon":
        return [geom]
    if geom.geom_type == "MultiPolygon":
        return list(geom.geoms)
    if geom.geom_type == "GeometryCollection":
        polygons = []
        for g in geom.geoms:
            if g.geom_type in ("Polygon", "MultiPolygon"):
                polygons.extend(_extract_polygons(g))
        return polygons
    return []


def fix_geojson(input_file: Path, output_file: Path) -> None:
    """Fix self-intersection and other geometry issues in GeoJSON file."""

    with input_file.open("r", encoding="utf-8") as f:
        data = json.load(f)

    # Convert to shapely geometry
    geom = shape(data)
    
    # Check if valid
    if not geom.is_valid:
        from shapely.validation import explain_validity
        reason = explain_validity(geom)
        print(f"⚠️  Invalid geometry detected: {reason}")
        print("🔧 Fixing geometry...")
        
        # Fix using make_valid (shapely 2.0+) or buffer(0) trick
        try:
            geom = make_valid(geom)
        except:
            # Fallback to buffer(0) trick for older shapely versions
            geom = geom.buffer(0)
        
        if geom.is_valid:
            print("✅ Geometry fixed successfully!")
        else:
            reason = explain_validity(geom)
            print(f"❌ Could not fix geometry: {reason}")
            return
    else:
        print("✅ Geometry is already valid!")
    
    # Normalize to MultiPolygon like sample.geojson
    polygons = _extract_polygons(geom)
    if not polygons:
        print("❌ No polygon geometry found after fixing")
        return

    # Convert back to GeoJSON MultiPolygon
    multi_coords = [mapping(p)["coordinates"] for p in polygons]
    fixed_data = {
        "type": "MultiPolygon",
        "coordinates": multi_coords,
    }

    with output_file.open("w", encoding="utf-8") as f:
        json.dump(fixed_data, f, ensure_ascii=False)
    
    print(f"💾 Saved to: {output_file}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fix self-intersection and geometry issues in GeoJSON files."
    )
    parser.add_argument(
        "--input",
        default="merged.geojson",
        help="Input GeoJSON file (default: merged.geojson)",
    )
    parser.add_argument(
        "--output",
        default="merged_fixed.geojson",
        help="Output fixed GeoJSON file (default: merged_fixed.geojson)",
    )
    args = parser.parse_args()
    
    input_file = Path(args.input)
    output_file = Path(args.output)
    
    if not input_file.exists():
        print(f"❌ Input file not found: {input_file}")
        exit(1)
    
    fix_geojson(input_file, output_file)


if __name__ == "__main__":
    main()
