import pandas as pd
import os

# === Set working directory ===
#insert your working directory here

# === Load doctors file ===
doctors = pd.read_csv("doctors_clean.csv", dtype=str)

# === Load PC file and check for relevant columns ===
pc = pd.read_csv("pcTotal_with_nonprofit_flags.csv", dtype=str)
pc_expected = ["nonprofit_hosp", "nonprofit_pgp"]
pc_present = [col for col in pc_expected if col in pc.columns]

# === Load SKA file and check for relevant columns ===
ska = pd.read_csv("skaSub_with_nonprofit_flags.csv", dtype=str)
ska_expected = ["nonprofit_hosp", "nonprofit_pgp", "nonprofit_company1"]
ska_present = [col for col in ska_expected if col in ska.columns]

# === If no flag columns exist, stop the script ===
if not pc_present and not ska_present:
    raise ValueError("None of the nonprofit flag columns exist in PC or SKA. Nothing to merge.")

# === Process PC flags if present ===
if pc_present:
    pc_flags = pc[["NPI"] + pc_present].dropna(subset=["NPI"])
    for col in pc_present:
        pc_flags[col] = pc_flags[col].astype(int)
    pc_flags = pc_flags.groupby("NPI", as_index=False).max()
    rename_pc = {col: f"{col}_pc" for col in pc_present}
    pc_flags = pc_flags.rename(columns=rename_pc)
    doctors = doctors.merge(pc_flags, on="NPI", how="left")

# === Process SKA flags if present ===
if ska_present:
    ska_flags = ska[["NPI"] + ska_present].dropna(subset=["NPI"])
    for col in ska_present:
        ska_flags[col] = ska_flags[col].astype(int)
    ska_flags = ska_flags.groupby("NPI", as_index=False).max()
    rename_ska = {col: f"{col}_ska" for col in ska_present}
    ska_flags = ska_flags.rename(columns=rename_ska)
    doctors = doctors.merge(ska_flags, on="NPI", how="left")

# === Fill NaNs for any flag columns added ===
all_flag_cols = [f"{col}_pc" for col in pc_present] + [f"{col}_ska" for col in ska_present]
for col in all_flag_cols:
    doctors[col] = doctors[col].fillna(0).astype(int)

# === Final check: Are there any non-zero flags? ===
nonprofit_cols = [col for col in doctors.columns if col.startswith("nonprofit_")]
row_flag_sums = doctors[nonprofit_cols].sum(axis=1)
non_zero_rows = (row_flag_sums > 0).sum()

if non_zero_rows == 0:
    print("All nonprofit flag columns are 0 for all doctors. Something may be wrong.")
else:
    print(f"Nonprofit flags assigned correctly: {non_zero_rows} rows have at least one flag = 1.")

# === Save the final output ===
doctors.to_csv("doctors_clean_with_nonprofit_flags.csv", index=False)
print("Saved: doctors_clean_with_nonprofit_flags.csv")
