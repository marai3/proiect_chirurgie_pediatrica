import streamlit as st
import requests
from jose import jwt
import grafice as grafice
import adauga_pacient
import adauga_rezultat

def login_form():
    st.title("Autentificare")
    with st.form("login"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Logare")
        if submit:
            r = requests.post("http://127.0.0.1:8000/token", data={"username": username, "password": password})
            if r.status_code == 200:
                token = r.json()["access_token"]
                decoded = jwt.decode(token, "secrettoken2025", algorithms=["HS256"])
                st.session_state.token = token
                st.session_state.username = decoded["sub"]
                st.session_state.role = decoded["role"]
            else:
                st.error("Login eșuat.")
                st.session_state.token = None
                st.session_state.username = None
                st.session_state.role = None

def render_sidebar():
    st.sidebar.title("Navigare")
    if st.sidebar.button("Acasa", key="home"):
        st.session_state.page = "home"
    if st.sidebar.button("Dashboard", key="dashboard"):
        st.session_state.page = "dashboard"
    with st.sidebar.expander("Adaugă Date", expanded=True):
        if st.session_state.role in ["doctor", "nurse"]:
            if st.button("Adaugă Pacient"):
                st.session_state.page = "adauga_pacient"
            if st.button("Adaugă Rezultate"):
                st.session_state.page = "adauga_rezultate"
        else:
            st.warning("Permisiuni insuficiente")
    if st.sidebar.button("Export", key="export"):
        st.session_state.page = "export"
    if st.sidebar.button("Vizualizare", key="vizualizare"):
        st.session_state.page = "vizualizare"
    if st.sidebar.button("Logout", key="logout"):
        st.session_state.username = None
        st.session_state.role = None
        st.session_state.token = None
        st.session_state.page = "login"

def pagina_home():
    st.title("Bine ai venit!")
    st.write(f"Rol: **{st.session_state.role}** | Utilizator: **{st.session_state.username}**")
    st.info("Folosește meniul din stânga pentru a naviga între module.")

if "token" not in st.session_state:
    st.session_state.token = None

if "page" not in st.session_state:
    st.session_state.page = "home"

if st.session_state.token is None:
    login_form()
    st.stop()
else:
    render_sidebar()
    pagina = st.session_state.page

    if pagina == "home":
        pagina_home()
    elif pagina == "dashboard":
        grafice.run_monitorizare()
    elif pagina == "adauga_pacient":
        adauga_pacient.pagina_adauga_pacient()
    elif pagina == "adauga_rezultate":  
        adauga_rezultat.pagina_adauga_rezultate()
        pass
    elif pagina == "export":
        #pagina_export()
        pass
    elif pagina == "logout":
        st.session_state.token = None
        st.session_state.username = None
        st.session_state.role = None
        st.session_state.page = "login"