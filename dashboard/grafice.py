import streamlit as st 
import pandas as pd
import plotly.express as px

def run_monitorizare():
    st.title("Monitorizare pacienți")

    data = pd.read_csv("data/vitals_sample.csv")
    data["timestamp"] = pd.to_datetime(data["timestamp"])

    # Găsim alertele critice
    alerts = data[(data["Puls"] > 180) | (data["SpO2"] < 90) | (data["Temperatura"] > 38.5)]
    alerts = alerts.sort_values("timestamp", ascending=False)
    last_alerts = alerts.drop_duplicates(subset="patient_id", keep="first")

    if not last_alerts.empty:
        st.error(f"{len(last_alerts)} alerte critice detectate!")
        for idx, row in last_alerts.iterrows():
            probleme = []
            if row["Puls"] > 180:
                probleme.append(f"Puls ridicat: {row['Puls']}")
            if row["SpO2"] < 90:
                probleme.append(f"SpO₂ scăzut: {row['SpO2']}")
            if row["Temperatura"] > 38.5:
                probleme.append(f"Temperatură ridicată: {row['Temperatura']}")

            probleme_str = "; ".join(probleme)
            st.warning(f"⚠️ Pacient ID {row['patient_id']} – {probleme_str}")
    else:
        st.success("Nu sunt alerte critice pentru pacienți.")

    # Alegere semn vital
    metric = st.selectbox(
        "Alege semnul vital pentru a vizualiza graficul:",
        ("Puls", "SpO₂", "Temperatura")
    )

    if metric == "Puls":
        fig = px.line(data, x="timestamp", y="Puls", color="patient_id", title="Ritmul Cardiac")
    elif metric == "SpO₂":
        fig = px.line(data, x="timestamp", y="SpO2", color="patient_id", title="Saturația în Oxigen (SpO₂)")
    else:
        fig = px.line(data, x="timestamp", y="Temperatura", color="patient_id", title="Temperatura Corpului")

    st.plotly_chart(fig)

    # Grafice detaliate doar pentru pacienții cu alerte
    for idx, row in last_alerts.iterrows():
        patient_data = data[data["patient_id"] == row["patient_id"]]

        if row["Puls"] > 180:
            fig_hr = px.line(patient_data, x="timestamp", y="Puls",
                             title=f"📈 Puls pentru Pacientul {row['patient_id']}")
            st.plotly_chart(fig_hr)

        if row["SpO2"] < 90:
            fig_spo2 = px.line(patient_data, x="timestamp", y="SpO2",
                               title=f"📈 SpO₂ pentru Pacientul {row['patient_id']}")
            st.plotly_chart(fig_spo2)

        if row["Temperatura"] > 38.5:
            fig_temp = px.line(patient_data, x="timestamp", y="Temperatura",
                               title=f"📈 Temperatură pentru Pacientul {row['patient_id']}")
            st.plotly_chart(fig_temp)
