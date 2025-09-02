import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
import numpy as np
import os

#Set working directory
#insert your working directory here

def match_ska_irs_company1(ska_path, irs_paths, output_path, name_thresh=0.90, addr_thresh=0.95):
    print("Reading unmatched SKA company1 data...")
    ska = pd.read_csv(ska_path, usecols=["COMPANY1", "ADDRESS1", "ZIP"], dtype=str, encoding="ISO-8859-1")
    ska["zip_prefix"] = ska["ZIP"].astype(str).str[:2]

    print("Reading and combining IRS EO master files...")
    irs = pd.concat([pd.read_csv(f, dtype=str, encoding="ISO-8859-1") for f in irs_paths], ignore_index=True)
    irs = irs.dropna(subset=["NAME", "STREET", "ZIP"])
    irs["zip_prefix"] = irs["ZIP"].astype(str).str[:2]

    ska["BestMatch_Name"] = ""
    ska["Similarity_Name"] = 0.0
    ska["MatchOnName"] = 0

    ska["BestMatch_Address"] = ""
    ska["Similarity_Address"] = 0.0
    ska["MatchOnAddress"] = 0

    for prefix in ska["zip_prefix"].dropna().unique():
        print(f"Processing ZIP prefix {prefix}...")

        ska_sub = ska[ska["zip_prefix"] == prefix].copy()
        irs_sub = irs[irs["zip_prefix"] == prefix].copy()
        if ska_sub.empty or irs_sub.empty:
            continue

        #Name Matching
        name_vectorizer = TfidfVectorizer(lowercase=True, stop_words="english")
        tfidf_irs_names = name_vectorizer.fit_transform(irs_sub["NAME"].fillna(""))
        tfidf_ska_names = name_vectorizer.transform(ska_sub["COMPANY1"].fillna(""))

        nn_name = NearestNeighbors(n_neighbors=1, metric="cosine").fit(tfidf_irs_names)
        dist_name, idx_name = nn_name.kneighbors(tfidf_ska_names)
        sim_name = 1 - dist_name.ravel()
        matched_name = sim_name > name_thresh
        best_name = [irs_sub.iloc[i]["NAME"] if m else "" for i, m in zip(idx_name.ravel(), matched_name)]

        ska.loc[ska_sub.index, "BestMatch_Name"] = best_name
        ska.loc[ska_sub.index, "Similarity_Name"] = sim_name
        ska.loc[ska_sub.index, "MatchOnName"] = matched_name.astype(int)

        #Address Matching
        addr_vectorizer = TfidfVectorizer(lowercase=True, stop_words="english")
        tfidf_irs_addr = addr_vectorizer.fit_transform(irs_sub["STREET"].fillna(""))
        tfidf_ska_addr = addr_vectorizer.transform(ska_sub["ADDRESS1"].fillna(""))

        nn_addr = NearestNeighbors(n_neighbors=1, metric="cosine").fit(tfidf_irs_addr)
        dist_addr, idx_addr = nn_addr.kneighbors(tfidf_ska_addr)
        sim_addr = 1 - dist_addr.ravel()
        matched_addr = sim_addr >= addr_thresh
        best_addr = [irs_sub.iloc[i]["STREET"] if m else "" for i, m in zip(idx_addr.ravel(), matched_addr)]

        ska.loc[ska_sub.index, "BestMatch_Address"] = best_addr
        ska.loc[ska_sub.index, "Similarity_Address"] = sim_addr
        ska.loc[ska_sub.index, "MatchOnAddress"] = matched_addr.astype(int)

    ska["MatchEither"] = np.logical_or(ska["MatchOnName"] == 1, ska["MatchOnAddress"] == 1).astype(int)

    ska.to_csv(output_path, index=False)
    print(f"Saved: {output_path} ({len(ska)} rows)")

#Run
match_ska_irs_company1 (
    ska_path="unmatched_company1_ska_total.csv",
    irs_paths=["eo1.csv", "eo2.csv", "eo3.csv"],
    output_path="matched_company1_ska_irs_name_address.csv",
    name_thresh=0.90,
    addr_thresh=0.95
)