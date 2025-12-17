import pandas as pd
import os
import json
import sys

import modelAlgorithm.randomForestRegressor as rfg

def save_processed_data(processed_data: dict, output_path: str):

    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Convert dictionary of DataFrames to nested dictionary structure
        json_data = {}
        for dish_name, df in processed_data.items():
            # Convert DataFrame to list of records
            # Handle date serialization by converting to ISO format strings
            df_copy = df.copy()
            if 'date' in df_copy.columns:
                df_copy['date'] = pd.to_datetime(df_copy['date'], errors='coerce')
                df_copy['date'] = df_copy['date'].dt.strftime('%Y-%m-%d').fillna('')
            
            # Convert to list of dictionaries
            json_data[dish_name] = df_copy.to_dict(orient="records")
        
        # Save to JSON file
        with open(output_path, "w") as f:
            json.dump(json_data, f, indent=4, default=str)
        
        print(f"Processed data saved to {output_path}")
    except Exception as e:
        print(f"Warning: Failed to save processed data: {str(e)}", file=sys.stderr)

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
        # Keep as datetime - don't convert to .date objects
    
    if "quantity" in data.columns:
        data["quantity"] = pd.to_numeric(data["quantity"], errors="coerce").fillna(0).astype(int)

    if "price" in data.columns:
        data["price"] = pd.to_numeric(data["price"], errors="coerce").fillna(0).astype(float)
    
    if "ingredient" in data.columns:
        data["ingredient"] = data['ingredient'].str.split(',').apply(lambda list: [s.strip() for s in list])
    
    if salesFile:
        # Prepare data for training
        data = data.groupby(["dish_name", "date"], as_index=False)["quantity"].sum()
        data = data.sort_values(by="date")
        
        # Train model and get processed dataframes
        processed_data = rfg.train_random_forest(data = data)
        
        # Get absolute path for processed output directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(script_dir))
        processed_dir = os.path.join(project_root, "upload", "processed")
        processed_path = os.path.join(processed_dir, "processed_data.json")
        
        # Save processed data to upload/processed/processed_data.json
        save_processed_data(processed_data, processed_path)

    
    # Get absolute path for output directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    outputDir = os.path.join(project_root, "upload", "cleaned")
    os.makedirs(outputDir, exist_ok=True)

    if "date" in data.columns:
        data = data.copy()
        mask = data["date"].notna()
        data.loc[mask, "date"] = pd.to_datetime(data.loc[mask, "date"]).dt.strftime('%Y-%m-%d')
        data.loc[~mask, "date"] = ""
    
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