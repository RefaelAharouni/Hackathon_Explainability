# Employee Turnover Prediction and Insights

**Project :** Hackathon Explainability AI - Group 29  
**Team :** Aharouni Refaël, Goder Joshua, Gérard Paul, Montaron Léa, Farhi-Rivasseau Guillaume  
**Date :** 17 March 2026  

---


## 1. Context

A fictional company is facing a high employee turnover rate, negatively impacting performance, team stability, and recruitment costs.  
The Human Resources department aims to better understand the root causes of employee attrition and preserve key talent.  
This project explores how AI can support HR decision-making by identifying early signals of disengagement and providing actionable insights.  


## 2. Objectives

We propose an AI-based analytical pipeline designed to assist HR teams in talent management and retention.  
The system analyzes both quantitative and qualitative employee data to:

• Identify employees at risk of leaving <br>
• Understand the main drivers of dissatisfaction <br>
• Evaluate employee performance through a structured scoring system <br>
• Provide interpretable insights to support HR decisions <br>


## 3. Scope

Our project focuses on internal employee data (reviews, ratings, performance criteria) and uses local and privacy-preserving AI models.  
It was designed as a model-driven analysis for HR assistance, it does not replace human judgment.  
It allows HR teams to understand *why* an employee is at risk, rather than relying on a black-box prediction.


## 4. Key Features

#### a)  Local LLM Deployment
We decide to take a model that we downloaded once using Hugging Face and then used in offline mode to ensure data confidentiality.  
All computations are performed locally, with no external API calls.

#### b)  Training and Evaluation Pipeline
We trained the LLM on all employees who had already left the company (reviews and personal ratings) and we tested it on all current employees.
The model pipeline allows HR to define performance criteria (like productivity and collaboration) and to assign weights to each of them.
A global performance score was computed for each employee, enabling ranking and identification of key contributors based on a predefined threshold.
All this will allow us to know if we want the employee to stay (he is essential to the company) or not based on an adjustable threshold.

#### c)  Departure Risk Detection
In parallel, from the semantic comparison of the reviews and ratings assigned by HR records, the LLM will allow us to know if the employee is likely to leave the company or not. For that, we used a boolean, set by default at 1 for those who have already left, and we implement another column that contains the reasons why the client wishes to leave.

#### d)  Decision Logic Framework

The system compares the company’s evaluation with the predicted employee intention (stay or leave).
Based on this comparison, two scenarios are considered:

• The company and the employee are aligned : consistent outcome (the employee will stay or leave)   
• The company and the employee disagree : inconsistent outcome (the employee may stay or leave)   

In case of mismatch, the system highlights underlying reasons and provides structured insights.   
If an high-performing employee is flagged for departure, the compagny will try to find a solution according to the provided insights.   
It could be a salary increase, an internal mobility or a promotion.   
Our system still keep the final decision under human control.  

#### Model Output & Insights
Once trained, the LLM generates a predictive report highlighting at-risk employees. It provides a structured output explaining the reasons behind each prediction (e.g., mismatch between performance and satisfaction). <br>
