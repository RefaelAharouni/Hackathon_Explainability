# Hackathon Explainability AI


**Group 29 : Aharouni Refaël, Goder Joshua, Gérard Paul, Montaron Léa, Farhi-Rivasseau Guillaume**

https://colab.research.google.com/drive/1SUB4oUlV2ItxqPIXCrLRPyQXw4xjospX?usp=sharing


## Ideas
•	We decide to take a model that we download once with HuggingFace. Then, we change the offline booleans to 1 to ensure confidentiality once downloaded (local operation)
•	We train the LLM on all employees who have already left the company (reviews + personal ratings) and we will test it on all current employees + we will develop an application in which we will ask for its performance criteria + its reviews. For each performance criterion, a performance weight will be assigned. Thus, at the end, for each employee, we will obtain a performance score and we can rank the employees in descending order of performance score. All this will allow us to know if we want the employee to stay (he is essential to the company) or not based on a threshold (for example, 0.5).
•	In parallel, the LLM, from the semantic comparison of the reviews and ratings assigned by the client, will allow to know if he wants to leave the company or not. A new boolean indicating whether the client wants to leave or not (all those who have already left will be at 1 by default) will be indicated with another column containing the reasons if the client wishes to leave and nothing else.
•	If the two booleans are identical, then everything is fine (if the company and the employee agree for the employee to leave, then he leaves and we summarize the reasons why he wants to leave and if they both want him to stay, then he stays). If the company wants him to leave and he is part of the 30 «worst» in terms of performance score, then he will be fired, regardless of his opinion on it. If she wants him to leave but he is still performing well, then he will stay. If the company wants him to stay but he wants to leave, we will establish the reasons why he wants to leave.
If, on the other hand, the employee wants to stay but the company wants him to leave, if he is one of the 30 «less good», he will leave, otherwise he will stay.



Once the LLM has been trained, we can use it through a streamlit interface (run.py) as a frontend, which would be proposed to the HR; they would be asked for information and the AI would give them an answer.
We can filter attacks quickly with word filters I guess.
