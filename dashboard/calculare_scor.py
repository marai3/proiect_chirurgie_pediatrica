import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.database import SessionLocal, Patient, ClinicalScore, VitalSigns

def pagina_scor():

    st.title("Calculare Scoruri Clinice")
    st.write("---")
    
    db = SessionLocal()
    pacienti = db.query(Patient).all()
    if not pacienti:
        st.warning("Nu există pacienți în baza de date.")
        return
    
    optiuni = {f"{p.pseudonym} ({p.patient_id})": p.patient_id for p in pacienti}
    selectie = st.selectbox("Selectează pacientul:", list(optiuni.keys()))
    patient_id = optiuni[selectie]
    pseudonym = [p.pseudonym for p in pacienti if p.patient_id == patient_id][0]

    st.selectbox("Selectează scorul clinic:", ["pSOFA", "NEWS","PEWS", "PRISM", "GCS Pediatric"], key="scor_selectat")
    st.write("---")

    st.subheader("Date vitale")
    date_vitale = db.query(VitalSigns).filter(VitalSigns.patient_id == patient_id).order_by(VitalSigns.timestamp).all()
    if not date_vitale:
        st.warning("Acest pacient nu are date vitale salvate.")

    st.subheader("Formular de calculare a scorului")

    if st.session_state.get("scor_selectat") == "NEWS":
        with st.form("NEWS"):
            st.markdown("**NEWS (National Early Warning Score)**")
            st.info("Completează datele pentru a calcula scorul NEWS.")
            
            col1, col2 = st.columns(2)
            with col1:
                rr = st.number_input("Frecvența respiratorie (rpm)", min_value=0, value=16)
                spo2 = st.number_input("Saturația oxigenului (%)", min_value=50, max_value=100, value=97)
                temp = st.number_input("Temperatura (°C)", min_value=30.0, max_value=45.0, value=36.5)
                conscious = st.selectbox("Nivel de conștiență (AVPU)", ["Alert", "Voce", "Durere", "Nereactiv"])
            with col2:
                hr = st.number_input("Frecvența cardiacă (bpm)", min_value=0, value=80)
                sbp = st.number_input("Tensiunea arterială sistolică (mmHg)", min_value=0, value=120)
                ox = st.checkbox("Primește oxigen suplimentar?", value=False)

            submit = st.form_submit_button("Calculează scorul")

            if submit:
                news_score = 0

                # Respirație
                if rr <= 8:
                    news_score += 3
                elif 9 <= rr <= 11 or 21 <= rr <= 24:
                    news_score += 2
                elif 12 <= rr <= 20:
                    news_score += 0
                elif rr >= 25:
                    news_score += 3

                # Saturație oxigen
                if spo2 <= 91:
                    news_score += 3
                elif 92 <= spo2 <= 93:
                    news_score += 2
                elif 94 <= spo2 <= 95:
                    news_score += 1
                elif spo2 >= 96:
                    news_score += 0

                # Temperatura
                if temp < 35:
                    news_score += 3
                elif 35 <= temp <= 36:
                    news_score += 1
                elif 36.1 <= temp <= 38.0:
                    news_score += 0
                elif 38.1 <= temp <= 39.0:
                    news_score += 1
                elif temp > 39.0:
                    news_score += 2

                # Puls
                if hr <= 40:
                    news_score += 3
                elif 41 <= hr <= 50 or 91 <= hr <= 110:
                    news_score += 1
                elif 51 <= hr <= 90:
                    news_score += 0
                elif 111 <= hr <= 130:
                    news_score += 2
                elif hr > 130:
                    news_score += 3

                # Presiune sistolică
                if sbp <= 90:
                    news_score += 3
                elif 91 <= sbp <= 100:
                    news_score += 2
                elif 101 <= sbp <= 110:
                    news_score += 1
                elif 111 <= sbp <= 219:
                    news_score += 0
                elif sbp >= 220:
                    news_score += 3

                # Nivel conștiență
                if conscious != "Alert":
                    news_score += 3

                # Oxigen suplimentar
                if ox:
                    news_score += 2

                st.success(f"Scorul NEWS este: {news_score}")
                
                #salvare scor in baza de date
                scor = ClinicalScore(
                    patient_id=patient_id,
                    score_type="NEWS",
                    score_value=news_score
                )
                db.add(scor)
                db.commit()
                db.refresh(scor)
                db.close()

                if news_score >= 7:
                    st.error("Risc major! intervenție imediată necesară.")
                elif 5 <= news_score <= 6:
                    st.warning("Risc moderat! evaluare urgentă.")
                elif 1 <= news_score <= 4:
                    st.info("Monitorizare crescută necesară.")
                else:
                    st.success("Stabil! Monitorizare standard.")


    if st.session_state.get("scor_selectat") == "PEWS":
        with st.form("PEWS"):
            st.markdown("**PEWS - Pediatric Early Warning Score**")
            st.info("Completează datele pentru a calcula scorul PEWS.")

            col1, col2 = st.columns(2)
            with col1:
                hr = st.number_input("Frecvența cardiacă (bpm)", min_value=0, value=100)
                rr = st.number_input("Frecvența respiratorie (rpm)", min_value=0, value=20)
                spo2 = st.number_input("Saturația oxigenului (%)", min_value=0, max_value=100, value=98)
            with col2:
                sbp = st.number_input("Tensiunea arterială sistolică (mmHg)", min_value=0, value=100)
                avpu = st.selectbox("Nivel de conștiență (AVPU)", ["Alert", "Voce", "Durere", "Nereactiv"])
                efort_resp = st.selectbox("Efort respirator", ["Normal", "Ușor crescut", "Moderate", "Sever"])

            submit = st.form_submit_button("Calculează scorul")

            if submit:
                pews_score = 0

                # Frecvența cardiacă
                if hr < 60 or hr > 160:
                    pews_score += 3
                elif 60 <= hr <= 80 or 140 <= hr <= 160:
                    pews_score += 2
                elif 81 <= hr <= 139:
                    pews_score += 0

                # Frecvența respiratorie
                if rr < 10 or rr > 60:
                    pews_score += 3
                elif 10 <= rr <= 20 or 50 <= rr <= 60:
                    pews_score += 2
                elif 21 <= rr <= 49:
                    pews_score += 0

                # Saturația oxigenului
                if spo2 < 90:
                    pews_score += 3
                elif 90 <= spo2 <= 94:
                    pews_score += 2
                elif spo2 > 94:
                    pews_score += 0

                # Nivel de conștiență
                if avpu == "Alert":
                    pews_score += 0
                elif avpu == "Voce":
                    pews_score += 1
                elif avpu == "Durere":
                    pews_score += 2
                elif avpu == "Nereactiv":
                    pews_score += 3

                # Efort respirator
                if efort_resp == "Normal":
                    pews_score += 0
                elif efort_resp == "Ușor crescut":
                    pews_score += 1
                elif efort_resp == "Moderate":
                    pews_score += 2
                elif efort_resp == "Sever":
                    pews_score += 3

                # Tensiunea arterială sistolică
                if sbp < 70:
                    pews_score += 3
                elif 70 <= sbp <= 80:
                    pews_score += 2
                elif sbp > 80:
                    pews_score += 0

                st.success(f"Scorul PEWS este: {pews_score}")

                #salvare scor in baza de date
                scor = ClinicalScore(
                    patient_id=patient_id,
                    score_type="PEWS",
                    score_value=pews_score
                )
                db.add(scor)
                db.commit()
                db.refresh(scor)
                db.close()

                if pews_score >= 6:
                    st.error("Risc major! intervenție imediată necesară.")
                elif 3 <= pews_score <= 5:
                    st.warning("Risc moderat! evaluare urgentă.")
                else:
                    st.success("Stabil! monitorizare standard.")


    if st.session_state.get("scor_selectat") == "PRISM":
        with st.form("PRISM"):
            st.markdown("**PRISM III - Pediatric Risk of Mortality**")
            st.info("Completează parametrii cei mai anormali în primele 24h de la internare.")

            col1, col2 = st.columns(2)
            with col1:
                sbp = st.number_input("Tensiune sistolică (mmHg)", min_value=0, value=90)
                temp = st.number_input("Temperatură (°C)", min_value=30.0, max_value=45.0, value=36.5)
                gcs = st.number_input("Scor GCS", min_value=3, max_value=15, value=15)
                pupil_fix = st.selectbox("Pupile fixe și dilatate?", ["Nu", "Unilateral", "Bilateral"])
                po2 = st.number_input("PaO₂ (mmHg)", min_value=10.0, value=80.0)
            with col2:
                pco2 = st.number_input("PaCO₂ (mmHg)", min_value=10.0, value=40.0)
                ph = st.number_input("pH", min_value=6.5, max_value=8.0, value=7.4)
                glucoza = st.number_input("Glucoză (mg/dL)", min_value=20.0, value=100.0)
                bili = st.number_input("Bilirubină totală (mg/dL)", min_value=0.0, value=1.2)
                creat = st.number_input("Creatinină serică (mg/dL)", min_value=0.1, value=0.8)

            submit = st.form_submit_button("Calculează scorul PRISM")

            if submit:
                prism_score = 0

                # SBP
                if sbp < 65:
                    prism_score += 4
                elif 65 <= sbp < 75:
                    prism_score += 2

                # Temperatura
                if temp < 33 or temp > 40:
                    prism_score += 3
                elif 33 <= temp <= 35 or 39 <= temp <= 40:
                    prism_score += 1

                # GCS
                if gcs < 5:
                    prism_score += 5
                elif gcs < 8:
                    prism_score += 3
                elif gcs < 11:
                    prism_score += 2

                # Pupile
                if pupil_fix == "Unilateral":
                    prism_score += 3
                elif pupil_fix == "Bilateral":
                    prism_score += 5

                # PaO₂
                if po2 < 40:
                    prism_score += 3
                elif 40 <= po2 < 60:
                    prism_score += 2

                # PaCO₂
                if pco2 > 60:
                    prism_score += 2

                # pH
                if ph < 7.1 or ph > 7.7:
                    prism_score += 3
                elif ph < 7.2 or ph > 7.6:
                    prism_score += 2

                # Glucoză
                if glucoza < 40 or glucoza > 500:
                    prism_score += 3

                # Bilirubină
                if bili > 15:
                    prism_score += 3
                elif 10 <= bili <= 15:
                    prism_score += 2

                # Creatinină
                if creat > 4:
                    prism_score += 3
                elif 2 <= creat <= 4:
                    prism_score += 2

                # Interpretare scor
                st.success(f"Scorul PRISM III este: {prism_score}")

                #salvare scor in baza de date
                scor = ClinicalScore(
                    patient_id=patient_id,
                    score_type="PRISM",
                    score_value=prism_score
                )
                db.add(scor)
                db.commit()
                db.refresh(scor)
                db.close()

                if prism_score >= 30:
                    st.error("Risc extrem! mortalitate foarte ridicată.")
                elif 20 <= prism_score < 30:
                    st.warning("Risc mare! supraveghere intensivă.")
                elif 10 <= prism_score < 20:
                    st.info("Risc moderat! monitorizare atentă.")
                else:
                    st.success("Risc scăzut.")


    if st.session_state.get("scor_selectat") == "GCS Pediatric":
        with st.form("GCS Pediatric"):
            st.markdown("**GCS Pediatric - Glasgow Coma Scale (adaptată)**")
            st.info("Evaluează conștiența copilului pe baza răspunsurilor clinice.")

            col1, col2, col3 = st.columns(3)

            with col1:
                ocular = st.radio(
                    "Răspuns ocular",
                    [
                        "4 - Deschide spontan ochii",
                        "3 - La comanda vocală",
                        "2 - La stimul dureros",
                        "1 - Niciun răspuns"
                    ],
                    key="ocular_radio"
                )
            with col2:
                verbal = st.radio(
                    "Răspuns verbal",
                    [
                        "5 - Răspuns adecvat (cuvinte/coerență)",
                        "4 - Confuz sau agitat",
                        "3 - Cuvinte nepotrivite",
                        "2 - Sunete, gemete",
                        "1 - Fără răspuns verbal"
                    ],
                    key="verbal_radio"
                )
            with col3:
                motor = st.radio(
                    "Răspuns motor",
                    [
                        "6 - Execută comenzi",
                        "5 - Localizează durerea",
                        "4 - Retragere la durere",
                        "3 - Flexie anormală (decorticare)",
                        "2 - Extensie anormală (decerebrare)",
                        "1 - Niciun răspuns motor"
                    ],
                    key="motor_radio"
                )

            submit = st.form_submit_button("Calculează scorul GCS Pediatric")

            if submit:
                ocular_score = int(ocular.split(" - ")[0])
                verbal_score = int(verbal.split(" - ")[0])
                motor_score = int(motor.split(" - ")[0])

                gcs_total = ocular_score + verbal_score + motor_score

                st.success(f"Scorul GCS Pediatric este: {gcs_total}")

                #salvare scor in baza de date
                scor = ClinicalScore(
                    patient_id=patient_id,
                    score_type="GCS Pediatric",
                    score_value=gcs_total
                )
                db.add(scor)
                db.commit()
                db.refresh(scor)
                db.close()

                if gcs_total <= 8:
                    st.error("Comă severă! intubație sau terapie intensivă.")
                elif 9 <= gcs_total <= 12:
                    st.warning("Stare intermediară! monitorizare neurologică.")
                elif gcs_total >= 13:
                    st.success("Nivel de conștiență normal sau ușor afectat.")

        
    
    if st.session_state.get("scor_selectat") == "pSOFA":
        with st.form("pSOFA"):
            st.markdown("**pSOFA - Pediatric Sequential Organ Failure Assessment**")
            st.info("Completează datele pentru a calcula scorul pSOFA.")

            col1, col2 = st.columns(2)
            with col1:
                pao2_fio2 = st.number_input("Raport PaO₂/FiO₂", min_value=0, value=300)
                trombocite = st.number_input("Trombocite (10^3/µL)", min_value=0, value=150)
                bilirubina = st.number_input("Bilirubină totală (mg/dL)", min_value=0.0, value=1.0)
            with col2:
                sbp = st.number_input("Tensiunea arterială sistolică (mmHg)", min_value=0, value=100)
                gcs = st.number_input("Scor GCS", min_value=3, max_value=15, value=15)
                creatinina = st.number_input("Creatinină serică (mg/dL)", min_value=0.0, value=0.5)

            submit = st.form_submit_button("Calculează scorul")

            if submit:
                psofa_score = 0

                # PaO₂/FiO₂
                if pao2_fio2 < 100:
                    psofa_score += 4
                elif 100 <= pao2_fio2 < 200:
                    psofa_score += 3
                elif 200 <= pao2_fio2 < 300:
                    psofa_score += 2
                elif 300 <= pao2_fio2 < 400:
                    psofa_score += 1
                else:
                    psofa_score += 0

                # Trombocite
                if trombocite < 20:
                    psofa_score += 4
                elif 20 <= trombocite < 50:
                    psofa_score += 3
                elif 50 <= trombocite < 100:
                    psofa_score += 2
                elif 100 <= trombocite < 150:
                    psofa_score += 1
                else:
                    psofa_score += 0

                # Bilirubină
                if bilirubina >= 12.0:
                    psofa_score += 4
                elif 6.0 <= bilirubina < 12.0:
                    psofa_score += 3
                elif 2.0 <= bilirubina < 6.0:
                    psofa_score += 2
                elif 1.2 <= bilirubina < 2.0:
                    psofa_score += 1
                else:
                    psofa_score += 0

                # Tensiunea arterială sistolică
                if sbp < 70:
                    psofa_score += 4
                elif 70 <= sbp < 80:
                    psofa_score += 3
                elif 80 <= sbp < 100:
                    psofa_score += 2
                elif 100 <= sbp < 110:
                    psofa_score += 1
                else:
                    psofa_score += 0

                # GCS
                if gcs < 6:
                    psofa_score += 4
                elif 6 <= gcs < 9:
                    psofa_score += 3
                elif 9 <= gcs < 12:
                    psofa_score += 2
                elif 12 <= gcs < 15:
                    psofa_score += 1
                else:
                    psofa_score += 0

                # Creatinină
                if creatinina >= 5.0:
                    psofa_score += 4
                elif 3.5 <= creatinina < 5.0:
                    psofa_score += 3
                elif 2.0 <= creatinina < 3.5:
                    psofa_score += 2
                elif 1.2 <= creatinina < 2.0:
                    psofa_score += 1
                else:
                    psofa_score += 0

                st.success(f"Scorul pSOFA este: {psofa_score}")

                #salvare scor in baza de date
                scor = ClinicalScore(
                    patient_id=patient_id,
                    score_type="pSOFA",
                    score_value=psofa_score
                )
                db.add(scor)
                db.commit()
                db.refresh(scor)
                db.close()

                if psofa_score >= 15:
                    st.error("Risc major! intervenție imediată necesară.")
                elif 5 <= psofa_score < 15:
                    st.warning("Risc moderat! evaluare urgentă.")
                else:
                    st.success("Stabil! monitorizare standard.")


