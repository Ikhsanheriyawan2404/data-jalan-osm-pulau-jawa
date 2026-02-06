#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple


def _load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _extract_geometry(doc: Dict[str, Any]) -> Tuple[str, List]:
    if "geometry" in doc and isinstance(doc["geometry"], dict):
        geom = doc["geometry"]
    else:
        geom = doc

    geom_type = geom.get("type")
    coords = geom.get("coordinates")
    if geom_type is None or coords is None:
        raise ValueError("Invalid GeoJSON: missing type/coordinates")

    return geom_type, coords


def _to_multipolygon_coords(geom_type: str, coords: List) -> List:
    if geom_type == "MultiPolygon":
        return coords
    if geom_type == "Polygon":
        return [coords]
    raise ValueError(f"Unsupported geometry type: {geom_type}")


def merge_geojson(input_dir: Path, output_file: Path) -> None:
    files = sorted(input_dir.glob("*.geojson"))
    if not files:
        raise FileNotFoundError(f"No .geojson files found in {input_dir}")

    merged_coords: List = []
    for file_path in files:
        doc = _load_json(file_path)
        geom_type, coords = _extract_geometry(doc)
        merged_coords.extend(_to_multipolygon_coords(geom_type, coords))

    merged = {
        "type": "MultiPolygon",
        "coordinates": merged_coords,
    }

    with output_file.open("w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Merge GeoJSON files into a single MultiPolygon GeoJSON."
    )
    parser.add_argument(
        "--input-dir",
        default="data",
        help="Directory containing .geojson files (default: data)",
    )
    parser.add_argument(
        "--output",
        default="merged.geojson",
        help="Output GeoJSON file (default: merged.geojson)",
    )
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_file = Path(args.output)

    merge_geojson(input_dir, output_file)


if __name__ == "__main__":
    main()
