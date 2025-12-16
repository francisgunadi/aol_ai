import pandas as pd
import os
import json
import sys

def load_data(path: str, name: str):
    # Try semicolon separator first, then comma
    data = pd.read_csv(path, sep=";")

    # Basic cleanups
    # Ensure column names are standard / trimmed
    data.columns = [c.strip().lower() for c in data.columns]

    salesFile = "quantity" in data.columns and "date" in data.columns and "dish_name" in data.columns
    pantryFile = "ingredient_name" in data.columns and "quantity" in data.columns and "unit" in data.columns

    # Parse date
    if "date" in data.columns:
        data["date"] = pd.to_datetime(data["date"], dayfirst=True, errors="coerce")
        data["date"] = data["date"].dt.date
        mask = data["date"].notna()
        data.loc[~mask, "date"] = ""
    
    if "quantity" in data.columns:
        data["quantity"] = pd.to_numeric(data["quantity"], errors="coerce").fillna(0).astype(int)

    if "price" in data.columns:
        data["price"] = pd.to_numeric(data["price"], errors="coerce").fillna(0).astype(float)
    
    if "ingredient" in data.columns:
        data["ingredient"] = data['ingredient'].str.split(',').apply(lambda list: [s.strip() for s in list])
    
    if salesFile:
        data = data.groupby(["dish_name", "date"], as_index=False)["quantity"].sum()
        data = data.sort_values(by="date")
    
    # Get absolute path for output directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    outputDir = os.path.join(project_root, "upload", "cleaned")
    os.makedirs(outputDir, exist_ok=True)

    data_dict = data.to_dict(orient="records")

    output_path = os.path.join(outputDir, f"{name}.json")

    if os.path.exists(output_path) and salesFile:
        with open(output_path, "r") as f:
            existing_data = json.load(f)
        
        if isinstance(existing_data, list):
            existing_data.extend(data_dict)
            combined_data = existing_data
        else:
            combined_data = [existing_data] + data_dict
    else:
        combined_data = data_dict

    with open(output_path, "w") as f:
        json.dump(combined_data, f, indent=4, default=str)
    
    return output_path

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python readFile.py <csv_path> <output_name>")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    output_name = sys.argv[2]
    
    try:
        result_path = load_data(csv_path, output_name)
        print(f"Successfully processed file. Output: {result_path}")
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)