import streamlit as st
import pandas as pd
from sqlalchemy.orm import Session
import datetime
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.database import SessionLocal, Patient, VitalSigns, LabResult, ClinicalScore
from blockchain.MedicalLog import log_event, get_logs_by_patient_id

def pagina_export():
    st.title("Exportă Date Vitale din Baza de Date")

    # Deschide sesiune DB
    db: Session = SessionLocal()

    # Obține lista pacienților
    pacienti = db.query(Patient).order_by(Patient.patient_id).all()
    if not pacienti:
        st.warning("Nu există pacienți în baza de date.")
        return

    optiuni = {f"{p.pseudonym} ({p.patient_id})": p.patient_id for p in pacienti}
    selectie = st.selectbox("Selectează pacientul:", list(optiuni.keys()))
    patient_id = optiuni[selectie]
    pseudonym = [p.pseudonym for p in pacienti if p.patient_id == patient_id][0]

    # Obține date vitale pentru pacientul selectat
    date_vitale = db.query(VitalSigns).filter(VitalSigns.patient_id == patient_id).order_by(VitalSigns.timestamp).all()
    rezultate_laborator = db.query(LabResult).filter(LabResult.patient_id == patient_id).order_by(LabResult.timestamp).all()
    scoruri_clinice = db.query(ClinicalScore).filter(ClinicalScore.patient_id == patient_id).order_by(ClinicalScore.timestamp).all()
    access_logs = get_logs_by_patient_id(patient_id)
    #print(access_logs)

    alegere = [st.checkbox("Date pacient", value=True, key="date_pacient")]

    if date_vitale:
        alegere.append(st.checkbox("Date vitale", value=False, key="date_vitale"))
    else:
        st.info("Acest pacient nu are date vitale salvate.")
    
    if rezultate_laborator:
        alegere.append(st.checkbox("Rezultate de laborator", value=False, key="rezultate_laborator"))
    else:
        st.info("Acest pacient nu are rezultate de laborator salvate.")
    
    if scoruri_clinice:
        alegere.append(st.checkbox("Scoruri clinice", value=False, key="scoruri_clinice"))
    else:
        st.info("Acest pacient nu are scoruri clinice salvate.")

    if st.session_state.role in ["doctor", "nurse", "admin"]:
        alegere.append(st.checkbox("Jurnal de acces", value=False, key="jurnal_acces"))
    
    if not alegere:
        st.info("Selectează cel puțin o opțiune pentru a exporta datele.")
        return

    # Convertim la DataFrame
    data = []
    if st.session_state.get("date_pacient", True):
        for p in pacienti:
            if p.patient_id == patient_id:
                data.append({
                    "ID pacient": p.patient_id,
                    "Nume": p.pseudonym,
                    "Data nașterii": p.date_of_birth.strftime("%Y-%m-%d") if p.date_of_birth else "",
                    "Gen": p.gender,
                    "Creat la": p.created_at.strftime("%Y-%m-%d %H:%M") if p.created_at else ""
                })

    if st.session_state.get("date_vitale", True):
        for vs in date_vitale:
            data.append({
                "ID pacient": vs.patient_id,
                "Ritmul cardiac": vs.heart_rate,
                "Saturația în oxigen (SpO2)": vs.spo2,
                "Temperatura": vs.temperature,
                "Timestamp": vs.timestamp.strftime("%Y-%m-%d %H:%M") if vs.timestamp else "",
                "Sursa": vs.source
            })

    if st.session_state.get("rezultate_laborator", True):
        for lr in rezultate_laborator:
            data.append({
                "ID pacient": lr.patient_id,
                "Test": lr.test_name,
                "Valoare": lr.value,
                "Unități": lr.units,
                "Interval de referință": lr.reference_range,
                "Timestamp": lr.timestamp.strftime("%Y-%m-%d %H:%M") if lr.timestamp else ""
            })

    if st.session_state.get("scoruri_clinice", True):
        for cs in scoruri_clinice:
            data.append({
                "ID pacient": cs.patient_id,
                "Tip scor": cs.score_type,
                "Valoare scor": cs.score_value,
                "Timestamp": cs.timestamp.strftime("%Y-%m-%d %H:%M") if cs.timestamp else ""
            })

    if st.session_state.get("jurnal_acces", True) and access_logs:
        for log in access_logs:
            data.append({
                "ID pacient": log["patient_id"],
                "Utilizator": log["user_name"],
                "Rol utilizator": log["user_role"],
                "Tip eveniment": log["event_type"],
                "Timestamp": log["timestamp"]
            })

    df = pd.DataFrame(data)
    if df.empty:
        st.warning("Nu există date de exportat pentru selecția făcută.")
        return

    # Alegem formatul de export
    format_export = st.radio("Selectează formatul pentru export:", ["CSV", "JSON"])

    if format_export == "CSV":
        csv = df.to_csv(index=False, encoding="utf-8-sig")
        download = st.download_button(
            label="Descarcă CSV",
            data=csv,
            file_name=f"{patient_id}_{pseudonym}_data_{datetime.datetime.now()}.csv",
            mime="text/csv"
        )
        if download:
            log_event(
                user_name=st.session_state.username,
                user_role=st.session_state.role,
                patient_id=patient_id,
                event_type="export_csv"
            )
            st.success("CSV descărcat cu succes!")
    else:
        json_data = df.to_json(orient="records", lines=True, force_ascii=False)
        download = st.download_button(
            label="Descarcă JSON",
            data=json_data,
            file_name=f"{patient_id}_{pseudonym}_data_{datetime.datetime.now()}.json",
            mime="application/json"
        )
        if download:
            log_event(
                user_name=st.session_state.username,
                user_role=st.session_state.role,
                patient_id=patient_id,
                event_type="export_json"
            )
            st.success("JSON descărcat cu succes!")

    db.close()
