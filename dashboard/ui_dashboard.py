import streamlit as st
import pandas as pd
import plotly.express as px
from utils.web3_utils import log_event

st.title("Monitorizare Chirurgie Pediatrică")

# Simulate data
data = pd.read_csv("data/vitals_sample.csv")

# Alertă pe scoruri vitale
alerts = data[(data["heart_rate"] > 180) | (data["spo2"] < 90) | (data["temperature"] > 38.5)]

if not alerts.empty:
    st.error(f"{len(alerts)} ALERTE DETECTATE!")
    for idx, row in alerts.iterrows():
        st.write(f"{row['patient_id']} – HR: {row['heart_rate']}, SpO₂: {row['spo2']}, Temp: {row['temperature']}")
        log_event(row["patient_id"], "ALERT_TRIGGERED")

# Grafic
fig = px.line(data, x="timestamp", y="heart_rate", color="patient_id", title="Evoluție Heart Rate")
st.plotly_chart(fig)