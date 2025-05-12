import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from home import render_sidebar


def run_monitorizare():

    st.title("Monitorizare pacienti")

    data = pd.read_csv("data/vitals_sample.csv")
    data["timestamp"] = pd.to_datetime(data["timestamp"])


    alerts = data[(data["Puls"] > 180) | (data["SpO2"] < 90) | (data["Temperatura"] > 38.5)]
    alerts = alerts.sort_values("timestamp", ascending=False)
    last_alerts = alerts.drop_duplicates(subset="patient_id", keep="first")

    if not last_alerts.empty:
        st.error(f"{len(last_alerts)} alerte critice detectate!")
        for idx, row in last_alerts.iterrows():
            st.write(f"{row['patient_id']} – Puls: {row['Puls']}, SpO₂: {row['SpO2']}, Temperatură: {row['Temperatura']}")
    else:
        st.write("Nu sunt alerte critice pentru pacienți.")

    metric = st.selectbox(
        "Alege semnul vital pentru a vizualiza graficul:",
        ("Puls", "SpO₂", "Temperatură")
    )

    if metric == "Puls":
        fig = px.line(data, x="timestamp", y="Puls", color="patient_id", title="Ritmul Cardiac")
        st.plotly_chart(fig)

    elif metric == "SpO₂":
        fig = px.line(data, x="timestamp", y="SpO2", color="patient_id", title="Saturația în Oxigen (SpO₂)")
        st.plotly_chart(fig)

    else: 
        fig = px.line(data, x="timestamp", y="Temperatura", color="patient_id", title="Temperatura Corpului")
        st.plotly_chart(fig)


    for idx, row in last_alerts.iterrows():
        if row["Puls"] > 180:
            fig_hr = px.line(data[data["patient_id"] == row["patient_id"]], x="timestamp", y="Puls", title=f"Ritmul Cardiac pentru Pacientul {row['patient_id']}")
            st.plotly_chart(fig_hr)
        elif row["SpO2"] < 90:
            fig_spo2 = px.line(data[data["patient_id"] == row["patient_id"]], x="timestamp", y="SpO2", title=f"Saturația în Oxigen pentru Pacientul {row['patient_id']}")
            st.plotly_chart(fig_spo2)
        elif row["Temperatura"] > 38.5:
            fig_temp = px.line(data[data["patient_id"] == row["patient_id"]], x="timestamp", y="Temperatura", title=f"Temperatura pentru Pacientul {row['patient_id']}")
            st.plotly_chart(fig_temp)
