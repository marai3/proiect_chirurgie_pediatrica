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

    st.title("Lista pacienților")

    # Căutare
    search_term = st.text_input("Caută după nume sau cod pacient (ID):").lower()

    # Preluăm pacienții
    db = SessionLocal()
    patients = db.query(Patient).all()

    # Convertim în DataFrame
    data = [
        {
            "ID": p.patient_id,
            "Nume": p.pseudonym,
            "Data nașterii": p.date_of_birth.strftime("%Y-%m-%d") if p.date_of_birth else "",
            "Gen": p.gender,
            "Creat la": p.created_at.strftime("%Y-%m-%d %H:%M")
        }
        for p in patients
    ]

    df = pd.DataFrame(data)

    # Fill NaN values with an empty string and convert to strings
    df["ID"] = df["ID"].fillna("").astype(str)
    df["Nume"] = df["Nume"].fillna("").astype(str)

    # Filtrare după search bar
    if search_term:
        df = df[df["ID"].str.lower().str.contains(search_term) | df["Nume"].str.lower().str.contains(search_term)]

    # Afișăm tabelul
    st.dataframe(df, use_container_width=True)
