#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def reformat_to_simple(input_file: Path, output_file: Path) -> None:
    """Reformat complex GeoJSON to simple MultiPolygon format like sample."""
    
    with input_file.open("r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Extract coordinates dari berbagai kemungkinan struktur
    if isinstance(data, dict):
        if data.get("type") == "MultiPolygon" and "coordinates" in data:
            # Sudah format yang benar
            coords = data["coordinates"]
        elif data.get("type") == "GeometryCollection":
            # Ambil hanya MultiPolygon dari GeometryCollection
            coords = []
            for geom in data.get("geometries", []):
                if geom.get("type") == "MultiPolygon":
                    coords.extend(geom.get("coordinates", []))
        elif "geometry" in data:
            # Feature atau FeatureCollection
            geom = data["geometry"]
            if geom.get("type") == "MultiPolygon":
                coords = geom.get("coordinates", [])
            else:
                print("❌ Geometry type tidak didukung")
                return
        else:
            print("❌ Format GeoJSON tidak dikenali")
            return
    else:
        print("❌ Data bukan dictionary")
        return
    
    # Format output yang sama dengan sample.geojson
    output = {
        "type": "MultiPolygon",
        "coordinates": coords
    }
    
    with output_file.open("w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False)
    
    print(f"✅ Reformatted successfully!")
    print(f"💾 Saved to: {output_file}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Reformat GeoJSON to simple MultiPolygon format."
    )
    parser.add_argument(
        "--input",
        default="merged_fixed.geojson",
        help="Input GeoJSON file (default: merged_fixed.geojson)",
    )
    parser.add_argument(
        "--output",
        default="merged_final.geojson",
        help="Output GeoJSON file (default: merged_final.geojson)",
    )
    args = parser.parse_args()
    
    input_file = Path(args.input)
    output_file = Path(args.output)
    
    if not input_file.exists():
        print(f"❌ Input file not found: {input_file}")
        exit(1)
    
    reformat_to_simple(input_file, output_file)


if __name__ == "__main__":
    main()
