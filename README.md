# Physician Loan Project – Data Integration & Nonprofit Tagging

This repository documents the physician loan data integration and nonprofit-tagging workflow completed in Summer 2025. It was conducted as part of a larger **University of Pennsylvania health services research project** examining how physician debt, nonprofit employment, and institutional affiliations interact with physician labor market outcomes.  

**Important:** This codebase is **not intended to be fully replicable** without the original proprietary data files and directory structure. It is shared here as a **reference framework** for others learning to clean, harmonize, and link multi-source healthcare datasets.

---

## Project Overview

- **Focus:** Link and enrich multi-year Physician Compare (PC) and SKA data; infer hospital/organization ties; apply nonprofit flags using IRS EO files.  
- **Contribution to larger research:** These scripts created harmonized PC and SKA datasets, flagged nonprofit affiliations, and merged them to physician-level identifiers. This pipeline was a **foundational step** that enabled subsequent econometric analysis of how **loan burden and nonprofit employment** shape physicians’ specialty choices and career trajectories.  
- **Intended use here:** A pedagogical example of data engineering and entity resolution in health services research—**not** a turnkey pipeline.  

---

## What this does (at a glance)

1. Builds a CCN↔LBN crosswalk from PC2021.  
2. Updates PC 2022–2024 with hospital affiliation CCNs/LBNs.  
3. Standardizes & stacks PC 2013–2024 into `pcTotal.csv`.  
4. Creates an SKA subset (`skaSub.csv`).  
5. Matches SKA ↔ PC by shared NPIs; exports best matches and unmatched.  
6. Fuzzy-matches unmatched SKA entities to IRS EO (TF-IDF + nearest neighbors).  
7. Filters false positives (PO boxes, religious terms, low similarity).  
8. Assigns nonprofit flags and merges them to doctor-level outputs for downstream analysis.  

---

## Workflow & Scripts

> Paths in the scripts point to a local working directory
> Update `os.chdir(...)` to your environment. Some files require specific encodings (`utf-8`, `latin1`, `ISO-8859-1`).

### 0) Facility Affiliation: CCN↔LBN Crosswalk & PC Updates
- Build crosswalk from **PC2021.csv**; update **PC2022–PC2024** with standardized CCN/LBN.

### 1) Standardize & Stack PC; Create SKA Subset
- Outputs: `pcTotal.csv`, `pcSub.csv`, `skaSub.csv`.

### 2) SKA↔PC Matching by Shared NPIs
- `compareData_append.py`: hospital (CODE7).  
- `sk_to_pc_hosp.py`: PGP (CODE3) and COMPANY1.  

### 3) Prepare Full Unmatched for Fuzzy Matching
- `sk_to_pc_pgp.py`: exports unmatched SKA rows per key.

### 4) Fuzzy Match to IRS EO Files
- `ska_fixing.py`: hospitals.  
- `ska_irs_hosp.py`: PGP.  
- `ska_irs_pgp.py`: COMPANY1.  

### 5) Filter & Clean Matches
- `ska_irs_company1.py`: filters out PO boxes, religious terms, and low-sim matches.  
  - Outputs: `cleaned_matched_hosp.csv`, `cleaned_matched_pgp.csv`, `cleaned_matched_company1.csv`.

### 6) Apply Nonprofit Flags & Merge to Doctors
- `cleaned_hosp_pgp_company1.py`: tags PC & SKA with nonprofit flags.  
- `pc+ska_nonprofit.py`: merges nonprofit tags into **doctor-level file**.  

---

## Inputs & Outputs (illustrative)

**Inputs (examples):**  
- `PC2013.csv … PC2024.csv`, `PC2021.csv`  
- `Facility_AffiliationYYYY.csv`  
- `ska_2007_2016.csv`  
- `eo1.csv`, `eo2.csv`, `eo3.csv` (IRS EO)  
- `doctors_clean.csv`

**Key outputs:**  
- `pcTotal.csv`, `pcSub.csv`, `skaSub.csv`  
- `shared_npis_all_years_*_best_match.csv`, `_unmatched_*.csv`  
- `unmatched_*_ska_total.csv`, `matched_*_name_and_address.csv`  
- `cleaned_matched_*.csv`  
- `pcTotal_with_nonprofit_flags.csv`, `skaSub_with_nonprofit_flags.csv`  
- `doctors_clean_with_nonprofit_flags.csv`

---

## Environment & Dependencies

- Python 3.9+  
- `pandas`, `numpy`, `scikit-learn`  
- Mixed encodings (`utf-8`, `latin1`, `ISO-8859-1`) handled within scripts.  

---

## Reproducibility & Data Access

This work depends on **restricted datasets** (e.g., SKA, PC, IRS EO extracts).  
- Update `os.chdir(...)` to your environment.  
- Supply analogs of PC/SKA/IRS EO files with equivalent schemas.  
- Results will differ based on dataset vintages and upstream processing.  

---

## Educational Use

This repository demonstrates practical steps for:
- Harmonizing multi-year files with changing schemas  
- Robust CSV ingestion with encoding fallbacks  
- Deterministic entity linking via **NPI**  
- Fuzzy matching of organizations (TF-IDF + cosine similarity)  
- Conservative filtering and quality control  
- Rolling entity flags up to **doctor-level data**  

---

## Acknowledgments & Context

This pipeline was developed as part of a **University of Pennsylvania health services research project** investigating the relationship between **physician debt and nonprofit employment**. By constructing a robust entity-linkage framework across PC, SKA, and IRS EO datasets, this work provided the **data foundation** for econometric analyses of physician labor markets.  

The process of cleaning, linking, and tagging was itself a valuable contribution: it not only supported the main study but also generated reusable workflows for **future research at the intersection of healthcare, labor economics, and organizational behavior**.  

Any errors or opinions here are the author’s alone. This repository does **not** imply endorsement by UPenn or affiliated units.
