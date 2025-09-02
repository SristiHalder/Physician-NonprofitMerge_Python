import pandas as pd
import os
import re
import gc

# === Set working directory ===
#insert your working directory here

#Helper Functions
def is_po_box(address):
    if pd.isna(address):
        return False
    address = address.upper()
    patterns = [
        r"\bP\.?\s*O\.?\s*BOX\b",
        r"\bPOST\s+OFFICE\s+BOX\b",
        r"\bBOX\s+\d+",
        r"\bP\s*O\s+\d+",
        r"\bP\.?\s*O\.?\s+\d+"
    ]
    return any(re.search(pattern, address) for pattern in patterns)

def has_religious_word(name):
    if pd.isna(name):
        return False
    name = name.upper()
    return any(word in name for word in ["CHURCH", "MINISTRIES"])

#Filter matched_hosp_with_irs_name_and_address.csv
print("Filtering: matched_hosp_with_irs_name_and_address.csv")
hosp_df = pd.read_csv("matched_hosp_with_irs_name_and_address.csv", dtype=str)
hosp_df["Similarity_Name"] = pd.to_numeric(hosp_df["Similarity_Name"], errors="coerce")
hosp_df["Similarity_Address"] = pd.to_numeric(hosp_df["Similarity_Address"], errors="coerce")
hosp_df["is_po_box"] = hosp_df["BestMatch_Address"].apply(is_po_box)

filtered_hosp = hosp_df[
    (
        (hosp_df["Similarity_Name"] >= 0.85) |
        (hosp_df["Similarity_Address"] >= 0.95)
    ) & (~hosp_df["is_po_box"])
].copy()

print(f"Filtered matched_hosp → {len(filtered_hosp)} rows retained")

del hosp_df
gc.collect()

#Filter matched_pgp_ska_irs_name_address.csv
print("Filtering: matched_pgp_ska_irs_name_address.csv")
pgp_df = pd.read_csv("matched_pgp_ska_irs_name_address.csv", dtype=str)
pgp_df["Similarity_Name"] = pd.to_numeric(pgp_df["Similarity_Name"], errors="coerce")
pgp_df["Similarity_Address"] = pd.to_numeric(pgp_df["Similarity_Address"], errors="coerce")
pgp_df["has_religious_word"] = pgp_df["BestMatch_Name"].apply(has_religious_word)
pgp_df["is_po_box"] = pgp_df["BestMatch_Address"].apply(is_po_box)

filtered_pgp = pgp_df[
    (
        (pgp_df["Similarity_Name"] > 0.90) |
        (pgp_df["Similarity_Address"] >= 0.95)
    ) & (~pgp_df["has_religious_word"]) & (~pgp_df["is_po_box"])
].copy()

print(f"Filtered matched_pgp → {len(filtered_pgp)} rows retained")

del pgp_df
gc.collect()

#Filter matched_company1_ska_irs_name_address.csv
print("Filtering: matched_company1_ska_irs_name_address.csv")
company_df = pd.read_csv("matched_company1_ska_irs_name_address.csv", dtype=str)
company_df["Similarity_Address"] = pd.to_numeric(company_df["Similarity_Address"], errors="coerce")
company_df["is_po_box"] = company_df["BestMatch_Address"].apply(is_po_box)

filtered_company = company_df[
    (company_df["Similarity_Address"] >= 0.95) & (~company_df["is_po_box"])
].copy()

print(f"Filtered matched_company1 → {len(filtered_company)} rows retained")

del company_df
gc.collect()

#Save Cleaned Outputs
filtered_hosp.to_csv("cleaned_matched_hosp.csv", index=False)
filtered_pgp.to_csv("cleaned_matched_pgp.csv", index=False)
filtered_company.to_csv("cleaned_matched_company1.csv", index=False)

print("Saved:")
print(" - cleaned_matched_hosp.csv")
print(" - cleaned_matched_pgp.csv")
print(" - cleaned_matched_company1.csv")
