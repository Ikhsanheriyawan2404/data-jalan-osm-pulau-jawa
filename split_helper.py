#!/usr/bin/env python3
"""
Helper script untuk split GeoJSON files dengan mudah
"""
import os
import sys

def print_menu():
    print("\n" + "="*60)
    print("  📍 GEOJSON SPLITTER - Pilih metode split")
    print("="*60)
    print("\n1. Longitude Split (Vertikal) - Default")
    print("   → Membagi dari garis tengah longitude (barat-timur)")
    print("   → Cocok untuk wilayah yang memanjang timur-barat")
    print("\n2. Latitude Split (Horizontal)")
    print("   → Membagi dari garis tengah latitude (utara-selatan)")
    print("   → Cocok untuk wilayah yang memanjang utara-selatan")
    print("\n3. Exit")
    print("\n" + "="*60)

def parse_args():
    if len(sys.argv) < 2:
        input_file = "provinsi-pulau-indonesia/jawa_barat_32.geojson"
    else:
        input_file = sys.argv[1]
    
    if len(sys.argv) < 3:
        output_prefix = "results/" + os.path.basename(input_file).replace('.geojson', '_split')
    else:
        output_prefix = sys.argv[2]
    
    return input_file, output_prefix

def validate_file(file_path):
    if not os.path.exists(file_path):
        print(f"❌ File tidak ditemukan: {file_path}")
        return False
    if not file_path.endswith('.geojson'):
        print(f"❌ File harus format .geojson")
        return False
    return True

def main():
    input_file, output_prefix = parse_args()
    
    # Validasi file
    if not validate_file(input_file):
        return 1
    
    print(f"\n📁 Input file: {input_file}")
    print(f"📁 Output prefix: {output_prefix}")
    
    print_menu()
    
    choice = input("Pilih opsi (1-3): ").strip()
    
    if choice == "1":
        method = "longitude"
        print("\n✓ Dipilih: Longitude Split (Vertikal)")
    elif choice == "2":
        method = "latitude"
        print("\n✓ Dipilih: Latitude Split (Horizontal)")
    elif choice == "3":
        print("\nExit")
        return 0
    else:
        print("❌ Opsi tidak valid!")
        return 1
    
    print("\n⏳ Processing...")
    cmd = f"python3 split_geojson.py '{input_file}' '{output_prefix}' {method}"
    exit_code = os.system(cmd)
    
    if exit_code == 0:
        print("\n✅ Berhasil! File output ada di folder results/")
        # List output files
        output_dir = os.path.dirname(output_prefix) or '.'
        base_name = os.path.basename(output_prefix)
        
        print("\n📄 Output files:")
        for f in ['left', 'right', 'north', 'south']:
            possible_file = f"{output_prefix}_{f}.geojson"
            if os.path.exists(possible_file):
                size = os.path.getsize(possible_file) / 1024
                print(f"   • {os.path.basename(possible_file)} ({size:.1f} KB)")
        
        return 0
    else:
        print("\n❌ Error saat processing")
        return 1

if __name__ == "__main__":
    sys.exit(main())
