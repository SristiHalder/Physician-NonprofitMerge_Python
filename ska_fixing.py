import pandas as pd
import os

# Set working directory
#insert your working directory here


#Load Unmatched Code Lists
unmatched_code7 = pd.read_csv("collapsed_unmatched_hosp_ska_list.csv", header=None, names=["CODE7"], dtype=str)
unmatched_code3 = pd.read_csv("collapsed_unmatched_pgp_ska_list.csv", header=None, names=["CODE3"], dtype=str)
unmatched_company1 = pd.read_csv("collapsed_unmatched_company1_ska_list.csv", header=None, names=["COMPANY1"], dtype=str)

# Clean strings
unmatched_code7["CODE7"] = unmatched_code7["CODE7"].str.strip()
unmatched_code3["CODE3"] = unmatched_code3["CODE3"].str.strip()
unmatched_company1["COMPANY1"] = unmatched_company1["COMPANY1"].str.strip().str.lower()

#Load SKA File
ska = pd.read_csv("skaSub.csv", dtype=str)
ska["CODE7"] = ska["CODE7"].str.strip()
ska["CODE3"] = ska["CODE3"].str.strip()
ska["COMPANY1"] = ska["COMPANY1"].str.strip().str.lower()

#Filter
filtered_code7 = ska[ska["CODE7"].isin(unmatched_code7["CODE7"])]
filtered_code3 = ska[ska["CODE3"].isin(unmatched_code3["CODE3"])]
filtered_company1 = ska[ska["COMPANY1"].isin(unmatched_company1["COMPANY1"])]

#Save Individual Outputs
filtered_code7.to_csv("unmatched_code7_ska_total.csv", index=False)
filtered_code3.to_csv("unmatched_code3_ska_total.csv", index=False)
filtered_company1.to_csv("unmatched_company1_ska_total.csv", index=False)

print(f"Saved: unmatched_code7_ska_total.csv with {len(filtered_code7)} rows")
print(f"Saved: unmatched_code3_ska_total.csv with {len(filtered_code3)} rows")
print(f"Saved: unmatched_company1_ska_total.csv with {len(filtered_company1)} rows")

#Combine and Save Master File
combined = pd.concat([filtered_code7, filtered_code3, filtered_company1], ignore_index=True)
combined = combined.drop_duplicates(subset=["ID", "NPI", "COMPANY1", "ADDRESS1"])
combined.to_csv("unmatched_ska_total.csv", index=False)
print(f"Saved: unmatched_ska_total.csv with {len(combined)} rows")