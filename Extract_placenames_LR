import json
import argparse
import os

parser = argparse.ArgumentParser(description="Extract placenames from npolar JSON to Lightroom keyword txt file.")
parser.add_argument("input_file", help="Path to the input JSON file")
parser.add_argument("-o", "--output", help="Path to the output txt file (optional)")
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
        label = chr(65 + i)
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
OUTPUT_FILE = args.output if args.output else os.path.splitext(INPUT_FILE)[0] + area_suffix + ".txt"

# Filter records
EXCLUDED_TERRAIN = {"named-place", "stadnamn"}

filtered_data = []
for r in data:
    # Filter by area
    if selected_area and r.get("area") != selected_area:
        continue

    terrain = r.get("terrain", {})
    terrain_en = terrain.get("en", "") if isinstance(terrain, dict) else ""
    terrain_nn = terrain.get("nn", "") if isinstance(terrain, dict) else ""

    # Skip named-place / stadnamn
    if terrain_en in EXCLUDED_TERRAIN or terrain_nn in EXCLUDED_TERRAIN:
        continue

    lat = r.get("latitude", 0.0)
    lon = r.get("longitude", 0.0)

    # Skip entries with no useful location or terrain data
    has_location = not (lat == 0.0 and lon == 0.0)
    has_terrain = terrain_en or terrain_nn

    if not has_location and not has_terrain:
        continue

    name = r.get("name", {})
    name_val = name.get("@value", "") if isinstance(name, dict) else str(name)

    filtered_data.append({
        "name": name_val,
        "latitude": lat,
        "longitude": lon,
        "terrain_en": terrain_en,
        "terrain_nn": terrain_nn,
        "area": r.get("area", ""),
    })

# Write Lightroom keyword txt file
T = "\t"  # tab character

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    # Write area as top-level keyword
    area_label = selected_area if selected_area else "All"
    f.write(f"{area_label}\n")

    for r in filtered_data:
        f.write(f"{T}{r['name']}\n")

        lat = r["latitude"]
        lon = r["longitude"]
        terrain_en = r["terrain_en"]
        terrain_nn = r["terrain_nn"]

        if lat != 0.0:
            f.write(f"{T}{T}{{Lat:{lat}}}\n")
        if lon != 0.0:
            f.write(f"{T}{T}{{Lon:{lon}}}\n")
        if terrain_en:
            f.write(f"{T}{T}{{{terrain_en}}}\n")
        if terrain_nn:
            f.write(f"{T}{T}{{{terrain_nn}}}\n")

print(f"Done — {len(filtered_data)} records written to {OUTPUT_FILE}")
