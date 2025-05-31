import streamlit as st
from sqlalchemy.orm import Session
import sys, os
import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.database import SessionLocal, Patient, LabResult, ClinicalScore
from blockchain.MedicalLog import log_event

def modificare_date():
    st.title("Modificare date")
    db = SessionLocal()

    entitate = st.radio("Ce dorești să modifici?", ["Pacient", "Rezultat de laborator"])

    if entitate == "Pacient":
        pacienti = db.query(Patient).order_by(Patient.patient_id).all()
        pacient_selectat = st.selectbox("Selectează pacientul", pacienti, format_func=lambda p: f"{p.patient_id} - {p.pseudonym}")

        with st.form("form_pacient"):
            cols = st.columns(2)
            pseudonym = st.text_input("Pseudonim*", value=pacient_selectat.pseudonym)

            with cols[0]:
                date_of_birth = st.date_input("Data nașterii*", max_value=datetime.datetime.now(), value=pacient_selectat.date_of_birth)
                
            with cols[1]:
                gender = st.selectbox("Gen*", ["Masculin", "Feminin", "Altul"], index=["Masculin", "Feminin", "Altul"].index(pacient_selectat.gender))
        
            submit = st.form_submit_button("Modifică")

            if submit:
                if not pseudonym or not date_of_birth or not gender:
                    st.error("Completați câmpurile obligatorii (*)")
                else:
                    db.query(Patient).filter(Patient.patient_id == pacient_selectat.patient_id).update({
                        Patient.pseudonym: pseudonym,
                        Patient.date_of_birth: date_of_birth,
                        Patient.gender: gender
                    })
                    db.commit()
                    log_event(st.session_state.username, st.session_state.role, pacient_selectat.patient_id, "modificare date pacient")
                    st.success("Modificare efectuată!")
                    pacienti = db.query(Patient).order_by(Patient.patient_id).all()  # Reîncărcăm lista de pacienți pentru a reflecta modificările

    elif entitate == "Rezultat de laborator":
        pacienti = db.query(Patient).order_by(Patient.patient_id).all()
        pacient_selectat = st.selectbox("Selectează pacientul", pacienti, format_func=lambda p: f"{p.patient_id} - {p.pseudonym}")
        rezultate = db.query(LabResult).filter(LabResult.patient_id == pacient_selectat.patient_id).all()
        if not rezultate:
            st.warning("Nu există rezultate de laborator pentru acest pacient.")
            return
        
        rezultat_selectat = st.selectbox("Selectează rezultatul de laborator", rezultate, format_func=lambda r: f"{r.id} - {r.test_name}")

        with st.form("form_rezultat"):
            cols = st.columns(2)
            with cols[0]:
                test_name = st.selectbox("Test*", ["CRP", "Leucocite", "Hemoglobina", "ALT", "AST", "Glicemie", "Altele"], index=["CRP", "Leucocite", "Hemoglobina", "ALT", "AST", "Glicemie", "Altele"].index(rezultat_selectat.test_name))
                value = st.number_input("Valoare*", step=0.1, value=rezultat_selectat.value)
                
            with cols[1]:
                units = st.text_input("Unitate*", value=rezultat_selectat.units)
                reference_range = st.text_input("Interval de referință", value=rezultat_selectat.reference_range)
        
            data_rezultat = st.date_input("Data rezultatului*", value=rezultat_selectat.timestamp, max_value=datetime.datetime.now())

            submit = st.form_submit_button("Modifică")

            if submit:
                if not test_name or not value or not units or not data_rezultat:
                    st.error("Completați câmpurile obligatorii (*)")
                else:
                    db.query(LabResult).filter(LabResult.id == rezultat_selectat.id).update({
                        LabResult.test_name: test_name,
                        LabResult.value: value,
                        LabResult.units: units,
                        LabResult.reference_range: reference_range,
                        LabResult.timestamp: data_rezultat
                    })
                    db.commit()
                    log_event(st.session_state.username, st.session_state.role, pacient_selectat.patient_id, "modificare rezultat laborator")
                    st.success("Modificare efectuată!")