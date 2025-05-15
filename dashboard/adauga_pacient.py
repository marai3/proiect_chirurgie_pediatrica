import streamlit as st
from datetime import datetime
import pandas as pd

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.database import SessionLocal, Patient

def pagina_adauga_pacient():
    if st.session_state.role not in ["doctor", "nurse", "admin"]:
        st.warning("Nu aveți permisiuni pentru această secțiune")
        return

    st.title("Adăugare Pacient Nou")
    st.write("---")
    
    with st.form("form_pacient", clear_on_submit=True):
        cols = st.columns(2)
        pseudonym = st.text_input("Pseudonim*")

        with cols[0]:
             date_of_birth = st.date_input("Data nașterii*", max_value=datetime.now())
            
        with cols[1]:
            gender = st.selectbox("Gen*", ["Masculin", "Feminin", "Altul"])
        
        submitted = st.form_submit_button("Salvează Pacient")
        
        if submitted:
            if not all([pseudonym, date_of_birth, gender]):
                st.error("Completați câmpurile obligatorii (*)")
            else:
                st.success(f"Pacient {pseudonym} înregistrat cu succes!")
                st.balloons()

                #Saave to database
                db = SessionLocal()
                new_patient = Patient(
                    pseudonym=pseudonym,
                    date_of_birth=date_of_birth,
                    gender=gender,
                    created_at=datetime.now()
                )
                db.add(new_patient)
                db.commit()
                db.refresh(new_patient)
                db.close()
    
