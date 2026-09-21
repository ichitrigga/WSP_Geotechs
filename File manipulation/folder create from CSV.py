from pathlib import Path
import csv

# Folder containing this Python script
script_dir = Path(__file__).parent

# Create output folder
parent_folder = script_dir / "new folders"
parent_folder.mkdir(exist_ok=True)

# CSV located beside the script
csv_file = script_dir / "new folders.csv"

with open(csv_file, newline="", encoding="utf-8-sig") as f:
    reader = csv.reader(f)

    for row in reader:
        if not row:
            continue

        folder_name = row[0].strip()

        if folder_name:
            (parent_folder / folder_name).mkdir(parents=True, exist_ok=True)

print(f"Created folders in: {parent_folder}")