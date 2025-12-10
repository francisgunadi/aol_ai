import pandas as pd
import os
import json

def load_data(path: str, name: str):
    data = pd.read_csv(path, sep=";")

    # Basic cleanups
    # Ensure column names are standard / trimmed
    data.columns = [c.strip().lower() for c in data.columns]

    # Parse date
    if "date" in data.columns:
        data["date"] = pd.to_datetime(data["date"], dayfirst=True)

    # Make sure quantity is numeric
    if "quantity" in data.columns:
        data["quantity"] = pd.to_numeric(data["quantity"], errors="coerce").fillna(0).astype(int)
    
    outputDir = "upload/cleaned"
    os.makedirs(outputDir, exist_ok=True)

    data = data.to_dict(orient="records")

    data = os.path.join(outputDir, f"{name}.json")
    with open(data, "w") as f:
        json.dump(data, f, indent=4)