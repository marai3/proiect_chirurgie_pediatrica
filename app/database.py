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
