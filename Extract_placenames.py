import json
import csv
import argparse
import os

parser = argparse.ArgumentParser(description="Extract fields from npolar placenames JSON to CSV.")
parser.add_argument("input_file", help="Path to the input JSON file")
parser.add_argument("-o", "--output", help="Path to the output CSV file (optional)")
args = parser.parse_args()

INPUT_FILE = args.input_file

with open(INPUT_FILE, encoding="utf-8") as f:
    data = json.load(f)

# Find unique areas
areas = sorted(set(r.get("area", "") for r in data if r.get("area")))

# Ask user to filter by area if more than one exists
selected_area = None
if len(areas) > 1:
    options = ["All"] + areas
    print("\nMultiple areas found. Choose one to extract:")
    for i, option in enumerate(options):
        label = chr(65 + i)  # A, B, C, ...
        print(f"  {label}: {option}")

    while True:
        choice = input("\nEnter your choice (e.g. A): ").strip().upper()
        index = ord(choice) - 65
        if 0 <= index < len(options):
            selected_area = None if options[index] == "All" else options[index]
            print(f"\nExtracting: {options[index]}")
            break
        else:
            print(f"Invalid choice. Please enter a letter between A and {chr(65 + len(options) - 1)}.")

# Build output filename including the chosen area
area_suffix = ("_" + selected_area.replace(" ", "_")) if selected_area else "_All"
OUTPUT_FILE = args.output if args.output else os.path.splitext(INPUT_FILE)[0] + area_suffix + ".csv"

def clean(val):
    return str(val).replace('"', '') if val else ""

filtered_data = [r for r in data if selected_area is None or r.get("area") == selected_area]

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "name", "latitude", "longitude",
        "terrain_en", "terrain_nn", "terrain_type", "area"
    ])
    writer.writeheader()

    for r in filtered_data:
        name = r.get("name", {})
        name_val = name.get("@value", "") if isinstance(name, dict) else str(name)

        terrain = r.get("terrain", {})
        terrain_en = terrain.get("en", "") if isinstance(terrain, dict) else ""
        terrain_nn = terrain.get("nn", "") if isinstance(terrain, dict) else ""

        writer.writerow({
            "name":         clean(name_val),
            "latitude":     r.get("latitude", ""),
            "longitude":    r.get("longitude", ""),
            "terrain_en":   clean(terrain_en),
            "terrain_nn":   clean(terrain_nn),
            "terrain_type": clean(r.get("terrain_type", "")),
            "area":         clean(r.get("area", "")),
        })

print(f"Done — {len(filtered_data)} records written to {OUTPUT_FILE}")
