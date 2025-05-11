from fastapi import FastAPI, Form, HTTPException, Depends
from pydantic import BaseModel
from passlib.context import CryptContext
import pandas as pd
from auth import create_access_token, fake_users_db, role_required

app = FastAPI()

pwd_context = CryptContext(schemes=["bcrypt"])

# Simulated local storage
df = pd.DataFrame()

class VitalData(BaseModel):
    patient_id: str
    heart_rate: int
    spo2: float
    temperature: float
    timestamp: str
@app.post("/token")
def login(username: str = Form(...), password: str = Form(...)):
    user = fake_users_db.get(username)
    if not user or not pwd_context.verify(password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token(data={"sub": username, "role": user["role"]})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/vitals-secured")
def view_vitals(user=Depends(role_required(["doctor", "nurse"]))):
    return df.tail(5).to_dict()

@app.get("/export/json")
def export_json():
    df.to_json("data/export_r.json", orient="records", lines=True)
    return {"message": "Export JSON pentru R salvat."}

@app.post("/submit")
def submit_vitals(data: VitalData):
    global df
    entry = data.dict()
    df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
    return {"message": "Date înregistrate."}