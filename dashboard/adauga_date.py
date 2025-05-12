import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from home import render_sidebar

render_sidebar()
st.title("Adaugă date vitale")
st.write("Completează formularul de mai jos pentru a adăuga date vitale pentru un pacient.")
st.write("Datele vor fi salvate în format JSON și CSV.")
st.write("Atenție: Asigură-te că datele sunt corecte înainte de a le trimite.")
st.write("Pentru a vizualiza datele vitale, accesați secțiunea corespunzătoare din aplicație.")
st.write("Pentru a exporta datele, accesați secțiunea corespunzătoare din aplicație.")
st.write("Pentru a vizualiza graficele, accesați secțiunea corespunzătoare din aplicație.")
st.write("Pentru a vizualiza alertele, accesați secțiunea corespunzătoare din aplicație.")

