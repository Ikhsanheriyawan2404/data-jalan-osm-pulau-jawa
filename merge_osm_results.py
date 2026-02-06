#!/usr/bin/env python3
import argparse
import json
import time
from pathlib import Path
from typing import Dict, Iterable


def _load_json(path: Path) -> Dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _iter_features(doc: Dict) -> Iterable[Dict]:
    doc_type = doc.get("type")
    if doc_type == "FeatureCollection":
        for feature in doc.get("features", []):
            if isinstance(feature, dict):
                yield feature
        return
    if doc_type == "Feature":
        yield doc
        return
    # Geometry-only
    if "type" in doc and "coordinates" in doc:
        yield {
            "type": "Feature",
            "properties": {},
            "geometry": doc,
        }
        return
    raise ValueError("Unsupported GeoJSON structure")


def merge_geojson(input_dir: Path, output_file: Path) -> None:
    files = sorted(input_dir.glob("*.geojson"))
    if not files:
        raise FileNotFoundError(f"No .geojson files found in {input_dir}")

    output_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"Merging {len(files)} files from: {input_dir}")
    print(f"Output file: {output_file}")
    start_all = time.time()

    with output_file.open("w", encoding="utf-8") as f:
        f.write("{\n")
        f.write("  \"type\": \"FeatureCollection\",\n")
        f.write("  \"features\": [\n")

        first = True
        total_features = 0
        for file_path in files:
            start_file = time.time()
            print(f"-> Loading: {file_path.name}")
            doc = _load_json(file_path)
            file_features = 0
            for feature in _iter_features(doc):
                if not first:
                    f.write(",\n")
                f.write(json.dumps(feature, ensure_ascii=False))
                first = False
                file_features += 1
                total_features += 1

            elapsed = time.time() - start_file
            print(
                f"   Added {file_features} features from {file_path.name} "
                f"in {elapsed:.1f}s"
            )

        f.write("\n  ]\n")
        f.write("}\n")

    elapsed_all = time.time() - start_all
    print(
        f"Done. Total features: {total_features}. "
        f"Elapsed: {elapsed_all:.1f}s"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Merge all .geojson files in a folder into one FeatureCollection."
    )
    parser.add_argument(
        "--input-dir",
        default="results-from-osm",
        help="Directory containing .geojson files (default: results-from-osm)",
    )
    parser.add_argument(
        "--output",
        default="final-pulau-jawa/final_pulau_jawa.geojson",
        help="Output GeoJSON file (default: final-pulau-jawa/final_pulau_jawa.geojson)",
    )
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_file = Path(args.output)

    merge_geojson(input_dir, output_file)


if __name__ == "__main__":
    main()
