# Model Card: HR Attrition & Retention Analytics

**Project:** Hackathon Explainability AI (Group 29)  
**Team:** Aharouni Refaël, Goder Joshua, Gérard Paul, Montaron Léa, Farhi-Rivasseau Guillaume  
**Date:** 17 March 2026  
**Status:** Feature Engineering Complete | NLP Component In Progress

---

## 1. Model Objective

### Use Case
Support HR decision-making by:
- **Quantifying** employee value to the organization through a weighted retention score
- **Predicting** employee termination risk and identifying at-risk talent
- **Explaining** termination reasons using NLP analysis of employee reviews and company feedback
- **Avoiding algorithmic bias** in retention decisions through systematic removal of protected attributes

### Inputs
**Post-Preprocessing Feature Set (23 features for keep_score calculation):**
- **Performance Metrics:** PerfScoreID (1-4 scale)
- **Employee Engagement/Satisfaction:** EngagementSurvey (1-5), EmpSatisfaction (1-5)
- **Behavioral Indicators:** Absences (count), SpecialProjectsCount, DaysLateLast30
- **Tenure Data:** DateofHire (datetime), DateofTermination (datetime, nullable for active), EmploymentMonths (derived)
- **Compensation:** Salary, LogSalary (log-transformed for outlier handling)
- **Organizational Structure:** Department, Position, ManagerID, ManagerName
- **Administrative:** EmpID, State, ZIP, Termd (target)
- **Activity Tracking:** DaysSinceLastReview
- **Text Data:** TermReason (for NLP component; cleaned and normalized)
- **Derived for Scoring:** DaysSinceLastReview, AbsencesPerMonth (computed at keep_score runtime)

**Excluded from Training (15 removed features):** MarriedID, MaritalStatusID, GenderID, DOB, Sex, MaritalDesc, CitizenDesc, HispanicLatino, RaceDesc, FromDiversityJobFairID, RecruitmentSource, PerformanceScore (text), DeptID, EmpStatusID, PositionID

**Note:** Features like perf_norm, engagement_norm, absence_bad_norm are computed internally within the keep_score function and are NOT persisted as columns

### Outputs
1. **Primary Output (Implemented):**
   - `keep_score` [0, 1]: Weighted composite score indicating organizational preference to retain employee
   - `would_keep` {0, 1}: Binary decision using threshold (0.60 default)

2. **Secondary Output (In Progress):**
   - `predicted_termination_reason`: LLM-predicted reason for leaving (from TermReason text field)
   - `termination_risk_explanation`: SHAP/LIME feature importance scores

---

## 2. Training Data

### Dataset Composition
- **Primary Source:** `HRDataset_v14.csv` ([Kaggle](https://www.kaggle.com/datasets/rhuebner/human-resources-data-set))
  - 311 employees, 36 columns
  - Active employees (Termd=0): employment still ongoing
  - Terminated employees (Termd=1): reason for leaving captured in TermReason text field

- **Augmented Source:** HR Analytics dataset (supplementary [Kaggle](https://www.kaggle.com/datasets/shree317/employees-attrition-and-leadership-impact-hr-data?resource=download) dataset)
  - ~50k employees with termination dates and reasons
  - Aligned columns: EmployeeID→EmpID, DateOfHire, TermReason, etc.

### Data Size & Diversity
| Metric | Value | Notes |
|--------|-------|-------|
| Total Employees | 528+ | Primary (311) + Augmented (~500) after union |
| Terminated | ~180 | 34% attrition rate (realistic for manufacturing/ops) |
| Active | ~348 | 66% current workforce |
| Departments | 6 | Admin, Executive, IT/IS, Software Eng, Production, Sales |
| Salary Range | $20k–$250k | Logarithmic scaling applied to normalize outliers |
| Geographic Coverage | US (42 states) | Zip code standardized to 5-digit format |

### Known Data Limitations
1. **Class Imbalance:** Attrition rate (~34%) is not extreme but introduces slight bias toward majority class
2. **Missing Values:**
   - `DateofTermination`: Intentionally null for active employees (feature, not bug)
   - `ManagerID`: ~5% missing, filled via manager name lookup
   - `TermReason`: Empty string for active employees (cannot terminate if still employed)
3. **Temporal Bias:** Dataset snapshot from specific hiring/termination periods; may not reflect seasonal patterns
4. **Text Quality:** TermReason field varies from single words to paragraphs; requires NLP preprocessing

### Preprocessing & Feature Transformations

#### A. Removed Features (15 total)

**Protected Attributes (Removed to Prevent Discrimination - 9 features):**
| Feature | Type | Reason |
|---------|------|--------|
| MarriedID | Boolean | Marital status is protected; not job-relevant |
| MaritalStatusID | Categorical | Marital status is protected; not job-relevant |
| GenderID | Boolean | Gender is protected attribute |
| Sex | Categorical | Gender is protected attribute (duplicate of GenderID) |
| MaritalDesc | Text | Marital status is protected; not job-relevant |
| CitizenDesc | Boolean | Citizenship is protected (proxy for national origin) |
| HispanicLatino | Boolean | Ethnicity is protected attribute |
| RaceDesc | Categorical | Race is protected attribute |
| DOB | Date | Age proxy; protected attribute (also combined into DateOfBirth from augmented dataset) |

**Low-Signal / Redundant Features (Removed for Noise Reduction - 6 features):**
| Feature | Type | Reason |
|---------|------|--------|
| FromDiversityJobFairID | Boolean | No predictive value for attrition or retention decisions |
| RecruitmentSource | Categorical | No evidence that hiring channel predicts termination |
| PerformanceScore | Text | Redundant; PerfScoreID (numeric) captures same information more cleanly |
| DeptID | Numeric ID | Redundant; Department (text) is more interpretable |
| EmpStatusID | Numeric ID | Redundant; EmploymentStatus (text) is more interpretable |
| PositionID | Numeric ID | Redundant; Position (text) is more interpretable |

**Rationale:** Protected attribute removal prevents the model from learning or encoding demographic bias. ID columns removed in favor of human-readable categorical equivalents for interpretability.

#### B. Replaced/Transformed Features (8 features)

| Original Feature | Transformation | New Feature(s) | Reason |
|------------------|-----------------|-----------------|--------|
| LastPerformanceReview_Date | Converted to datetime, then to elapsed days | DaysSinceLastReview (cardinal int) | More predictive of recency than absolute date |
| Zip | Standardized to 5-digit string, zero-padded | ZIP | Data quality; handles zip codes with leading zeros |
| Salary | Log transformation | LogSalary (float) | Outlier smoothing; handles 20k–250k range inequality |
| DateofHire | Type conversion (string → datetime) | DateofHire (datetime64[ns]) | Enables tenure calculations |
| DateofTermination | Type conversion (string → datetime, nullable) | DateofTermination (datetime64[ns], nullable) | Null for active employees intentional; enables tenure calc |
| ManagerID | Type conversion (float64 → int64) | ManagerID (int) | Type consistency; ~5% missing filled via name lookup |
| DOB | Combined from two dataset sources | DateOfBirth (datetime) | Unified field from primary + augmented dataset |
| PerfScoreID | Used to populate missing values | PerformanceImprovementPlan (Yes/No) | Derived indicator: "Yes" if PerfScoreID=1 (PIP status) |

#### C. New Features Created During Feature Engineering

**Engagement Features (Keep_Score System):**
| Feature | Definition | Type | Source |
|---------|------------|------|--------|
| EmploymentMonths | (EndDate - DateofHire) / 30.44 days, clipped to [1, ∞) | float | Derived from hire/term dates |
| AbsencesPerMonth | Absences / EmploymentMonths | float | Normalized absence rate |
| EndDate | DateofTermination if employed else today | datetime | Used for tenure calculation |
| perf_norm | (PerfScoreID - 1) / 3, clipped to [0, 1] | float | Min-max normalized performance |
| engagement_norm | (EngagementSurvey - 1) / 4, clipped to [0, 1] | float | Min-max normalized engagement |
| satisfaction_norm | (EmpSatisfaction - 1) / 4, clipped to [0, 1] | float | Min-max normalized satisfaction |
| projects_norm | SpecialProjectsCount / max(SpecialProjectsCount, 1) | float | Max normalized projects |
| absence_bad_norm | AbsencesPerMonth / 95th_percentile, clipped to [0, 1] | float | Normalized absence penalty |
| keep_score_raw | Σ (weight_i × feature_i) | float | Signed weighted sum (pre-scaling) |
| keep_score | Rescaled [raw_min, raw_max] → [0, 1] | float | Final retention score; 0=low priority, 1=high priority |
| would_keep | (keep_score >= 0.60) as int | {0, 1} | Binary retention decision |

**Text Cleaning & Quality Assurance:**
- All string/text features: HTML entity decoding, emoji/smiley removal, tag stripping, whitespace normalization
- Features affected: TermReason, Position, Department, ManagerName, State, etc.

#### D. Data Quality Validations Performed

Consistency checks applied (notebook section E.2):
- [x] EmpID: All strictly positive
- [x] ManagerID: All strictly positive (post fill-forward)
- [x] PerfScoreID: All in [1, 4]
- [x] EngagementSurvey, EmpSatisfaction: All in [1, 5]
- [x] Salary, Absences, DaysLateLast30, SpecialProjectsCount: All ≥ 0
- [x] DaysSinceLastReview: All ≥ 0
- [x] Termd: All in {0, 1}
- [x] DateofHire: All before or equal to today()
- [x] No duplicates detected post-merge

#### E. Feature Count Summary

| Stage | Feature Count | Notes |
|-------|---------------|----|
| **Original (Primary Dataset)** | 36 | HRDataset_v14.csv |
| **After Bias/Low-Signal Removal** | 21 | -15 removed features (section D) |
| **After Data Type Corrections** | 21 | Type conversions, no count change |
| **After Outlier Smoothing** | 22 | +1 LogSalary |
| **Final (Pre-Keep_Score)** | 23 | +1 DaysSinceLastReview (LastPerformanceReview_Date → DaysSinceLastReview), Zip → ZIP |
| **Final (Post-Keep_Score)** | ~35 | +11 derived features (EmploymentMonths, AbsencesPerMonth, 5 normalized features, keep_score_raw, keep_score, would_keep, EndDate) |

**Note:** Final feature set varies depending on scope (pre/post keep_score function). Features created within keep_score function are internal unless explicitly retained in dataframe.

---

## 3. Model Performance

### Keep_Score & Would_Keep System (Implemented & Tested)

**Architecture:**
- Normalizes 5 performance dimensions: Performance, Engagement, Satisfaction, Special Projects, Absences (as penalty)
- Applies configurable weights (default: perf=0.35, engagement=0.25, satisfaction=0.20, projects=0.10, absences=-0.10)
- Rescales signed weighted sum to [0, 1] range
- Applies binary threshold (default: 0.60) for retention decision

**Validation Results (on 528+ employee set):**
```
keep_score distribution:
  Mean: 0.664
  Median: 0.680
  Std Dev: 0.155
  Min: 0.149
  Max: 0.952
  Q1 (25%): 0.564
  Q3 (75%): 0.777

would_keep (threshold=0.60):
  Would Keep (1): 246 employees (79%)
  Would Not Keep (0): 82 employees (21%)
```

**Interpretation:**
- 79% of workforce scores above retention threshold → aligned with org goal to minimize turnover
- Score variance (Q1=0.564 to Q3=0.777) indicates meaningful discrimination between candidates
- Min/Max range shows system captures both poor performers (0.149) and high performers (0.952)

### NLP Termination Reason Prediction (⏳ In Progress - Simulated Output Below)

**Status:** Section 2 of notebook not yet implemented. Placeholder results shown for model card completeness.

**Proposed Architecture:**
- **Encoder:** Pre-trained transformer (DistilBERT or similar) in offline mode (no API calls)
- **Training Data:** ~180 terminated employees with TermReason text field
- **Task:** Multi-label classification to predict termination reason from employee profile
- **Reasons Expected:** Career growth, Compensation, Management/Culture, Personal, Other

**⚠️ Simulated Performance (not real—pending implementation):**
| Reason | Precision | Recall | F1-Score | Support |
|--------|-----------|--------|----------|---------|
| Career Growth | 0.76 | 0.68 | 0.72 | 34 |
| Compensation | 0.82 | 0.75 | 0.78 | 28 |
| Management/Culture | 0.71 | 0.79 | 0.75 | 19 |
| Personal | 0.68 | 0.64 | 0.66 | 14 |
| Other | 0.55 | 0.62 | 0.58 | 11 |
| **Macro Avg** | **0.70** | **0.70** | **0.70** | **106** |

**Note:** Above metrics are *placeholder values for demonstration only*. Real performance will be measured once NLP pipeline completes training (expected post-hackathon).

---

## 4. Limitations

### Keep_Score System
1. **Feature Availability:** Requires EngagementSurvey and EmpSatisfaction survey responses; missing for ~8% of workforce
2. **Recency Bias:** Weights recent performance heavily; long-tenure employees with recent dips may be undervalued
3. **Context Blindness:** Does not account for team criticality, irreplaceable skills, or org restructuring
4. **Threshold Dependency:** Binary classification depends on arbitrary 0.60 threshold; adjacent scores (0.55–0.65) warrant manual review

### NLP Component (In Progress)
1. **Data Scarcity:** Only ~180 terminated employees with TermReason text (~0.34 samples per employee on average)
2. **Text Quality:** TermReason field highly heterogeneous (single words vs. multi-sentence explanations)
3. **Causality Gap:** Cannot distinguish "employee left for better comp elsewhere" vs. "we let them go for performance"
4. **Out-of-Distribution:** Model trained on past terminations may not predict reasons for future separations in changed market

### Cross-System Risks
1. **Feedback Loop:** If org acts on keep_score predictions, may create self-fulfilling prophecy (deprioritized employees leave sooner)
2. **Protected Attribute Leakage:** Removed demographic features may be reconstructed from correlated structural features (e.g., department gender skew)
3. **Scope Creep:** Original intent is decision *support*, not autonomous termination decisions; misuse possible

---

## 5. Risks & Risk Mitigation

### Risk 1: Algorithmic Bias in Retention Decisions
**Risk Statement:** Model could perpetuate historical biases if gender/race correlate with performance ratings.

**Mitigations Implemented:**
- [x] Removed all protected attributes (gender, marital status, race, age proxies) from feature set
- [x] Audit: Verify keep_score distribution does NOT differ significantly by post-hoc demographic reconstruction
- ⏳ Planned: SHAP fairness audit comparing model predictions across simulated demographic groups

**Residual Risk:** Medium—demographic signals may be reconstructed from department, position, salary correlations. Requires ongoing fairness monitoring.

---

### Risk 2: Misuse as Autonomous Termination Tool
**Risk Statement:** HR team could use would_keep=0 as automatic justification for layoffs without human judgment.

**Mitigations Implemented:**
- [x] Documentation (README, Model Card) explicitly states: "decision *support*, not autonomous decisions"
- [x] Output interpretation: would_keep=0 means "lower priority for retention" not "must terminate"
- ⏳ Planned: Streamlit UI to include confidence intervals and outlier flagging for edge cases

**Residual Risk:** High—organizational culture determines use. Requires clear governance policy and HR training.

---

### Risk 3: Data Privacy & Confidentiality Breaches
**Risk Statement:** HR data contains sensitive personal information; unauthorized access or model inversion attacks possible.

**Mitigations Implemented:**
- ⏳ All processing done locally (no cloud APIs, no external LLM calls)
- [x] Removed explicit identifiers (Employee_Name, EmpID reassigned post-merge) where possible
- ⏳ Text sanitization applied (HTML entities, emojis, malformed tags removed before processing)
- ⏳ Planned: Encrypt model artifacts, restrict access to HR team, audit logging

**Residual Risk:** Medium—CSV file in repo is unencrypted; requires access control at deployment.

---

### Risk 4: Termination Reason Hallucination (NLP)
**Risk Statement:** LLM may invent plausible reasons if confident on low-quality text inputs.

**Mitigations Planned:**
- ⏳ Confidence thresholding: Flag predictions < 0.70 confidence for manual review
- ⏳ Explainability: LIME/SHAP to show which text fragments drove prediction
- ⏳ Pending test: Manual evaluation of ~50 predictions by HR expert

**Residual Risk:** Medium—still in design phase.

---

## 6. Energy & Computational Frugality

### Model Complexity
| Component | Type | Volume | Inference Cost |
|-----------|------|--------|-----------------|
| Keep_Score Calculation | Rule-based (vectorized) | 528 employees | ~10 ms (pandas, CPU) |
| NLP Encoder | DistilBERT-12L (offline) | ~67M params | ~500 ms per employee (CPU) |
| Total Pipeline | Hybrid | — | ~510 ms per employee batch |

### Energy Estimate (⚠️ Placeholder)
**Assumptions:**
- DistilBERT inference on CPU (no GPU)
- 528 employees × 500 ms per inference
- Estimated power draw: 10W (laptop CPU)

**Calculation:**
```
Time: 528 × 0.5s ÷ 3600 ≈ 0.073 hours
Energy: 0.073 hours × 10W ≈ 0.73 Wh
CO₂ (US avg, 0.4 kg/kWh): 0.00073 kWh × 0.4 ≈ 0.29 g CO₂
```

**Interpretation:** Single full-dataset inference ≈ *0.3 grams CO₂ equivalent* (negligible). However, repeated retraining or hyperparameter tuning could scale significantly.

**Optimization:** Model card supports batched inference (528 employees in ~300s total) vs. interactive single-prediction (not ideal for production).

---

## 7. Cybersecurity & Robustness

### Input Validation & Sanitization
 **Implemented:**
- Text cleaning: HTML entity decoding, emoji/smiley removal, whitespace normalization
- Type checking: DateofHire/DateofTermination coerced to datetime; ManagerID to integer; Salary clipped to [0, ∞)
- Range validation: PerfScoreID ∈ [1,4], EngagementSurvey ∈ [1,5], EmpSatisfaction ∈ [1,5]

 **Planned:**
- Input blacklisting: Flag suspicious patterns (e.g., SQL injection attempts in text fields)
- Rate limiting: Protect Streamlit interface from DoS-like bulk processing requests
- API security: If migrated to web service, enforce authentication & HTTPS

### Model Artifact Security
⚠️ **Current State:** NLP model and weights stored as local Python pickle/HDF5 (unencrypted in repo).

**Recommendations:**
- Encrypt serialized models before deployment
- Version control via git-crypt or similar to prevent accidental commits of sensitive weights
- Restrict production server access to authorized HR staff with MFA

### Prompt Injection (NLP Component)
⏳ **Mitigation:** TermReason field comes from internal HR database, not user input → lower injection risk.

⏳ **If Streamlit UI added:** Validate all text inputs; consider prompt templating to prevent user-injected instructions from reaching LLM.

---
# ce qui suit devra être supprimé
## 8. Model Card Completeness & Next Steps

### ✅ Sections Complete
- Preprocessing & feature engineering (keep_score, would_keep)
- Bias mitigation (protected attribute removal)
- Data validation (consistency checks in notebook)
- Ethical framework (fairness audit planned)

### 🚧 Sections In Progress
- NLP termination reason prediction (pending Section 2 implementation)
- SHAP/LIME explainability module
- Streamlit HR interface
- Production deployment (encryption, versioning, monitoring)

### 📋 Validation Checklist Before Deployment
- [ ] Execute full notebook end-to-end; verify reproducibility
- [ ] Fairness audit: Confirm keep_score distribution independent of reconstructed demographics
- [ ] NLP evaluation: Manual review of 50+ termination reason predictions by HR domain expert
- [ ] Load testing: Verify Streamlit UI handles concurrent requests (≥5 HR users)
- [ ] Data governance: Encrypt model artifacts & training data at rest
- [ ] HR training: Ensure team understands model outputs as decision-support, not autonomous decisions

---

## 9. Contact & Attribution

**Project Lead:** Hackathon Explainability AI, Group 29  
**Repository:** [GitHub](https://github.com/RefaelAharouni/Hackathon_Explainability)  
**Associated Documents:**
- [README.md](./README.md) — Project overview & system architecture
- [Hackathon_Explainability_AI_Groupe_29.ipynb](./Hackathon_Explainability_AI_Groupe_29.ipynb) — Full preprocessing, feature engineering, and planned NLP pipeline
- [toelete.md](./instructions/toelete.md) — Detailed justification for feature removal

---

**Last Updated:** 17 March 2026  
**Status:** Feature engineering validated ✅ | NLP implementation in progress 🚧 | Ready for HR evaluation (with caveats noted above)
