import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.database import SessionLocal, Patient

def pagina_vizualizare():
    # Interfață Streamlit
    st.title("Vizualizare Pacienți")
    st.write("---")

    # Search bar
    search_term = st.text_input("Caută după nume sau ID pacient:").strip().lower()

    # Conectare la DB
    db = SessionLocal()
    patients = db.query(Patient).all()

    # Structurăm datele într-un DataFrame
    data = [
        {
            "ID": p.patient_id,
            "Nume": p.pseudonym,
            "Data nașterii": p.date_of_birth.strftime("%Y-%m-%d") if p.date_of_birth else "",
            "Gen": p.gender,
            "Creat la": p.created_at.strftime("%Y-%m-%d %H:%M") if p.created_at else ""
        }
        for p in patients
    ]
    df = pd.DataFrame(data)

    # Filtrare după search bar
    if search_term:
        df = df[df["Nume"].str.lower().str.contains(search_term) | df["ID"].astype(str).str.contains(search_term)]

    st.subheader("Lista pacienților")
    st.dataframe(df, use_container_width=True)

    # Selectare pacient din tabel
    if not df.empty:
        ids = df["ID"].tolist()
        selected_id = st.radio("Selectează un pacient pentru detalii:", ids)

        # Detalii despre pacientul selectat
        patient = db.query(Patient).filter(Patient.patient_id == selected_id).first()

        if patient:
            st.write("---")
            st.subheader("Informații generale:")
            st.write(f"**ID:** {patient.patient_id}")
            st.write(f"**Nume:** {patient.pseudonym}")
            st.write(f"**Data nașterii:** {patient.date_of_birth}")
            st.write(f"**Gen:** {patient.gender}")
            st.write(f"**Creat la:** {patient.created_at}")

            st.write("---")
            st.subheader("Rezultate de laborator:")

            if patient.labs:
                lab_data = [
                    {
                        "Test": l.test_name,
                        "Valoare": l.value,
                        "Unități": l.units,
                        "Interval de referință": l.reference_range,
                        "Data": l.timestamp.strftime("%Y-%m-%d %H:%M")
                    }
                    for l in patient.labs
                ]
                df_labs = pd.DataFrame(lab_data)
                st.dataframe(df_labs, use_container_width=True)
            else:
                st.info("Nu există rezultate de laborator pentru acest pacient.")

            st.write("---")
            st.subheader("Scoruri clinice:")

            if patient.scores:
                score_data = [
                    {
                        "Tip scor": s.score_type,
                        "Valoare": s.score_value,
                        "Data": s.timestamp.strftime("%Y-%m-%d %H:%M")
                    }
                    for s in patient.scores
                ]
                df_scores = pd.DataFrame(score_data)
                st.dataframe(df_scores, use_container_width=True)
            else:
                st.info("Nu există scoruri clinice pentru acest pacient.")
        else:
            st.error("Pacientul nu a fost găsit.")
    else:
        st.warning("Nu există pacienți care corespund căutării.")
