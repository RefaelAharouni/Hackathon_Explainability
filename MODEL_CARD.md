# Model Card: HR Explainability AI (Group 29)

**Project:** Hackathon Explainability AI  
**Notebook Reference:** `cc/Hackathon_Explainability_AI_Groupe_29.ipynb`  
**App Reference:** `cc/app.py`  
**Date:** 17 March 2026  
**Status:** Prototype complete (preprocessing + scoring + XGBoost + Streamlit demo)

---

## 1) Model objective

This project provides an HR decision-support pipeline with two complementary goals:

1. **Retention priority scoring** (`keep_score` and `would_keep`) based on structured employee indicators.
2. **Explainability support** through textual employee context (`textInformation`) and optional local LLM generation in the app.

The system is explicitly positioned as **decision support**, not autonomous HR decision-making.

---

## 2) Data and preprocessing (as implemented in `cc` notebook)

### 2.1 Data sources
- Primary dataset: `HRDataset_v14.csv`.
- Supplementary attrition dataset loaded as `attrition.csv`, schema-aligned and concatenated.

### 2.2 Key preprocessing actions actually present in the notebook

- Column mapping between datasets (`mapping_cols`) and target harmonization (`Termd`).
- Merge + row reindexing (`EmpID`).
- Compensation normalization: `Salary = Salary + Bonus` (with missing bonus filled to 0).
- `PerfScoreID` remapping for values originally on 5-point scale.
- Missing-value treatment for selected operational columns (`StressLevelScore`, `WorkHoursPerWeek`, `TrainingHours`, `YearsInCurrentRole`) via medians.
- Manager ID fill from manager name dictionary.
- Text target consolidation:
  - `TermReason` cleaned (`N/A-StillEmployed` → empty)
  - merged with `RetentionRisk` into `Reasons`
  - original columns dropped.
- Qualitative cleaning pipeline (HTML tags/entities, emojis/smileys, whitespace normalization).
- Salary outlier smoothing via `LogSalary = log(Salary)`.

### 2.3 Removed features in the current `cc` notebook

The notebook removes a broader set than earlier versions, including:
- Protected or sensitive proxies: `MarriedID`, `MaritalStatusID`, `GenderID`, `Sex`, `MaritalDesc`, `CitizenDesc`, `HispanicLatino`, `RaceDesc`, `DiversityCategory`, `DOB`, `DateOfBirth`.
- Low-value / redundant / sparse fields: `FromDiversityJobFairID`, `RecruitmentSource`, `YearsSinceLastTraining`, `PerformanceScore`, `DeptID`, `EmpStatusID`, `PositionID`, `Employee_Name`, `State`, `Zip`, `LastPerformanceReview_Date`, `DaysLateLast30`, `LastPromotionDate`.
- Date columns explicitly dropped in this version: `DateofHire`, `DateofTermination`.

### 2.4 Engineered features currently produced
- `keep_score` (continuous in [0,1])
- `would_keep` (binary thresholded at 0.60)
- `textInformation` (narrative context per employee)
- `LogSalary`
- `Reasons` (merged textual reason field)

---

## 3) Retention scoring model (`keep_score`)

### 3.1 Features used by the scoring function
The implemented function `add_keep_score` uses:
- `PerfScoreID`
- `EngagementSurvey`
- `EmpSatisfaction`
- `SpecialProjectsCount`
- `SkillsAssessmentScore`
- `StressLevelScore`
- `Absences`
- `YearsAtCompany` (for absence-rate normalization)

### 3.2 Current weight configuration (from notebook)
```python
DEFAULT_WEIGHTS = {
  "perf_norm": 0.30,
  "engagement_norm": 0.15,
  "satisfaction_norm": 0.15,
  "projects_norm": 0.10,
  "skills_norm": 0.15,
  "stress_bad_norm": -0.05,
  "absence_bad_norm": -0.10,
}
```

### 3.3 Important implementation detail
Absence intensity is normalized as:
- `EmploymentMonths = max(YearsAtCompany * 12, 1)`
- `AbsencesPerMonth = Absences / EmploymentMonths`
- capped by the 95th percentile for robust scaling.

Intermediate normalized columns are dropped after final score computation.

---

## 4) Supervised model in section 2 (XGBoost)

The notebook trains an XGBoost classifier on **departed employees only** (`Termd == 1`) using target `would_keep`.

### 4.1 Training setup (as coded)
- Split: `train_test_split(..., test_size=0.2, random_state=42)`
- Model family: `xgb.XGBClassifier`
- Hyperparameter tuning: `GridSearchCV(cv=5, scoring='accuracy', n_jobs=-1)`
- Candidate feature set:
  - `Salary`, `EngagementSurvey`, `EmpSatisfaction`, `Absences`,
  - `WorkHoursPerWeek`, `StressLevelScore`, `SkillsAssessmentScore`, `ProjectsAssigned`

### 4.2 Saved artifacts
- `best_xgb_model.pkl`
- `final_hr_data.csv`

⚠️ **Note on metrics:** performance values (confusion matrix / classification report) depend on runtime data state and should be copied from the executed notebook output for final reporting.

---

## 5) App behavior (`cc/app.py`)

The Streamlit app:
- loads `best_xgb_model.pkl` and `final_hr_data.csv`,
- visualizes retention-risk scatter plots,
- shows individual employee cards,
- optionally generates explanation text via local LLM pipeline (demo fallback if LLM not loaded),
- flags mismatch situations (`would_keep` vs `Termd`).

This app is currently a **prototype UI** and not production-hardened.

---

## 6) Known limitations

1. **Target design coupling:** XGBoost predicts `would_keep`, which is itself derived from a rule-based score; this may replicate scoring logic rather than learn independent ground truth.
2. **Selection bias:** supervised model is trained on `Termd == 1` subset only.
3. **Data heterogeneity after merge:** source datasets may have different collection standards.
4. **Explainability scope:** narrative generation and optional LLM explanation are informative but not formal causal explanations.
5. **Prototype lifecycle:** no end-to-end MLOps controls yet (versioned pipelines, CI validation, strict model registry).

---

## 7) Cybersecurity & robustness (conference-aligned, theoretical roadmap)

Aligned to the conference framework (**confidentiality, integrity, availability**, plus AI-specific threats).

### 7.1 Current prototype posture
- Local/offline orientation (`TRANSFORMERS_OFFLINE=1`) reduces external API leakage risk.
- However, there is currently no built-in authentication/RBAC in `app.py`.
- Model/data artifacts are loaded directly from local disk with no signature verification.

### 7.2 High-priority improvements for later implementation

#### A) Confidentiality controls
- Encrypt `final_hr_data.csv` and model artifacts at rest.
- Separate raw HR data from serving directory.
- Minimize personally identifying fields in UI views.

#### B) Integrity controls
- Add hash/signature checks before loading `best_xgb_model.pkl` and local LLM weights.
- Enforce approved artifact versions only (model registry or signed manifest).

#### C) Availability / resilience
- Add robust exception handling, timeout guards, and safe fallback mode.
- Add controlled resource limits for local LLM generation.

#### D) Access control and auditability
- Add authentication and role-based authorization in Streamlit.
- Log inference usage (user, timestamp, model version, action) with immutable audit trail.

#### E) AI-specific threat mitigation
- **Data poisoning:** controlled retraining inputs + provenance checks.
- **Model extraction:** query throttling and output minimization if exposed via API.
- **Prompt injection:** strict prompt templates + sanitization of untrusted text segments.

#### F) Supply-chain hardening
- Pin dependencies, avoid ad-hoc runtime `pip install` in production environment.
- Maintain vulnerability scanning of Python packages and model dependencies.

### 7.3 Governance / compliance direction
For real deployment, align controls and documentation with:
- EU AI Act (risk management, traceability, human oversight),
- GDPR (data minimization, purpose limitation, rights),
- NIS2 / resilience principles,
- NIST AI RMF / OWASP AI risk practices.

---

## 8) What is implemented vs. planned

### Implemented now
- Data merge and heavy preprocessing
- Fairness-oriented feature removal
- Rule-based retention scoring (`keep_score`, `would_keep`)
- Narrative context generation (`textInformation`)
- XGBoost training + artifact export
- Streamlit prototype interface

### Planned / theoretical improvements
- Production security controls (auth, encryption, integrity verification, audit logging)
- Formalized model governance and risk monitoring
- Stronger LLM safety controls for prompt injection and output policy
- Deployment-grade MLOps and CI/CD checks

---

## 9) References
- Notebook: `cc/Hackathon_Explainability_AI_Groupe_29.ipynb`
- App: `cc/app.py`
- Conference guidance: `Conference_AI_CYBER_Hackathon_Esilv_x_Capgemini.txt`

---

**Last updated:** 17 March 2026  
**Model card status:** Synchronized with current `cc` implementation and theoretical cyber roadmap
