import streamlit as st
from sqlalchemy.orm import Session
from app.main import SessionLocal, Patient, ClinicalScore, LabResult  

def delete_patient_data():
    st.title("Ștergere date pacient")

    delete_option = st.selectbox(
        "Alege ce vrei să ștergi:",
        ["Pacient complet", "Doar scoruri clinice", "Doar rezultate de laborator"]
    )

    with SessionLocal() as db:
        patients = db.query(Patient).all()

        if not patients:
            st.warning("Nu există pacienți în baza de date.")
            return

        patient_names = [f"{p.patient_id} - {p.pseudonym}" for p in patients]
        selected = st.selectbox("Selectează pacientul:", patient_names)

        selected_id = int(selected.split(" - ")[0])
        patient = db.query(Patient).filter_by(patient_id=selected_id).first()

        if st.button("Șterge"):
            if delete_option == "Pacient complet":
                db.query(ClinicalScore).filter_by(patient_id=patient.patient_id).delete()
                db.query(LabResult).filter_by(patient_id=patient.patient_id).delete()
                db.query(Patient).filter_by(patient_id=patient.patient_id).delete()
                st.success(f"Pacientul {patient.pseudonym} și toate datele asociate au fost șterse.")
            elif delete_option == "Doar scoruri clinice":
                deleted = db.query(ClinicalScore).filter_by(patient_id=patient.patient_id).delete()
                if deleted:
                    st.success(f"Scorurile clinice pentru {patient.pseudonym} au fost șterse.")
                else:
                    st.info(f"Nu există scoruri clinice pentru acest pacient.")
            elif delete_option == "Doar rezultate de laborator":
                deleted = db.query(LabResult).filter_by(patient_id=patient.patient_id).delete()
                if deleted:
                    st.success(f"Rezultatele de laborator pentru {patient.pseudonym} au fost șterse.")
                else:
                    st.info(f"Nu există rezultate de laborator pentru acest pacient.")
            db.commit()

if __name__ == "__main__":
    delete_patient_data()
