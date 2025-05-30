import streamlit as st
from sqlalchemy.orm import Session
from app.main import get_db
from app.database import Pacient, LabResult, ClinicalScore
from utils import log_access 

def modificare_date():
    st.title("Modificare date")
    db: Session = next(get_db())

    entitate = st.radio("Ce dorești să modifici?", ["Pacient", "Rezultat de laborator", "Scor clinic"])

    if entitate == "Pacient":
        pacienti = db.query(Pacient).all()
        pacient_selectat = st.selectbox("Selectează pacientul", pacienti, format_func=lambda p: f"{p.id} - {p.nume}")

        atribut = st.radio("Alege atributul de modificat", ["nume", "data_nasterii", "cnp", "istoric", "diagnostic", "telefon", "medicamente", "programare_data", "programare_ora", "doctor"])

        valoare_noua = None
        if atribut in ["nume", "cnp", "istoric", "diagnostic", "telefon", "medicamente", "doctor"]:
            valoare_noua = st.text_input("Introduceți noua valoare:")
        elif atribut == "data_nasterii":
            valoare_noua = st.date_input("Selectați noua dată:")
        elif atribut in ["programare_data"]:
            valoare_noua = st.date_input("Selectează noua dată pentru programare:")
        elif atribut in ["programare_ora"]:
            valoare_noua = st.time_input("Selectează noua oră pentru programare:")

        if st.button("Modifică"):
            setattr(pacient_selectat, atribut, valoare_noua)
            db.commit()
            log_access(db, f"Modificare {atribut} pentru pacientul {pacient_selectat.id}")
            st.success("Modificare efectuată!")

    elif entitate == "Rezultat de laborator":
        rezultate = db.query(LabResult).all()
        rezultat_selectat = st.selectbox("Selectează rezultatul", rezultate, format_func=lambda r: f"{r.id} - {r.tip_test}")

        atribut = st.radio("Alege atributul de modificat", ["tip_test", "valoare", "unitate", "data"])
        if atribut in ["tip_test", "unitate"]:
            valoare_noua = st.text_input("Introduceți noua valoare:")
        elif atribut == "valoare":
            valoare_noua = st.number_input("Introduceți noua valoare:", format="%.2f")
        elif atribut == "data":
            valoare_noua = st.date_input("Selectează noua dată:")

        if st.button("Modifică"):
            setattr(rezultat_selectat, atribut, valoare_noua)
            db.commit()
            log_access(db, f"Modificare {atribut} pentru rezultatul {rezultat_selectat.id}")
            st.success("Modificare efectuată!")

    elif entitate == "Scor clinic":
        scoruri = db.query(ClinicalScore).all()
        scor_selectat = st.selectbox("Selectează scorul", scoruri, format_func=lambda s: f"{s.id} - {s.tip_scor}")

        atribut = st.radio("Alege atributul de modificat", ["tip_scor", "valoare", "data"])
        if atribut == "tip_scor":
            valoare_noua = st.text_input("Introduceți noul tip de scor:")
        elif atribut == "valoare":
            valoare_noua = st.number_input("Introduceți noua valoare:", format="%.2f")
        elif atribut == "data":
            valoare_noua = st.date_input("Selectează noua dată:")

        if st.button("Modifică"):
            setattr(scor_selectat, atribut, valoare_noua)
            db.commit()
            log_access(db, f"Modificare {atribut} pentru scorul {scor_selectat.id}")
            st.success("Modificare efectuată!")
