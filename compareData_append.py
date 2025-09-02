import os
import pandas as pd

# Set working directory
#insert your working directory here

# Define unified column map for different years
column_aliases = {
    "Organization legal name": ["Organization legal name", " org_nm", "org_nm", "Facility Name"],
    "Line 1 Street Address": ["Line 1 Street Address", " adr_ln_1", "adr_ln_1"],
    "Claims based hospital affiliation CCN 1": ["Claims based hospital affiliation CCN 1", " hosp_afl_1", "Hospital affiliation CCN 1", "hosp_afl_1"],
    "Claims based hospital affiliation LBN 1": ["Claims based hospital affiliation LBN 1", " hosp_afl_lbn_1", "hosp_afl_lbn_1", "Hospital affiliation LBN 1"],
    "Zip Code": ["Zip Code", "ZIP Code", " zip", "zip"]
}

# Always keep these columns in PC
target_cols = ["NPI", "year"] + list(column_aliases.keys())


# Helper to rename columns to consistent names
def standardize_columns(df):
    col_map = {}
    for standard_name, variants in column_aliases.items():
        for variant in variants:
            if variant in df.columns:
                col_map[variant] = standard_name
                break
    return df.rename(columns=col_map)


# Load PC2013 and standardize
print("Reading PC2013.csv")
pc_total = pd.read_csv("PC2013.csv", dtype=str, encoding="utf-8", on_bad_lines="skip")
pc_total["year"] = 2013
pc_total = standardize_columns(pc_total)

# Loop through PC2014–PC2024
for year in range(2014, 2025):
    file_name = f"PC{year}.csv"
    print(f"Reading {file_name}")
    try:
        df = pd.read_csv(file_name, dtype=str, encoding="utf-8", on_bad_lines="skip")
    except Exception:
        print(f"Trying fallback encoding for {file_name}")
        try:
            df = pd.read_csv(file_name, dtype=str, encoding="latin1", on_bad_lines="skip", engine="python")
        except Exception as e:
            print(f"Skipping {file_name}: {e}")
            continue

    df["year"] = year
    df = standardize_columns(df)

    for col in target_cols:
        if col not in df.columns:
            df[col] = pd.NA

    pc_total = pd.concat([pc_total[target_cols], df[target_cols]], ignore_index=True)

# Save pcTotal.csv
pc_total.to_csv("pcTotal.csv", index=False)
print("Saved pcTotal.csv")

# Check for columns that are completely null for each year
print("\n--- Column completeness check by year ---")
for year in range(2013, 2025):
    df_year = pc_total[pc_total["year"] == year]
    null_cols = df_year.columns[df_year.isnull().all()]
    if len(null_cols) > 0:
        print(f"Year {year}: All null columns: {list(null_cols)}")
    else:
        print(f"Year {year}: No completely null columns")


# Save pcSub.csv
pc_total[target_cols].to_csv("pcSub.csv", index=False)
print("Saved pcSub.csv")

# Process skaSub.csv
ska_keep_cols = ["NPI", "COMPANY1", "ADDRESS1", "ZIP", "YEAR", "ID", "EXPL3", "EXPL5", "EXPL7", "CODE7", "CODE3"]

try:
    ska = pd.read_csv("ska_2007_2016.csv", usecols=ska_keep_cols, dtype=str, encoding="utf-8", on_bad_lines="skip")
except UnicodeDecodeError:
    print("Retrying ska_2007_2016.csv with latin1 encoding...")
    ska = pd.read_csv("ska_2007_2016.csv", usecols=ska_keep_cols, dtype=str, encoding="latin1", on_bad_lines="skip")

ska.to_csv("skaSub.csv", index=False)
print("Saved skaSub.csv")