import os
import pandas as pd

#Set wd
#insert your working directory here

#Load PC & SKA
pcTotal = pd.read_csv("pcTotal.csv", dtype=str)
skaSub = pd.read_csv("skaSub.csv", dtype=str)

#Load Crosswalk files for SKA tagging
shared_hosp = pd.read_csv("shared_npis_all_years_hosp_best_match.csv", dtype=str)
shared_pgp = pd.read_csv("shared_npis_all_years_pgp_best_match.csv", dtype=str)
shared_company1 = pd.read_csv("shared_npis_all_years_company1_best_match.csv", dtype=str)

matched_hosp = pd.read_csv("cleaned_matched_hosp.csv", dtype=str)
matched_pgp = pd.read_csv("cleaned_matched_pgp.csv", dtype=str)
matched_company1 = pd.read_csv("cleaned_matched_company1.csv", dtype=str)

#Load IRS datasets
eo1 = pd.read_csv("eo1.csv", dtype=str)
eo2 = pd.read_csv("eo2.csv", dtype=str)
eo3 = pd.read_csv("eo3.csv", dtype=str)
irs_names = set(pd.concat([eo1["NAME"], eo2["NAME"], eo3["NAME"]], ignore_index=True).dropna().str.upper())

#PC TAGGING
pcTotal["nonprofit_hosp"] = pcTotal["Claims based hospital affiliation LBN 1"].str.upper().isin(irs_names).astype(int)
pcTotal["nonprofit_pgp"] = pcTotal["Organization legal name"].str.upper().isin(irs_names).astype(int)

#SKA TAGGING

#HOSPITAL (CODE7/EXPL7/ADDRESS1)
shared_hosp["nonprofit_hosp"] = shared_hosp["Claims based hospital affiliation LBN 1"].str.upper().isin(irs_names).astype(int)
code7_to_nonprofit = dict(zip(shared_hosp["CODE7"], shared_hosp["nonprofit_hosp"]))
nonprofit_hosp_expl7 = set(matched_hosp["EXPL7"].dropna().str.upper())
nonprofit_hosp_addresses = set(matched_hosp["ADDRESS1"].dropna().str.upper())

skaSub["nonprofit_hosp"] = (
    skaSub["CODE7"].map(code7_to_nonprofit).eq(1).astype(int) |
    skaSub["EXPL7"].str.upper().isin(nonprofit_hosp_expl7) |
    skaSub["ADDRESS1"].str.upper().isin(nonprofit_hosp_addresses)
).astype(int)

#PGP (CODE3/EXPL3)
shared_pgp["nonprofit_pgp"] = shared_pgp["Organization legal name"].str.upper().isin(irs_names).astype(int)
code3_to_nonprofit = dict(zip(shared_pgp["CODE3"], shared_pgp["nonprofit_pgp"]))
nonprofit_pgp_expl3 = set(matched_pgp["EXPL3"].dropna().str.upper())

skaSub["nonprofit_pgp"] = (
    skaSub["CODE3"].map(code3_to_nonprofit).eq(1).astype(int) |
    skaSub["EXPL3"].str.upper().isin(nonprofit_pgp_expl3)
).astype(int)

#COMPANY1 (COMPANY1/ADDRESS1)
shared_company1["nonprofit_company1"] = shared_company1["Organization legal name"].str.upper().isin(irs_names).astype(int)
company1_to_nonprofit = dict(zip(shared_company1["COMPANY1"], shared_company1["nonprofit_company1"]))
nonprofit_company1_names = set(matched_company1["BestMatch_Name"].dropna().str.upper())
nonprofit_company1_addresses = set(matched_company1["BestMatch_Address"].dropna().str.upper())

skaSub["nonprofit_company1"] = (
    skaSub["COMPANY1"].map(company1_to_nonprofit).eq(1).astype(int) |
    skaSub["COMPANY1"].str.upper().isin(nonprofit_company1_names) |
    skaSub["ADDRESS1"].str.upper().isin(nonprofit_company1_addresses)
).astype(int)

#Save outputs
pcTotal.to_csv("pcTotal_with_nonprofit_flags.csv", index=False)
skaSub.to_csv("skaSub_with_nonprofit_flags.csv", index=False)

print("Saved:")
print("pcTotal_with_nonprofit_flags.csv")
print("skaSub_with_nonprofit_flags.csv")
