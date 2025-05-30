from fastapi import FastAPI, Form, HTTPException, Depends
from pydantic import BaseModel
from passlib.context import CryptContext
import pandas as pd
from sqlalchemy.orm import Session
from .auth import create_access_token
from .database import  SessionLocal, Patient, VitalSigns, LabResult, ClinicalScore, User
from datetime import datetime

app = FastAPI()

pwd_context = CryptContext(schemes=["bcrypt"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#endpoint pentru a obtine tokenul de acces
@app.post("/token")
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()

    if not user or not pwd_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Credentiale incorecte")
    
    token = create_access_token(data={"sub": username, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}

#endpoint pentru a adauga pacienti
@app.post("/patients/")
def add_patient(patient_id: str, pseudonym: str, date_of_birth: str, gender: str, created_at: datetime, db: Session = Depends(get_db)):
    if(patient_id is None or pseudonym is None or date_of_birth is None or gender is None or created_at is None):
        raise HTTPException(status_code=400, detail="Toate campurile sunt necesare")
    
    elif(db.query(Patient).filter(Patient.patient_id == patient_id).first() is not None):
        raise HTTPException(status_code=400, detail="Pacientul exista deja")
    
    else:
        new_patient = Patient(
            patient_id=patient_id,
            pseudonym=pseudonym,
            date_of_birth=date_of_birth,
            gender=gender,
            created_at=created_at)
        db.add(new_patient)
        db.commit()
        db.refresh(new_patient)
        return {"message": "Pacient adaugat cu succes", "patient_id": new_patient.patient_id}

 #endpoint pentru a vizualiza un pacient    
@app.get("/patients/{patient_id}")
def get_patient(patient_id: str, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    
    if not patient:
        raise HTTPException(status_code=404, detail="Pacientul nu a fost gasit")
    
    return {
        "patient_id": patient.patient_id,
        "pseudonym": patient.pseudonym,
        "date_of_birth": patient.date_of_birth,
        "gender": patient.gender,
        "created_at": patient.created_at,
        "vitals": patient.vitals,
        "labs": patient.labs,
        "scores": patient.scores
    }

#endpoint pentru a vizualiza toti pacientii
@app.get("/patients/")
def get_all_patients(db: Session = Depends(get_db)):
    patients = db.query(Patient).all()
    
    if not patients:
        raise HTTPException(status_code=404, detail="Nu exista pacienti in baza de date")
    
    return [{"patient_id": patient.patient_id, "pseudonym": patient.pseudonym} for patient in patients]

#endpoint pentru a adauga semne vitale unui pacient
@app.post("/vital_signs/{patient_id}")
def add_vital_signs(patient_id: str, heart_rate: int, spo2: float, temperature: float, timestamp: datetime, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    
    if not patient:
        raise HTTPException(status_code=404, detail="Pacientul nu a fost gasit")
    
    if heart_rate is None or spo2 is None or temperature is None or timestamp is None:
        raise HTTPException(status_code=400, detail="Toate campurile sunt necesare")
    elif db.query(VitalSigns).filter(VitalSigns.patient_id == patient_id, VitalSigns.timestamp == timestamp).first() is not None:
        raise HTTPException(status_code=400, detail="Semnele vitale exista deja pentru acest pacient la acest timestamp")

    new_vital_sign = VitalSigns(
        patient_id=patient_id,
        heart_rate=heart_rate,
        spo2=spo2,
        temperature=temperature,
        timestamp=timestamp
    )
    
    db.add(new_vital_sign)
    db.commit()
    db.refresh(new_vital_sign)
    
    return {"message": "Semne vitale adaugate cu succes", "vital_signs": new_vital_sign}

#endpoint pentru a vizualiza semnele vitale ale unui pacient
@app.get("/vital_signs/{patient_id}")
def get_vital_signs(patient_id: str, db: Session = Depends(get_db)):
    vital_signs = db.query(VitalSigns).filter(VitalSigns.patient_id == patient_id).all()
    
    if not vital_signs:
        raise HTTPException(status_code=404, detail="Semnele vitale nu au fost gasite")
    
    return [{"heart_rate": vs.heart_rate, "spo2": vs.spo2, "temperature": vs.temperature, "timestamp": vs.timestamp} for vs in vital_signs]

#endpoint pentru a adauga rezultate de laborator pentru un pacient
@app.post("/lab_results/{patient_id}")
def add_lab_data(patient_id: str, test_name: str, value: float, units: str, reference_range: str, timestamp: datetime, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    
    if not patient:
        raise HTTPException(status_code=404, detail="Pacientul nu a fost gasit")
    if test_name is None or value is None or units is None or reference_range is None or timestamp is None:
        raise HTTPException(status_code=400, detail="Toate campurile sunt necesare")
    elif db.query(LabResult).filter(LabResult.patient_id == patient_id, LabResult.test_name == test_name, LabResult.timestamp == timestamp).first() is not None:
        raise HTTPException(status_code=400, detail="Rezultatele de laborator exista deja pentru acest pacient la acest timestamp")
    
    new_lab_result = LabResult(
        patient_id=patient_id,
        test_name=test_name,
        value=value,
        units=units,
        reference_range=reference_range,
        timestamp=timestamp
    )
    
    db.add(new_lab_result)
    db.commit()
    db.refresh(new_lab_result)
    
    return {"message": "Rezultate de laborator adaugate cu succes", "lab_result": new_lab_result}

#endpoint pentru a vizualiza rezultatele de laborator ale unui pacient
@app.get("/lab_results/{patient_id}")
def get_lab_results(patient_id: str, db: Session = Depends(get_db)):
    lab_results = db.query(LabResult).filter(LabResult.patient_id == patient_id).all()
    
    if not lab_results:
        raise HTTPException(status_code=404, detail="Rezultatele de laborator nu au fost gasite")
    
    return [{"test_name": lr.test_name, "value": lr.value, "units": lr.units, "reference_range": lr.reference_range, "timestamp": lr.timestamp} for lr in lab_results]

#endpoint pentru a adauga scoruri clinice pentru un pacient
@app.post("/clinical_scores/{patient_id}")
def add_clinical_scores(patient_id: str, score_type: str, score_value: int, timestamp: datetime, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    
    if not patient:
        raise HTTPException(status_code=404, detail="Pacientul nu a fost gasit")
    if score_type is None or score_value is None or timestamp is None:
        raise HTTPException(status_code=400, detail="Toate campurile sunt necesare")
    elif db.query(ClinicalScore).filter(ClinicalScore.patient_id == patient_id, ClinicalScore.score_type == score_type, ClinicalScore.timestamp == timestamp).first() is not None:
        raise HTTPException(status_code=400, detail="Scorurile clinice exista deja pentru acest pacient la acest timestamp")
    
    new_clinical_score = ClinicalScore(
        patient_id=patient_id,
        score_type=score_type,
        score_value=score_value,
        timestamp=timestamp
    )
    
    db.add(new_clinical_score)
    db.commit()
    db.refresh(new_clinical_score)
    
    return {"message": "Scoruri clinice adaugate cu succes", "clinical_score": new_clinical_score}

#endpoint pentru a vizualiza scorurile clinice ale unui pacient    
@app.get("/clinical_scores/{patient_id}")
def get_clinical_scores(patient_id: str, db: Session = Depends(get_db)):
    clinical_scores = db.query(ClinicalScore).filter(ClinicalScore.patient_id == patient_id).all()
    
    if not clinical_scores:
        raise HTTPException(status_code=404, detail="Scorurile clinice nu au fost gasite")
    
    return [{"score_type": cs.score_type, "score_value": cs.score_value, "timestamp": cs.timestamp} for cs in clinical_scores]

#endpoint pentru exportarea datelor pacientului in format CSV
@app.get("/export_csv/{patient_id}")
def export_csv(patient_id: str, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    
    if not patient:
        raise HTTPException(status_code=404, detail="Pacientul nu a fost gasit")
    
    data = {
        "patient_id": patient.patient_id,
        "pseudonym": patient.pseudonym,
        "date_of_birth": patient.date_of_birth,
        "gender": patient.gender,
        "created_at": patient.created_at,
        "vitals": [{"heart_rate": vs.heart_rate, "spo2": vs.spo2, "temperature": vs.temperature, "timestamp": vs.timestamp} for vs in patient.vitals],
        "labs": [{"test_name": lr.test_name, "value": lr.value, "units": lr.units, "reference_range": lr.reference_range, "timestamp": lr.timestamp} for lr in patient.labs],
        "scores": [{"score_type": cs.score_type, "score_value": cs.score_value, "timestamp": cs.timestamp} for cs in patient.scores]
    }
    return pd.DataFrame(data).to_csv(index=False)

#endpoint pentru exportarea datelor pacientului in format JSON
@app.get("/export_json/{patient_id}")
def export_json(patient_id: str, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    
    if not patient:
        raise HTTPException(status_code=404, detail="Pacientul nu a fost gasit")
    
    data = {
        "patient_id": patient.patient_id,
        "pseudonym": patient.pseudonym,
        "date_of_birth": patient.date_of_birth,
        "gender": patient.gender,
        "created_at": patient.created_at,
        "vitals": [{"heart_rate": vs.heart_rate, "spo2": vs.spo2, "temperature": vs.temperature, "timestamp": vs.timestamp} for vs in patient.vitals],
        "labs": [{"test_name": lr.test_name, "value": lr.value, "units": lr.units, "reference_range": lr.reference_range, "timestamp": lr.timestamp} for lr in patient.labs],
        "scores": [{"score_type": cs.score_type, "score_value": cs.score_value, "timestamp": cs.timestamp} for cs in patient.scores]
    }
    return data

#endpoint pentru a verifica daca API-ul este activ
@app.post("/")
def root():
    return {"message": "API-ul este activ."}
# endpoint pentru modificarea datelor unui pacient
@app.put("/patients/{patient_id}")
def update_patient(patient_id: str, pseudonym: str = None, date_of_birth: str = None, gender: str = None, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()

    if not patient:
        raise HTTPException(status_code=404, detail="Pacientul nu a fost gasit")

    if pseudonym:
        patient.pseudonym = pseudonym
    if date_of_birth:
        patient.date_of_birth = date_of_birth
    if gender:
        patient.gender = gender

    db.commit()
    db.refresh(patient)
    return {"message": "Pacient actualizat cu succes", "patient": patient}

# endpoint pentru stergerea unui pacient
@app.delete("/patients/{patient_id}")
def delete_patient(patient_id: str, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Pacientul nu a fost gasit")

    db.delete(patient)
    db.commit()
    return {"message": "Pacient sters cu succes"}


# endpoint pentru stergerea rezultatelor de laborator
@app.delete("/lab_results/{patient_id}/{timestamp}")
def delete_lab_result(patient_id: str, timestamp: datetime, db: Session = Depends(get_db)):
    result = db.query(LabResult).filter(LabResult.patient_id == patient_id, LabResult.timestamp == timestamp).first()
    if not result:
        raise HTTPException(status_code=404, detail="Rezultatul de laborator nu a fost gasit")

    db.delete(result)
    db.commit()
    return {"message": "Rezultat de laborator sters cu succes"}


# endpoint pentru stergerea scorurilor clinice
@app.delete("/clinical_scores/{patient_id}/{timestamp}")
def delete_clinical_score(patient_id: str, timestamp: datetime, db: Session = Depends(get_db)):
    score = db.query(ClinicalScore).filter(ClinicalScore.patient_id == patient_id, ClinicalScore.timestamp == timestamp).first()
    if not score:
        raise HTTPException(status_code=404, detail="Scorul clinic nu a fost gasit")

    db.delete(score)
    db.commit()
    return {"message": "Scor clinic sters cu succes"}


# endpoint pentru stergerea semnelor vitale
@app.delete("/vital_signs/{patient_id}/{timestamp}")
def delete_vital_sign(patient_id: str, timestamp: datetime, db: Session = Depends(get_db)):
    vs = db.query(VitalSigns).filter(VitalSigns.patient_id == patient_id, VitalSigns.timestamp == timestamp).first()
    if not vs:
        raise HTTPException(status_code=404, detail="Semnul vital nu a fost gasit")

    db.delete(vs)
    db.commit()
    return {"message": "Semn vital sters cu succes"}


# endpoint pentru modificarea unui rezultat de laborator
@app.put("/lab_results/{patient_id}/{timestamp}")
def update_lab_result(patient_id: str, timestamp: datetime, value: float = None, units: str = None, reference_range: str = None, db: Session = Depends(get_db)):
    result = db.query(LabResult).filter(LabResult.patient_id == patient_id, LabResult.timestamp == timestamp).first()
    if not result:
        raise HTTPException(status_code=404, detail="Rezultatul nu a fost gasit")

    if value is not None:
        result.value = value
    if units is not None:
        result.units = units
    if reference_range is not None:
        result.reference_range = reference_range

    db.commit()
    db.refresh(result)
    return {"message": "Rezultatul laboratorului a fost actualizat", "lab_result": result}


# endpoint pentru modificarea unui scor clinic
@app.put("/clinical_scores/{patient_id}/{timestamp}")
def update_clinical_score(patient_id: str, timestamp: datetime, score_value: int = None, db: Session = Depends(get_db)):
    score = db.query(ClinicalScore).filter(ClinicalScore.patient_id == patient_id, ClinicalScore.timestamp == timestamp).first()
    if not score:
        raise HTTPException(status_code=404, detail="Scorul nu a fost gasit")

    if score_value is not None:
        score.score_value = score_value

    db.commit()
    db.refresh(score)
    return {"message": "Scorul clinic a fost actualizat", "clinical_score": score}


# endpoint pentru modificarea semnelor vitale
@app.put("/vital_signs/{patient_id}/{timestamp}")
def update_vital_sign(patient_id: str, timestamp: datetime, heart_rate: int = None, spo2: float = None, temperature: float = None, db: Session = Depends(get_db)):
    vs = db.query(VitalSigns).filter(VitalSigns.patient_id == patient_id, VitalSigns.timestamp == timestamp).first()
    if not vs:
        raise HTTPException(status_code=404, detail="Semnul vital nu a fost gasit")

    if heart_rate is not None:
        vs.heart_rate = heart_rate
    if spo2 is not None:
        vs.spo2 = spo2
    if temperature is not None:
        vs.temperature = temperature

    db.commit()
    db.refresh(vs)
    return {"message": "Semnul vital a fost actualizat", "vital_sign": vs}

