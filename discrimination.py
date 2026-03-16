import pandas as pd
import numpy as np

# Load data
df = pd.read_csv("HRDataset_v14.csv")

# ----------------------------
# 1) Parse dates
# ----------------------------
df["DateofHire"] = pd.to_datetime(df["DateofHire"], errors="coerce")
df["DateofTermination"] = pd.to_datetime(df["DateofTermination"], errors="coerce")

# For active employees, use a reference date
reference_date = pd.Timestamp("2026-03-16")

# End date = termination date if available, otherwise reference date
df["EndDate"] = df["DateofTermination"].fillna(reference_date)

# Employment duration in months
df["EmploymentMonths"] = ((df["EndDate"] - df["DateofHire"]).dt.days / 30.44).clip(lower=1)

# ----------------------------
# 2) Build Absences per month
# ----------------------------
df["AbsencesPerMonth"] = df["Absences"] / df["EmploymentMonths"]

# ----------------------------
# 3) Normalize features to 0-1
# ----------------------------

# PerfScoreID: 1 (bad) -> 4 (very good)
df["perf_norm"] = (df["PerfScoreID"] - 1) / 3
df["perf_norm"] = df["perf_norm"].clip(0, 1)

# EngagementSurvey: assumed roughly 1 to 5
df["engagement_norm"] = (df["EngagementSurvey"] - 1) / 4
df["engagement_norm"] = df["engagement_norm"].clip(0, 1)

# EmpSatisfaction: 1 to 5
df["satisfaction_norm"] = (df["EmpSatisfaction"] - 1) / 4
df["satisfaction_norm"] = df["satisfaction_norm"].clip(0, 1)

# SpecialProjectsCount: normalize by observed max
projects_max = max(df["SpecialProjectsCount"].max(), 1)
df["projects_norm"] = df["SpecialProjectsCount"] / projects_max
df["projects_norm"] = df["projects_norm"].clip(0, 1)

# AbsencesPerMonth: lower is better
# Use 95th percentile to reduce effect of outliers
absence_cap = max(df["AbsencesPerMonth"].quantile(0.95), 1e-6)
df["absence_bad_norm"] = (df["AbsencesPerMonth"] / absence_cap).clip(0, 1)
df["attendance_norm"] = 1 - df["absence_bad_norm"]

# ----------------------------
# 4) Weighted retention score
# ----------------------------
weights = {
    "perf_norm": 0.35,
    "engagement_norm": 0.25,
    "satisfaction_norm": 0.20,
    "projects_norm": 0.10,
    "attendance_norm": 0.10,
}

df["keep_score"] = (
    weights["perf_norm"] * df["perf_norm"]
    + weights["engagement_norm"] * df["engagement_norm"]
    + weights["satisfaction_norm"] * df["satisfaction_norm"]
    + weights["projects_norm"] * df["projects_norm"]
    + weights["attendance_norm"] * df["attendance_norm"]
)

# ----------------------------
# 5) Convert score to 0/1
# ----------------------------
# Threshold can be tuned
threshold = 0.60
df["would_keep"] = (df["keep_score"] >= threshold).astype(int)

# ----------------------------
# 6) Show result
# ----------------------------
cols_to_show = [
    "Employee_Name",
    "PerfScoreID",
    "EngagementSurvey",
    "EmpSatisfaction",
    "SpecialProjectsCount",
    "Absences",
    "EmploymentMonths",
    "AbsencesPerMonth",
    "keep_score",
    "would_keep",
]

print(df[cols_to_show].head(10))

# Optional: save
df.to_csv("HR_with_keep_score.csv", index=False)