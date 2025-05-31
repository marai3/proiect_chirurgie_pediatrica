import streamlit as st
from sqlalchemy.orm import Session
import os, sys
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.database import Patient, ClinicalScore, LabResult,VitalSigns, SessionLocal
from blockchain.MedicalLog import log_event

def delete_patient_data():
    st.title("Ștergere date pacient")

    db = SessionLocal()

    pacienti = db.query(Patient).order_by(Patient.patient_id).all()
    if not pacienti:
        st.warning("Nu există pacienți în baza de date.")
        return
    
    pacient_selectat = st.selectbox("Selectează pacientul", pacienti, format_func=lambda p: f"{p.patient_id} - {p.pseudonym}")

    delete_option = st.radio(
        "Șterge datele asociate cu pacientul selectat:",
        ["Pacient complet", "Rezultate de laborator", "Scoruri clinice"],
        horizontal=True
    )

    if delete_option == "Pacient complet":
        st.warning("Această acțiune va șterge toate datele asociate cu pacientul selectat, inclusiv scorurile clinice și rezultatele de laborator.")
        st.warning("Aceasta actiune este ireversibila!")

        st.write("---")
        st.subheader("Date pacient:")
        st.write(f"ID pacient: {pacient_selectat.patient_id}")
        st.write(f"Pseudonim: {pacient_selectat.pseudonym}")
        st.write(f"Data nașterii: {pacient_selectat.date_of_birth}")
        st.write(f"Gen: {pacient_selectat.gender}")

        st.write("---")
        st.subheader("Rezultate de laborator:")
        if(db.query(LabResult).filter(LabResult.patient_id == pacient_selectat.patient_id).count() == 0):
            st.info("Nu există rezultate de laborator pentru acest pacient.")
        else:
            rezultate = db.query(LabResult).filter(LabResult.patient_id == pacient_selectat.patient_id).all()
            rezultate_df = pd.DataFrame([{
                "Test": r.test_name,
                "Valoare": r.value,
                "Unitate": r.units,
                "Interval de referință": r.reference_range,
                "Data rezultat": r.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            } for r in rezultate])
            st.dataframe(rezultate_df)
        
        st.write("---")
        st.subheader("Scoruri clinice:")
        if(db.query(ClinicalScore).filter(ClinicalScore.patient_id == pacient_selectat.patient_id).count() == 0):
            st.info("Nu există scoruri clinice pentru acest pacient.")
        else:
            scoruri = db.query(ClinicalScore).filter(ClinicalScore.patient_id == pacient_selectat.patient_id).all()
            scoruri_df = pd.DataFrame([{
                "Scor": s.score_type,
                "Valoare": s.score_value,
                "Data scor": s.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            } for s in scoruri])
            st.dataframe(scoruri_df)

        st.write("---")
        if st.button("Șterge toate datele asociate cu acest pacient", key="delete_all"):
            db.query(ClinicalScore).filter_by(patient_id=pacient_selectat.patient_id).delete()
            db.query(LabResult).filter_by(patient_id=pacient_selectat.patient_id).delete()
            db.query(VitalSigns).filter_by(patient_id=pacient_selectat.patient_id).delete()
            db.query(Patient).filter_by(patient_id=pacient_selectat.patient_id).delete()
            db.commit()
            log_event(st.session_state.username, st.session_state.role, pacient_selectat.patient_id, "ștergere pacient")
            st.success(f"Pacientul {pacient_selectat.pseudonym} și toate datele asociate au fost șterse.")
            return
        
    elif delete_option == "Rezultate de laborator":
        st.warning("Această acțiune va șterge toate rezultatele de laborator asociate cu pacientul selectat.")
        st.write("---")
        st.subheader("Rezultate de laborator:")
        
        rezultate = db.query(LabResult).filter(LabResult.patient_id == pacient_selectat.patient_id).all()
        if not rezultate:
            st.info("Nu există rezultate de laborator pentru acest pacient.")
            return
        
        rezultate_df = pd.DataFrame([{
            "Test": r.test_name,
            "Valoare": r.value,
            "Unitate": r.units,
            "Interval de referință": r.reference_range,
            "Data rezultat": r.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        } for r in rezultate])
        st.dataframe(rezultate_df)

        if st.button("Șterge toate rezultatele de laborator pentru acest pacient", key="delete_lab_results"):
            db.query(LabResult).filter_by(patient_id=pacient_selectat.patient_id).delete()
            db.commit()
            log_event(st.session_state.username, st.session_state.role, pacient_selectat.patient_id, "ștergere rezultat laborator")
            st.success(f"Rezultatele de laborator pentru {pacient_selectat.pseudonym} au fost șterse.")
        
    elif delete_option == "Scoruri clinice":
        st.warning("Această acțiune va șterge toate scorurile clinice asociate cu pacientul selectat.")
        st.write("---")
        st.subheader("Scoruri clinice:")
        
        scoruri = db.query(ClinicalScore).filter(ClinicalScore.patient_id == pacient_selectat.patient_id).all()
        if not scoruri:
            st.info("Nu există scoruri clinice pentru acest pacient.")
            return
        
        scoruri_df = pd.DataFrame([{
            "Scor": s.score_type,
            "Valoare": s.score_value,
            "Data scor": s.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        } for s in scoruri])
        st.dataframe(scoruri_df)

        if st.button("Șterge toate scorurile clinice pentru acest pacient", key="delete_clinical_scores"):
            db.query(ClinicalScore).filter_by(patient_id=pacient_selectat.patient_id).delete()
            db.commit()
            log_event(st.session_state.username, st.session_state.role, pacient_selectat.patient_id, "ștergere scor clinic")
            st.success(f"Scorurile clinice pentru {pacient_selectat.pseudonym} au fost șterse.")
