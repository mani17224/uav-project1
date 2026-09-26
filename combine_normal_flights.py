import glob
import os
import re
import pandas as pd

PROCESSED_DIR = "processed_data"
OUTPUT_FILE = "processed_data/normal_flights.csv"

print("========================================")
print("      COMBINING NORMAL FLIGHTS")
print("========================================")

files = glob.glob(
    os.path.join(PROCESSED_DIR, "flight*_processed.csv")
)

files = sorted(
    files,
    key=lambda x: int(
        re.search(r"flight(\d+)_processed", x).group(1)
    )
)

if not files:
    raise FileNotFoundError("No processed flight files found.")

all_flights = []

for file in files:

    match = re.search(
        r"flight(\d+)_processed",
        file
    )

    flight_id = int(match.group(1))

    print(f"Loading Flight {flight_id:02d}...")

    df = pd.read_csv(file)

    df["flight_id"] = flight_id

    print(f"Flight {flight_id:02d} samples: {len(df)}")

    all_flights.append(df)

print()
print("Combining flights...")

combined = pd.concat(
    all_flights,
    ignore_index=True
)

print()
print("Checking constant features...")

exclude = ["time_sec", "flight_id"]

constant_features = []

for column in combined.columns:

    if column in exclude:
        continue

    if combined[column].nunique() <= 1:
        constant_features.append(column)
        print(f"Removing constant feature: {column}")

if constant_features:
    combined = combined.drop(
        columns=constant_features
    )

combined.to_csv(
    OUTPUT_FILE,
    index=False
)

print()
print("========================================")
print("       COMBINATION COMPLETED")
print("========================================")

print(f"Total samples : {len(combined)}")
print(f"Total columns : {len(combined.columns)}")
print(f"Output file   : {os.path.abspath(OUTPUT_FILE)}")

print()
print("Samples per flight:")

print(
    combined["flight_id"]
    .value_counts()
    .sort_index()
)

print()
print("Final columns:")

for i, column in enumerate(
    combined.columns,
    start=1
):
    print(f"{i:2d}. {column}")

print()
print("Saved successfully!")
print("========================================")
