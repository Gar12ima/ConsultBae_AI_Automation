import pandas as pd
from pathlib import Path

DATA_DIR = Path("data")

files = [
    "source1_naukri_applicants.csv",
    "source2_gig_workers.csv",
    "source3_cbnexus_contacts.csv"
]

for file_name in files:
    file_path = DATA_DIR / file_name

    print("\n" + "=" * 70)
    print(f"FILE: {file_name}")
    print("=" * 70)

    df = pd.read_csv(file_path)

    print(f"\nRows: {len(df)}")
    print(f"Columns: {len(df.columns)}")

    print("\nCOLUMN NAMES:")
    for column in df.columns:
        print(f"  - {column}")

    print("\nFIRST 3 ROWS:")
    print(df.head(3).to_string(index=False))

    print("\nMISSING VALUES:")
    missing = df.isnull().sum()
    print(missing[missing > 0].to_string())

    print("\nDUPLICATE ROWS:")
    print(df.duplicated().sum())
    