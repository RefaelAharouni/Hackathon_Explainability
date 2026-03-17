# **Technical Documentation:**
**Project:** Hackathon Explainability - Group 29

**Authors:** Aharouni Refaël, Goder Joshua, Gérard Paul, Montaron Léa, Farhi-Rivasseau Guillaume

**Dataset:** `HRDataset_v14.csv` & `employees attrition and leadership impact hr data`

---

## **1. System Overview**  
The objective of this project is to implement an AI solution (combining NLP and Classification) to help the company understand employee quitting rates and reasons for resignation. The system identifies high-risk employees and provides actionable insights for talent retention based on performance metrics such as engagement, special projects, and absences.

## **2. Data Engineering & Preprocessing**

#### **A. Dataset Integration (Concatenation)**
To increase the robustness of the model and capture a wider range of employee behaviors, we performed a horizontal concatenation of two primary datasets.
   * **Merging Logic:** The datasets were aligned based on unique employee identifiers.
   * **Result:** This process allowed us to combine standard HR administrative data with detailed performance and engagement metrics, providing a 360-degree view of the employee lifecycle.

#### **B. Outlier Management**
To ensure model stability and prevent extreme values from distorting the results, we analyzed numerical distributions:
   * **Identification:** Used Boxplots to detect outliers in sensitive columns like `Salary` and `Absences`.
   * **Treatment:** Identified outliers were evaluated to distinguish between "noise" and "exceptional profiles." This step ensures that the model learns from representative employee patterns rather than anomalies.

#### **C. Feature Engineering: The `would_keep` Variable**
A key innovation in this project is the creation of the `would_keep` target feature. This variable represents the company's strategic interest in an employee, calculated based on:
   * **Performance Scores:** High performers are marked as essential.
   * **Engagement & Projects:** Employees involved in high-impact special projects or with top-tier engagement scores are prioritized.
   * **Logic:** This allows the AI to not only predict who will leave but also to highlight who the company cannot afford to lose, enabling a prioritized retention strategy.

#### **D. Data Cleaning**
   * **Missing Values:**
      * `DateofTermination` was handled to distinguish between active and terminated employees.
      * `ManagerId` gaps were filled using a mapping dictionary based on manager names.

   * **Feature Transformation:**
      * Dates(`DateoHire`, `LastPerformanceReview_Date`) were converted to DateTime objects.
      * Engineered a `DaysSinceLastReview` feature to measure the time elapsed since the last formal evaluation.
      * ZIP codes were standardized to 5-character strings.
   
   * **Duplicate Management:** A rigorous check for duplicate entries was conducted using unique employee identifiers. No redundant records were found, ensuring that the statistical distribution of the features remains unbiased.   

#### **E. Bias Mitigation & Ethical AI**
To ensure algorithmic fairness and prevent discrimination, the following sensitive demographic and recruitment variables were removed from the training set:
   * **Demographics:** `MarriedID`, `MaritalStatusID`, `GenderID`, `DOB`, `Sex`, `MaritalDesc`, `CitizenDesc`, `HispanicLatino`, `RaceDesc`.
   * **Personal Info:** `State`, `Zip`, `EmploymentStatus`
   *  **Sourcing:** `FromDiversityJobFairID`, `RecruitmentSource`
   


