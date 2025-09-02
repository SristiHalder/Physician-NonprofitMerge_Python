import pandas as pd
import os

#Set your working directory
#insert your working directory here

#Step 1: Build crosswalk from PC2021
pc2021 = pd.read_csv("PC2021.csv", dtype=str, encoding='latin1')
crosswalk = pc2021[[" hosp_afl_1", " hosp_afl_lbn_1"]].drop_duplicates()
crosswalk.columns = ["facility_ccn", "facility_lbn"]
print("Crosswalk ready")

#Step 2: Merge Facility Affiliation NPI–CCN with crosswalk and update PC files
def update_pc_file_with_affil(year, ccn_colname, affil_file, pc_file):
    affil = pd.read_csv(affil_file, dtype=str, encoding='latin1')
    affil = affil.rename(columns={ccn_colname: "facility_ccn"})

    # Merge affiliation CCNs with LBNs
    affil = affil.merge(crosswalk, how="left", on="facility_ccn")
    affil_subset = affil[["NPI", "facility_ccn", "facility_lbn"]].rename(columns={
        "facility_ccn": "hosp_afl_1",
        "facility_lbn": "hosp_afl_lbn_1"
    })

    # Load existing PC file and merge
    pc = pd.read_csv(pc_file, dtype=str, encoding='latin1')
    updated = pc.drop(columns=["hosp_afl_1", "hosp_afl_lbn_1"], errors="ignore")  # Drop if exists
    updated = updated.merge(affil_subset, how="left", on="NPI")

    updated.to_csv(pc_file, index=False)

#Run for each year
update_pc_file_with_affil(2022, "facility_afl_ccn", "Facility_Affiliation2022.csv", "PC2022.csv")
update_pc_file_with_affil(2023, "Facility Affiliations Certification Number", "Facility_Affiliation2023.csv", "PC2023.csv")
update_pc_file_with_affil(2024, "Facility Affiliations Certification Number", "Facility_Affiliation2024.csv", "PC2024.csv")

print("PC2022, PC2023 and PC2024 is updated.")
