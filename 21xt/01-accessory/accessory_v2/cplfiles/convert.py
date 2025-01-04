#!/usr/bin/env python3
"""
Convert either:
- a KiCad .pos file, or
- a KiCad BOM .csv file (with columns like Ref,PosX,PosY,Rot,Side)

into a JLCPCB-compatible CPL .csv with columns:
  Designator,Mid X,Mid Y,Layer,Rotation
"""

import csv
import os

def parse_kicad_pos(pos_file_path):
    """
    Parse a KiCad .pos file. 
    Returns a dictionary of the form:
       {
          'C1': {'PosX': 41.35, 'PosY': -10.25, 'Side': 'bottom', 'Rot': 180.0},
          ...
       }
    """
    data = {}
    with open(pos_file_path, mode='r', encoding='utf-8', newline='') as f:
        for line in f:
            line = line.strip()
            # Skip empty lines or comment lines
            if not line or line.startswith('#') or line.startswith('##'):
                continue

            columns = line.split()
            if len(columns) < 7:
                continue

            ref = columns[0]
            posx = float(columns[3])
            posy = float(columns[4])
            rot  = float(columns[5])
            side = columns[6].lower()

            data[ref] = {
                'PosX': posx,
                'PosY': posy,
                'Rot': rot,
                'Side': side
            }
    return data

def parse_kicad_csv(bom_csv_path):
    """
    Parse a KiCad BOM-style .csv file that contains columns:
      Ref, Val, Package, PosX, PosY, Rot, Side
    Returns a dictionary of the same form as parse_kicad_pos.
    """
    data = {}
    # Use 'utf-8-sig' if your CSV may contain BOM (byte-order mark)
    with open(bom_csv_path, mode='r', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Try reading either 'Ref' or 'Designator'
            ref = row.get('Ref') or row.get('Designator')
            if not ref:
                continue

            # Convert position, rotation as floats
            posx = float(row.get('PosX', '0.0'))
            posy = float(row.get('PosY', '0.0'))
            rot  = float(row.get('Rot', '0.0'))
            side = row.get('Side', '').lower()

            data[ref] = {
                'PosX': posx,
                'PosY': posy,
                'Rot': rot,
                'Side': side
            }
    return data

def write_jlc_cpl(parsed_data, output_csv_path):
    """
    Write a JLCPCB-compatible CPL file with columns:
      Designator,Mid X,Mid Y,Layer,Rotation
    """
    with open(output_csv_path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])

        # Sort references for convenience
        for ref in sorted(parsed_data.keys()):
            pd = parsed_data[ref]
            mid_x = pd.get('PosX', 0.0)
            mid_y = pd.get('PosY', 0.0)
            side_raw = pd.get('Side', 'top').lower()
            rotation = pd.get('Rot', 0.0)

            # Convert side to "Top"/"Bottom" for JLC
            if side_raw.startswith('top'):
                layer = "Top"
            elif side_raw.startswith('bot'):
                layer = "Bottom"
            else:
                layer = "Top"

            writer.writerow([
                ref,
                f"{mid_x:.4f}",
                f"{mid_y:.4f}",
                layer,
                f"{rotation:.2f}"
            ])

def main():
    # Set your input path and output path below
    input_path = "accessory_v2-all-pos.csv"  # or "board.csv"
    output_cpl_path = "jlc_cpl.csv"

    # Detect extension to decide how to parse
    extension = os.path.splitext(input_path)[1].lower()

    if extension == '.pos':
        parsed_data = parse_kicad_pos(input_path)
    elif extension == '.csv':
        parsed_data = parse_kicad_csv(input_path)
    else:
        print("Unrecognized file format. Use either .pos or .csv.")
        return

    write_jlc_cpl(parsed_data, output_cpl_path)
    print(f"Created JLCPCB CPL: {output_cpl_path}")

if __name__ == "__main__":
    main()
