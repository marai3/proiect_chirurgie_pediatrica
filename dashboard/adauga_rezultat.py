import streamlit as st
from datetime import datetime
import pandas as pd
#from home import render_sidebar

def pagina_adauga_rezultate():
    if st.session_state.role not in ["doctor", "nurse"]:
        st.warning("Nu aveți permisiuni pentru această secțiune")
        return

    st.title("Adăugare Rezultate Laborator")
    st.write("---")
    
    with st.form("form_lab_results", clear_on_submit=True):
        patient_id = st.text_input("ID Pacient*")
        
        cols = st.columns(2)
        with cols[0]:
            test_name = st.selectbox("Test*", ["CRP", "Leucocite", "Hemoglobina", "ALT", "AST", "Glicemie", "Altele"])
            value = st.number_input("Valoare*", step=0.1)
            
        with cols[1]:
            units = st.text_input("Unitate*")
            reference_range = st.text_input("Interval de referință")
        
        data_rezultat = st.date_input("Data rezultatului*", value=datetime.now())
        
        submitted = st.form_submit_button("Salvează Rezultat")
        
        if submitted:
            if not all([patient_id, test_name, value, units, data_rezultat]):
                st.error("Completați câmpurile obligatorii (*)")
            else:
                st.success("Rezultat laborator înregistrat cu succes!")
                st.balloons()