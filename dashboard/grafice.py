import streamlit as st 
import pandas as pd
import plotly.express as px

import os,sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.database import SessionLocal, Patient, VitalSigns

def run_monitorizare():
    st.title("Monitorizare pacienți")

    db = SessionLocal()

    data = db.query(
        Patient.patient_id,
        VitalSigns.heart_rate.label("Puls"),
        VitalSigns.spo2.label("SpO2"),
        VitalSigns.temperature.label("Temperatura"),
        VitalSigns.timestamp
    ).join(VitalSigns, Patient.patient_id == VitalSigns.patient_id).all()
    db.close()

    # Convertim rezultatele într-un DataFrame
    data = pd.DataFrame(data, columns=["patient_id", "Puls", "SpO2", "Temperatura", "timestamp"])
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
            st.warning(f"Pacient ID {row['patient_id']} – {probleme_str}")
    else:
        st.success("Nu sunt alerte critice pentru pacienți.")

    st.markdown("---")
    st.subheader("Caută și selectează pacienți pentru grafic")

    # Lista unică cu pacienți
    pacienti_unici = data["patient_id"].unique().tolist()
    pacienti_selectati = st.multiselect(
        "Selectează pacienți",
        options=pacienti_unici,
        default=last_alerts["patient_id"].unique().tolist()  # implicit selectați pacienții cu alerte
    )

    if len(pacienti_selectati) == 0:
        st.info("Selectează cel puțin un pacient pentru a vedea graficul.")
        return

    # Alegere semn vital
    metric = st.selectbox(
        "Alege semnul vital pentru a vizualiza graficul:",
        ("Puls", "SpO2", "Temperatura")
    )

    # Filtrăm datele pentru pacienții selectați
    data_filtrata = data[data["patient_id"].isin(pacienti_selectati)]

    # Titlu grafic
    titlu_metric = {
        "Puls": "Ritmul Cardiac",
        "SpO2": "Saturația în Oxigen (SpO₂)",
        "Temperatura": "Temperatura Corpului"
    }

    # Graficul principal cu toți pacienții selectați
    fig = px.line(
        data_filtrata,
        x="timestamp",
        y=metric,
        color="patient_id",
        title=f"{titlu_metric[metric]} pentru pacienți selectați"
    )
    st.plotly_chart(fig)

    # Opțional: grafice detaliate pentru fiecare pacient selectat
    st.subheader("Grafice detaliate pentru pacienții selectați")
    for pacient in pacienti_selectati:
        pacient_data = data_filtrata[data_filtrata["patient_id"] == pacient]
        fig_detaliat = px.line(
            pacient_data,
            x="timestamp",
            y=metric,
            title=f"{titlu_metric[metric]} - Pacient ID {pacient}"
        )
        st.plotly_chart(fig_detaliat)

