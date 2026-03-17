# Hackathon Explainability AI


**Group 29 : Aharouni Refaël, Goder Joshua, Gérard Paul, Montaron Léa, Farhi-Rivasseau Guillaume**


## Context

A fictional company is facing a high employee turnover rate, negatively impacting performance, team stability, and recruitment costs. <br>
The Human Resources department aims to better understand the root causes of employee attrition and preserve key talent. <br>
This project explores how AI can support HR decision-making by identifying early signals of disengagement and providing actionable insights. <br>


## Objectives

We propose an AI-based solution designed to assist HR teams in talent management and retention. <br>
The system analyzes both quantitative and qualitative employee data to:

• Identify employees at risk of leaving <br>
• Understand the main drivers of dissatisfaction <br>
• Evaluate employee performance through a structured scoring system <br>
• Provide interpretable insights to support HR decisions <br>


## Scope

Our project focuses on internal employee data (reviews, ratings, performance criteria) and uses local and privacy-preserving AI models. <br>
It was designed as a prototype for HR assistance, it does not replace human judgment. <br>
It allows HR teams to understand *why* an employee is at risk, rather than relying on a black-box prediction.


## Key Features

#### Local LLM Deployment
We decide to take a model that we downloaded once using Hugging Face and then used in offline mode to ensure data confidentiality. <br>
All computations are performed locally, with no external API calls.

#### Training and Evaluation Pipeline
We trained the LLM on all employees who had already left the company (reviews and personal ratings) and we tested it on all current employees.
The application allows HR to define performance criteria (like productivity and collaboration) and to assign weights to each of them.
A global performance score was computed for each employee, enabling ranking and identification of key contributors based on a predefined threshold.
All this will allow us to know if we want the employee to stay (he is essential to the company) or not based on an adjustable threshold.

#### Departure Risk Detection
In parallel, from the semantic comparison of the reviews and ratings assigned by the client, the LLM will allow us to know if the employee is likely to leave the company or not. For that, we used a boolean, set by default at 1 for those who have already left, and we implement another column that contains the reasons why the client wishes to leave.

#### Decision Logic Framework

The system compares the company’s evaluation with the predicted employee intention (stay or leave).
Based on this comparison, two scenarios are considered:

• The company and the employee are aligned : consistent outcome (the employee will stay or leave)
• The company and the employee disagree : inconsistent outcome (the employee may stay or leave)

In case of mismatch, the system highlights underlying reasons and provides structured insights. <br>
If an high-performing employee is flagged for departure, the compagny will try to find a solution according to the provided insights. <br>
It could be a salary increase, an internal mobility or a promotion. <br>
Our system still keep the final decision under human control. <br>

#### User Interface
Once the LLM has been trained, The HR will be able to use it through a streamlit interface (run.py) as a frontend. <br>
They would be asked for information and the AI would give them an answer. <br>
Simple word-based filtering mechanisms can be implemented to limit inappropriate or malicious inputs. <br>
