# **Technical Documentation:**
**Project:** Hackathon Explainability - Group 29

**Authors:** Aharouni Refaël, Goder Joshua, Gérard Paul, Montaron Léa, Farhi-Rivasseau Guillaume

**Dataset:** `HRDataset_v14.csv` & `employees attrition and leadership impact hr data`

---

### **1. System Overview**  
The objective of this project is to implement an AI solution (combining NLP and Classification) to help the company understand employee quitting rates and reasons for resignation. The system identifies high-risk employees and provides actionable insights for talent retention based on performance metrics such as engagement, special projects, and absences.

### **2. Data Engineering & Preprocessing**

#### **A. Dataset Integration (Concatenation)**
To increase the robustness of the model and capture a wider range of employee behaviors, we performed a horizontal concatenation of two primary datasets.
   * **Merging Logic:** The datasets were aligned based on unique employee identifiers.
   * **Result:** This process allowed us to combine standard HR administrative data with detailed performance and engagement metrics, providing a 360-degree view of the employee lifecycle.

#### **B. Data Cleaning**
   * **Missing Values:**
      * `DateofTermination` was handled to distinguish between active and terminated employees.
      * `ManagerId` gaps were filled using a mapping dictionary based on manager names.

   * **Feature Transformation:**
      * Dates(`DateoHire`, `LastPerformanceReview_Date`) were converted to DateTime objects.
      * Engineered a `DaysSinceLastReview` feature to measure the time elapsed since the last formal evaluation.
      * ZIP codes were standardized to 5-character strings.

#### **C. Bias Mitigation & Ethical AI**
To ensure algorithmic fairness and prevent discrimination, the following sensitive demographic and recruitment variables were removed from the training set:
   * **Demographics:** `MarriedID`, `MaritalStatusID`, `GenderID`, `DOB`, `Sex`, `MaritalDesc`, `CitizenDesc`, `HispanicLatino`, `RaceDesc`.
   * **Personal Info:** `State`, `Zip`, `EmploymentStatus`
   *  **Sourcing:** `FromDiversityJobFairID`, `RecruitmentSource`


