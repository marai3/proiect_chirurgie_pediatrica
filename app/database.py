<<<<<<< HEAD
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime

# -> Ai nevoie de PostgreSQL activ și de o bază numită 'clinica'
DATABASE_URL = "postgresql://postgres:password@localhost/clinica"  # ← adaptează parola și baza ta

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Patient(Base):
    __tablename__ = "patients"
    patient_id = Column(String, primary_key=True, index=True)  # ex: P001
    pseudonym = Column(String, nullable=False)
    date_of_birth = Column(DateTime)
    gender = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    vitals = relationship("VitalSigns", back_populates="patient")
    labs = relationship("LabResult", back_populates="patient")
    scores = relationship("ClinicalScore", back_populates="patient")

class VitalSigns(Base):
    __tablename__ = "vital_signs"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patients.patient_id"))
    heart_rate = Column(Integer)
    spo2 = Column(Float)
    temperature = Column(Float)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    source = Column(String)  # ex: "manual", "api"

    patient = relationship("Patient", back_populates="vitals")

class LabResult(Base):
    __tablename__ = "lab_results"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patients.patient_id"))
    test_name = Column(String)            # ex: CRP, leucocite
    value = Column(Float)
    units = Column(String)
    reference_range = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    patient = relationship("Patient", back_populates="labs")

class ClinicalScore(Base):
    __tablename__ = "clinical_scores"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patients.patient_id"))
    score_type = Column(String)           # ex: PEWS, NEWS
    score_value = Column(Integer)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    patient = relationship("Patient", back_populates="scores")

class AccessLog(Base):
    __tablename__ = "access_logs"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String)
    username = Column(String)
    role = Column(String)
    event_type = Column(String)            # ex: ACCESS_VIEW, DATA_SUBMIT
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    username = Column(String, primary_key=True)
    hashed_password = Column(Text, nullable=False)
    role = Column(String, nullable=False)  # doctor, nurse, researcher

def init_db():
    Base.metadata.create_all(bind=engine)
=======
import pandas as pd

# Inițializăm DataFrame-ul cu structura de date dorită
df = pd.DataFrame(columns=["patient_id", "heart_rate", "spo2", "temperature", "timestamp"])

# Funcție de salvare a unei înregistrări noi
def save_vital_data(entry: dict):
    global df
    df.loc[len(df)] = entry

# Funcție pentru extragerea ultimelor înregistrări
def get_latest_entries(n=10):
    return df.tail(n).to_dict(orient="records")

# Funcție pentru export CSV
def export_csv(path="data/export.csv"):
    df.to_csv(path, index=False)

# Funcție pentru export JSON
def export_json(path="data/export.json"):
    df.to_json(path, orient="records", lines=True)
>>>>>>> 4de70005ada7e99a8eb21320c7e745b4696340fe
