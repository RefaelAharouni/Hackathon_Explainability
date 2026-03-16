# Hackathon_Explainability
https://colab.research.google.com/drive/1SUB4oUlV2ItxqPIXCrLRPyQXw4xjospX?usp=sharing


## ideas
•	On décide de prendre un modèle qu’on télécharge une fois avec HuggingFace. Ensuite, on passe les booléens d’offline à 1 pour s’assurer de la confidentialité une fois téléchargés (fonctionnement en local)
•	On entraîne le LLM sur tous les employés qui sont déjà partis de la compagnie (reviews + ratings persos) et on le testera sur tous les employés actuels + on développera une application dans lesquelles on demandera ses critères de performance + ses reviews. Pour chaque critère de performance, on attribuera un poids de performance. Ainsi, à la fin, pour chaque employé, on obtiendra un score de performance et on pourra classer les employés par ordre décroissant de score de performance. Tout ça permettra de savoir si on veut que l’employé reste (il est indispensable à la compagnie) ou pas en fonction d’un seuil (par exemple, 0.5).
•	En parallèle, le LLM, à partir de la comparaison sémantique des reviews et ratings attribués par le client, permettra de savoir s’il veut partir de la compagnie ou pas. Un nouveau booléen indiquant si le client veut partir ou pas (tous ceux qui sont déjà partis seront à 1 par défaut) sera indiqué avec une autre colonne de créée contenant les raisons si le client souhaite bien partir et rien sinon.
•	Si les deux booléens sont identiques, alors tout va bien (si l’entreprise et l’employé sont d’accord pour que l’employé parte, alors il part et on résume les raisons pour lesquelles il veut partir et s’ils veulent tous deux qu’il reste, alors il reste). Si l’entreprise veut qu’il parte et qu’il fait partie des 30 « pires » de la boîte en termes de score de performance, alors il sera viré, quelle que soit son avis là-dessus. Si elle veut qu’il parte mais qu’il est quand même performant, alors il restera. Si l’entreprise veut qu’il reste mais que lui veut partir, on établira les raisons pour lesquelles il veut partir.
Si en revanche l’employé veut rester mais que l’entreprise veut qu’il parte, s’il fait partie des 30 « moins bons », il partira, sinon il restera.


Une fois que le LLM aura été entraîné, on pourra l'utiliser au travers d'une interface streamlit (run.py) comme frontend, qui serait proposée aux HR; on leur demanderait des infos et l'IA leur donnerait une réponse.
On peut filtrer des attaques vite fait avec du filtre de mots j'imagine
