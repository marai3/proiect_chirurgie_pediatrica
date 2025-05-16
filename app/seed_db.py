from database import SessionLocal, User
from passlib.context import CryptContext
import random
from datetime import datetime, timedelta
from database import Patient, VitalSigns

def add_test_users():
    # Setup bcrypt
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    # Utilizatori de test
    users = [
        {"username": "medic", "password": "medic123", "role": "doctor"},
        {"username": "asistent", "password": "asistent123", "role": "nurse"},
        {"username": "cercetator", "password": "research123", "role": "researcher"},
        {"username": "admin", "password": "admin", "role": "admin"},
    ]

    # Conectare la DB
    db = SessionLocal()

    for user in users:
        # Verifică dacă există deja
        existing = db.query(User).filter(User.username == user["username"]).first()
        if not existing:
            hashed_pw = pwd_context.hash(user["password"])
            new_user = User(
                username=user["username"],
                hashed_password=hashed_pw,
                role=user["role"]
            )
            db.add(new_user)
            print(f"Utilizator '{user['username']}' adăugat.")
        else:
            print(f"Utilizatorul '{user['username']}' există deja.")

    db.commit()
    db.close()

def seed_vital_signs_for_all():
    db = SessionLocal()

    # Obține toți pacienții existenți
    pacienti = db.query(Patient).all()
    if not pacienti:
        print("Nu există pacienți în baza de date.")
        return

    for pacient in pacienti:
        for i in range(5):
            vit = VitalSigns(
                patient_id=pacient.patient_id,
                heart_rate=random.randint(60, 200),
                spo2=round(random.uniform(80, 100), 1),
                temperature=round(random.uniform(35.8, 40.5), 1),
                source=random.choice(["manual", "api"]),
                timestamp=datetime.utcnow() - timedelta(hours=i * 3),
            )
            db.add(vit)
        print(f"Adăugat 5 seturi vitale pentru pacientul {pacient.patient_id} ({pacient.pseudonym})")

    db.commit()
    db.close()
    print("Gata! Datele vitale au fost generate cu succes pentru toți pacienții.")

if __name__ == "__main__":
    seed_vital_signs_for_all()
