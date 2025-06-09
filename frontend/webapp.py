"""Simple Streamlit frontend for demand predictions."""

import json
import requests
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

API_URL = "http://localhost:8000/predict"

st.title("Prediccion de Demanda")

with st.form("prediction_form"):
    features = {
        "age": st.number_input("age", value=0.0),
        "sex": st.number_input("sex", value=0.0),
        "bmi": st.number_input("bmi", value=0.0),
        "bp": st.number_input("bp", value=0.0),
        "s1": st.number_input("s1", value=0.0),
        "s2": st.number_input("s2", value=0.0),
        "s3": st.number_input("s3", value=0.0),
        "s4": st.number_input("s4", value=0.0),
        "s5": st.number_input("s5", value=0.0),
        "s6": st.number_input("s6", value=0.0),
    }
    submitted = st.form_submit_button("Predecir")

if submitted:
    resp = requests.post(API_URL, json=features)
    if resp.ok:
        result = resp.json()["prediction"]
        st.success(f"Prediccion: {result}")
    else:
        st.error("Error al consultar la API")

st.header("Demanda Historica")
hist = pd.read_csv("data/simulated.csv")
fig, ax = plt.subplots()
ax.plot(hist.index, hist["target"], label="historico")
ax.set_xlabel("Registro")
ax.set_ylabel("Demanda")
st.pyplot(fig)
