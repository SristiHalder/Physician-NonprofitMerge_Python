import pandas as pd
import os

# Set working directory
#insert your working directory here

# Read SKA and PC datasets with only required columns
ska = pd.read_csv("skaSub.csv", usecols=["ID", "COMPANY1", "YEAR", "NPI", "ADDRESS1", "EXPL7", "CODE7"], dtype=str)
pc = pd.read_csv("pcSub.csv", usecols=[
    "year", "NPI", "Line 1 Street Address", "Zip Code",
    "Claims based hospital affiliation LBN 1", "Claims based hospital affiliation CCN 1"
], dtype=str)

# Filter out missing NPI
ska = ska[ska["NPI"].notna()]
pc = pc[pc["NPI"].notna()]

#Clean hospital names and assign unique PC_ID
pc["clean_name"] = pc["Claims based hospital affiliation LBN 1"].fillna("").str.strip().str.lower()
pc_id_map = pd.DataFrame({"clean_name": pc["clean_name"].unique()})
pc_id_map["PC_ID"] = range(1, len(pc_id_map) + 1)
pc = pc.merge(pc_id_map, on="clean_name", how="left")

# Process each year individually
all_results = []
for year in sorted(ska["YEAR"].dropna().unique()):
    ska_y = ska[(ska["YEAR"] == year) & ska["CODE7"].notna()]
    pc_y = pc[(pc["year"] == year) &
              pc["Claims based hospital affiliation LBN 1"].notna() &
              pc["Claims based hospital affiliation CCN 1"].notna()]

    ska_y = ska_y.drop_duplicates(subset=["CODE7", "NPI", "ADDRESS1"]).rename(columns={"ADDRESS1": "ska_address"})
    pc_y = pc_y.drop_duplicates(subset=[
        "PC_ID", "Claims based hospital affiliation LBN 1",
        "Claims based hospital affiliation CCN 1", "NPI",
        "Line 1 Street Address", "Zip Code"
    ]).rename(columns={"Line 1 Street Address": "pc_address"})

    merged = ska_y.merge(pc_y, on="NPI", how="left")
    merged = merged[merged["PC_ID"].notna()]

    grouped = merged.groupby(["CODE7", "PC_ID"]).agg({
        "ska_address": "first",
        "Claims based hospital affiliation LBN 1": "first",
        "Claims based hospital affiliation CCN 1": "first",
        "pc_address": "first",
        "Zip Code": "first",
        "NPI": "count"
    }).reset_index().rename(columns={"NPI": "shared_npi_count"})

    grouped["year"] = year
    all_results.append(grouped)

# Combine all year-wise results
final_results = pd.concat(all_results, ignore_index=True)

# Keep only rows with >1 shared NPI
final_results = final_results[final_results["shared_npi_count"] > 1]

# Keep the best match per CODE7
best_match = final_results.loc[final_results.groupby("CODE7")["shared_npi_count"].idxmax()]

# Identify unmatched SKA CODE7s
matched_codes = set(best_match["CODE7"])
unmatched_ska = ska[~ska["CODE7"].isin(matched_codes)][["CODE7", "ADDRESS1"]].drop_duplicates()

#Save unmatched SKA records
unmatched_ska.to_csv("shared_npis_all_years_hosp_unmatched_ska.csv", index=False)

#Clean and save best matches
best_match = best_match[
    best_match["Claims based hospital affiliation LBN 1"].notna() &
    best_match["Claims based hospital affiliation LBN 1"].str.strip().ne("")
]
best_match = best_match.sort_values(["CODE7", "shared_npi_count"], ascending=[True, False])
best_match.to_csv("shared_npis_all_years_hosp_best_match.csv", index=False)

#Save collapsed unmatched SKA CODE7 list
unmatched_ska[["CODE7"]].drop_duplicates().to_csv("collapsed_unmatched_hosp_ska_list.csv", index=False)