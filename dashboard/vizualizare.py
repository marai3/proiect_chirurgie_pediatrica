import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from home import render_sidebar
import datetime
#from .database import Patient 

# Configurare conexiune la baza de date
DATABASE_URL = "postgresql://postgres:password@localhost/clinica"  # ← modifică dacă e nevoie
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Funcție pentru a prelua pacienții
##def get_all_patients(session):
   ## return session.query(Patient).all()

# Interfață Streamlit
st.set_page_config(page_title="Pacienți - Clinica", layout="wide")
st.title("Lista pacienților")

# Căutare
search_term = st.text_input("🔍 Caută după nume sau cod pacient (ID):").lower()

# Deschidem sesiunea SQLAlchemy
session = SessionLocal()

# Preluăm pacienții
patients = get_all_patients(session)

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

# Filtrare după search bar
if search_term:
    df = df[df["ID"].str.lower().str.contains(search_term) | df["Nume"].str.lower().str.contains(search_term)]

# Afișăm tabelul
st.dataframe(df, use_container_width=True)

# Cleanup
session.close()
