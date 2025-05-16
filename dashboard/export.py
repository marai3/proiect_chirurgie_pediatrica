import streamlit as st
import pandas as pd
from sqlalchemy.orm import Session
from database import SessionLocal, Patient, VitalSigns  
import io

def pagina_export():
    st.title("Exportă Date Vitale din Baza de Date")

    # Deschide sesiune DB
    db: Session = SessionLocal()

    # Obține lista pacienților
    pacienti = db.query(Patient).all()
    if not pacienti:
        st.warning("Nu există pacienți în baza de date.")
        return

    optiuni = {f"{p.pseudonym} ({p.patient_id})": p.patient_id for p in pacienti}
    selectie = st.selectbox("Selectează pacientul:", list(optiuni.keys()))
    patient_id = optiuni[selectie]

    # Obține date vitale pentru pacientul selectat
    date_vitale = db.query(VitalSigns).filter(VitalSigns.patient_id == patient_id).order_by(VitalSigns.timestamp).all()

    if not date_vitale:
        st.info("Acest pacient nu are date vitale salvate.")
        return

    # Convertim la DataFrame
    df = pd.DataFrame([{
        "heart_rate": d.heart_rate,
        "spo2": d.spo2,
        "temperature": d.temperature,
        "timestamp": d.timestamp,
        "source": d.source
    } for d in date_vitale])

    st.dataframe(df)

    # Alegem formatul de export
    format_export = st.radio("Selectează formatul pentru export:", ["CSV", "JSON"])

    if format_export == "CSV":
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Descarcă CSV",
            data=csv,
            file_name=f"{patient_id}_vital_signs.csv",
            mime="text/csv"
        )
    else:
        json_data = df.to_json(orient="records", force_ascii=False, indent=2)
        st.download_button(
            label="Descarcă JSON",
            data=json_data,
            file_name=f"{patient_id}_vital_signs.json",
            mime="application/json"
        )

    db.close()
