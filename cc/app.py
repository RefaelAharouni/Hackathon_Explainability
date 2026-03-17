import streamlit as st
import pandas as pd
import joblib
import os
from transformers import pipeline

st.set_page_config(page_title="HR Explainability AI", layout="wide")

# Configuration LLM Offline
os.environ["TRANSFORMERS_OFFLINE"] = "1" 

@st.cache_resource
def load_resources():
    model = joblib.load("best_xgb_model.pkl")
    data = pd.read_csv("final_hr_data.csv")
    # Remplacez par le chemin de votre modèle local téléchargé
    # pipe = pipeline("text-generation", model="./my_local_llama") 
    return model, data, None # pipe à la place de None si chargé

model, df_app, llm_pipe = load_resources()

st.title("🤖 29th Team: HR Explainability Management Board")

tab1, tab2 = st.tabs(["Dashboard Global", "Analyse Individuelle"])

with tab1:
    st.subheader("Visualisation des risques")
    st.scatter_chart(df_app, x="StressLevelScore", y="keep_score", color="would_keep")

with tab2:
    emp_id = st.selectbox("Sélectionner un employé", df_app['EmpID'].unique())
    row = df_app[df_app['EmpID'] == emp_id].iloc[0]
    
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Poste:** {row['Position']}")
        st.metric("Score de Rétention", f"{row['keep_score']:.2f}")
        st.metric("Niveau de Stress", f"{row['StressLevelScore']}/10")
    
    with col2:
        st.subheader("Analyse Ethique du LLM")
        if st.button("Générer l'explication"):
            # Simulation si le pipe n'est pas chargé pour le test
            if llm_pipe is None:
                st.info(f"Analyse basée sur le contexte : {row['textInformation'][:150]}...")
                st.warning("Mode démo : Connectez un modèle local pour l'explication complète.")
            else:
                response = llm_pipe(row['textInformation'], max_new_tokens=100)
                st.success(response[0]['generated_text'])

    # Logique de décision (Mismatch detection)
    st.divider()
    if row['would_keep'] == 1 and row['Termd'] == 1:
        st.error("⚠️ ALERTE : Cet employé était jugé 'Essentiel' mais a quand même quitté l'entreprise.")
    elif row['would_keep'] == 0 and row['Termd'] == 0:
        st.warning("ℹ️ ATTENTION : Employé à faible priorité de rétention actuellement en poste.")