import streamlit as st
from datetime import datetime
import pandas as pd
#from home import render_sidebar

def pagina_adauga_pacient():
    if st.session_state.role not in ["doctor", "nurse"]:
        st.warning("Nu aveți permisiuni pentru această secțiune")
        return

    st.title("Adăugare Pacient Nou")
    st.write("---")
    
    with st.form("form_pacient", clear_on_submit=True):
        cols = st.columns(2)
        
        with cols[0]:
            patient_id = st.text_input("ID Pacient*")
            pseudonym = st.text_input("Nume*")
            
        with cols[1]:
            date_of_birth = st.date_input("Data nașterii*", max_value=datetime.now())
            gender = st.selectbox("Gen*", ["Masculin", "Feminin", "Altul"])
        
        submitted = st.form_submit_button("Salvează Pacient")
        
        if submitted:
            if not all([patient_id, pseudonym, date_of_birth, gender]):
                st.error("Completați câmpurile obligatorii (*)")
            else:
                st.success(f"Pacient {pseudonym} înregistrat cu succes!")
                st.balloons()
