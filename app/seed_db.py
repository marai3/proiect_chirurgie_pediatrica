from database import SessionLocal, User
from passlib.context import CryptContext

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
