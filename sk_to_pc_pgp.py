import pandas as pd
import os

# Set working directory
#insert your working directory here


# Read SKA and PC files
ska = pd.read_csv("skaSub.csv", usecols=["ID", "COMPANY1", "YEAR", "NPI", "ADDRESS1", "CODE3", "EXPL3"], dtype=str)
pc = pd.read_csv("pcSub.csv", usecols=["Organization legal name", "year", "NPI", "Line 1 Street Address", "Zip Code"], dtype=str)

# Filter for non-missing NPIs
ska = ska[ska["NPI"].notna()]
pc = pc[pc["NPI"].notna()]

# Clean organization names and assign PC_ID
pc["clean_name"] = pc["Organization legal name"].fillna("").str.strip().str.lower()
pc_id_map = pd.DataFrame({"clean_name": pc["clean_name"].unique()})
pc_id_map["PC_ID"] = range(1, len(pc_id_map) + 1)
pc = pc.merge(pc_id_map, on="clean_name", how="left")

### -----------------------------------
### Part 1: CODE3 → Organization match
### -----------------------------------
all_results_pgp = []
for year in ska["YEAR"].dropna().unique():
    ska_y = ska[(ska["YEAR"] == year) & ska["CODE3"].notna()]
    pc_y = pc[(pc["year"] == year) & pc["Organization legal name"].notna()]

    ska_y = ska_y.drop_duplicates(subset=["CODE3", "NPI", "ADDRESS1"]).rename(columns={"ADDRESS1": "ska_address"})
    pc_y = pc_y.drop_duplicates(subset=["PC_ID", "Organization legal name", "NPI", "Line 1 Street Address", "Zip Code"]).rename(
        columns={"Line 1 Street Address": "pc_address"})

    merged = ska_y.merge(pc_y, on="NPI", how="left")
    merged = merged[merged["PC_ID"].notna()]

    grouped = merged.groupby(["CODE3", "PC_ID"]).agg({
        "ska_address": "first",
        "Organization legal name": "first",
        "pc_address": "first",
        "Zip Code": "first",
        "NPI": "count"
    }).reset_index().rename(columns={"NPI": "shared_npi_count"})

    grouped["year"] = year
    all_results_pgp.append(grouped)

# Finalize matches
final_pgp = pd.concat(all_results_pgp)
final_pgp = final_pgp[final_pgp["shared_npi_count"] > 1]
best_pgp = final_pgp.loc[final_pgp.groupby("CODE3")["shared_npi_count"].idxmax()]

# Save results
matched_codes_pgp = set(best_pgp["CODE3"])
unmatched_pgp = ska[~ska["CODE3"].isin(matched_codes_pgp)][["CODE3", "ADDRESS1"]].drop_duplicates()
best_pgp.to_csv("shared_npis_all_years_pgp_best_match.csv", index=False)
unmatched_pgp.to_csv("shared_npis_all_years_pgp_unmatched_ska.csv", index=False)
unmatched_pgp[["CODE3"]].drop_duplicates().to_csv("collapsed_unmatched_pgp_ska_list.csv", index=False)

### ---------------------------------------
### Part 2: COMPANY1 → Organization match
### ---------------------------------------
all_results_company = []
for year in ska["YEAR"].dropna().unique():
    ska_y = ska[(ska["YEAR"] == year) & ska["COMPANY1"].notna()]
    pc_y = pc[(pc["year"] == year) & pc["Organization legal name"].notna()]

    ska_y = ska_y.drop_duplicates(subset=["COMPANY1", "NPI", "ADDRESS1"]).rename(columns={"ADDRESS1": "ska_address"})
    pc_y = pc_y.drop_duplicates(subset=["PC_ID", "Organization legal name", "NPI", "Line 1 Street Address", "Zip Code"]).rename(
        columns={"Line 1 Street Address": "pc_address"})

    merged = ska_y.merge(pc_y, on="NPI", how="left")
    merged = merged[merged["PC_ID"].notna()]

    grouped = merged.groupby(["COMPANY1", "PC_ID"]).agg({
        "ska_address": "first",
        "Organization legal name": "first",
        "pc_address": "first",
        "Zip Code": "first",
        "NPI": "count"
    }).reset_index().rename(columns={"NPI": "shared_npi_count"})

    grouped["year"] = year
    all_results_company.append(grouped)

# Finalize matches
final_company = pd.concat(all_results_company)
final_company = final_company[final_company["shared_npi_count"] > 1]
best_company = final_company.loc[final_company.groupby("COMPANY1")["shared_npi_count"].idxmax()]

# Save results
matched_company = set(best_company["COMPANY1"])
unmatched_company = ska[~ska["COMPANY1"].isin(matched_company)][["COMPANY1", "ADDRESS1"]].drop_duplicates()
best_company.to_csv("shared_npis_all_years_company1_best_match.csv", index=False)
unmatched_company.to_csv("shared_npis_all_years_company1_unmatched_ska.csv", index=False)
unmatched_company[["COMPANY1"]].drop_duplicates().to_csv("collapsed_unmatched_company1_ska_list.csv", index=False)