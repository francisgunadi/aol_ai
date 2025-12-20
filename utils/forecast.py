import os
import json
import argparse
import joblib
import numpy as np
import pandas as pd
from datetime import timedelta


def forecast_next_days(
    x_days: int = 14,
    model_dir: str = 'utils/model/',
    rolling_window_size: int = 7
):
    """
    Forecast the next x_days for each dish using saved daily RandomForest models.

    Args:
        x_days (int): Number of future days to forecast
        model_dir (str): Directory containing saved .pkl models

    Returns:
        dict[dish_name -> DataFrame of daily forecasts]
    """

    processed_data = readData()

    if not isinstance(processed_data, dict):
        raise TypeError("processed_data must be a dictionary")
    
    forecasts = {}
    min_history = rolling_window_size + 1  # Need window + at least 1 more
    
    for dish_name, df in processed_data.items():
        # Validate DataFrame structure
        required_cols = {"date", "quantity", "time_idx"}
        if not required_cols.issubset(set(df.columns)):
            print(f"Skipping {dish_name}: missing required columns")
            continue

        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        model_path = os.path.join(base_dir, 'utils', 'model', f"{dish_name}.pkl")
        
        if not os.path.exists(model_path):
            print(f"Skipping {dish_name}: model not found at {model_path}")
            continue

        if len(df) < min_history:
            print(f"Skipping {dish_name}: insufficient history (need {min_history}, have {len(df)})")
            continue

        try:
            model = joblib.load(model_path)
        except Exception as e:
            print(f"Skipping {dish_name}: failed to load model - {e}")
            continue

        df = df.sort_values("date").reset_index(drop=True)
        last_row = df.iloc[-1]
        last_date = pd.to_datetime(last_row["date"])
        
        # Initialize rolling window with actual historical data
        quantity_window = list(df["quantity"].tail(rolling_window_size))
        current_time_idx = int(last_row["time_idx"])
        
        future_rows = []
        
        for step in range(1, x_days + 1):
            # FIXED: Increment by step days, not always 1
            next_date = last_date + timedelta(days=step)
            past_weekly_avg = float(np.mean(quantity_window))
            
            future_row = {
                "dish_name": dish_name,
                "year": next_date.year,
                "weekOfYear": next_date.isocalendar().week,
                "time_idx": current_time_idx + step,  # FIXED: increment by step
                "pastWeeklySalesAvg": past_weekly_avg,
            }
            
            try:
                X_future = pd.DataFrame([future_row])
                predicted_quantity = float(model.predict(X_future)[0])
                
                # Update rolling window (FIFO)
                quantity_window.append(predicted_quantity)
                quantity_window.pop(0)
                
                future_row.update({
                    "date": next_date,
                    "predicted_quantity": predicted_quantity,
                })
                future_rows.append(future_row)
            except Exception as e:
                print(f"Error predicting for {dish_name} on day {step}: {e}")
                break  # Stop forecasting this dish if prediction fails
        
        if future_rows:
            forecasts[dish_name] = pd.DataFrame(future_rows)
    
    ingredient_reccomendation = compute_stock_recommendations(predicted_data=forecasts)

    return forecasts, ingredient_reccomendation


def compute_stock_recommendations(
    predicted_data: dict,
    menu_path: str = 'upload/cleaned/menu.json',
    pantry_path: str = 'upload/cleaned/pantry.json',
    ingredient_path: str = 'upload/cleaned/ingredient.json',
):
    """
    For all predicted dishes, compute total ingredient requirements using
    per-portion amounts from ingredient.json, and compare to pantry stock.

    Returns:
        dict: Dictionary mapping ingredient_name -> aggregate recommendation:
            - ingredient_name
            - required_qty (total needed across ALL dishes)
            - current_stock (current pantry stock)
            - unit
            - to_buy (amount to purchase)
            - status ("NEED_TO_BUY" or "ENOUGH")
    """
    # Validate file paths
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    menu_path = os.path.join(base_dir, 'upload', 'cleaned', 'menu.json')
    pantry_path = os.path.join(base_dir, 'upload', 'cleaned', 'pantry.json')
    ingredient_path = os.path.join(base_dir, 'upload', 'cleaned', 'ingredient.json')

    if not os.path.exists(menu_path):
        raise FileNotFoundError(f"Menu file not found: {menu_path}")
    if not os.path.exists(pantry_path):
        raise FileNotFoundError(f"Pantry file not found: {pantry_path}")
    if not os.path.exists(ingredient_path):
        raise FileNotFoundError(f"Ingredient file not found: {ingredient_path}")

    # Load data files
    menu = pd.read_json(menu_path)
    pantry = pd.read_json(pantry_path)
    ingredients_per_portion = pd.read_json(ingredient_path)

    # Validate required columns
    if "ingredient_name" not in pantry.columns or "quantity" not in pantry.columns:
        raise ValueError("Pantry.json must have 'ingredient_name' and 'quantity' columns.")

    # Prepare pantry lookup with cleaned ingredient names
    pantry_clean = pantry.copy()
    pantry_clean["ingredient_name_clean"] = (
        pantry_clean["ingredient_name"].astype(str).str.strip().str.lower()
    )

    # Prepare per-portion quantity lookup (ingredient.json)
    ipp = ingredients_per_portion.copy()
    ipp["ingredient_name_clean"] = (
        ipp["ingredient_name"].astype(str).str.strip().str.lower()
    )

    # Dictionary to store results for each INGREDIENT (aggregated over all dishes)
    all_recommendations = {}

    # Loop through each predicted dish
    for dish_name, forecast_df in predicted_data.items():
        if forecast_df.empty or "predicted_quantity" not in forecast_df.columns:
            print(f"Skipping {dish_name}: no predicted quantities found")
            continue

        # Total predicted portions for this dish across all forecast days
        total_predicted_portions = float(forecast_df["predicted_quantity"].sum())

        # Find the menu row for this dish
        match = menu[menu["dish_name"] == dish_name]
        if match.empty:
            print(f"Warning: Dish '{dish_name}' not found in menu.json, skipping stock calculation")
            continue

        menu_row = match.iloc[0]
        ingredients = menu_row.get("ingredient", []) or []

        if not ingredients:
            print(f"Dish '{dish_name}' has no ingredients listed in menu.json.")
            continue

        # For each ingredient used by this dish, add its requirement into the aggregate
        for ing in ingredients:
            ing_name = str(ing).strip()
            if not ing_name:
                continue
            ing_clean = ing_name.lower()

            # Default per-portion quantity if not found in ingredient.json
            amount_per_portion = 1.0
            unit = "unit"

            # Look up per-portion quantity from ingredient.json
            row_ipp = ipp[ipp["ingredient_name_clean"] == ing_clean]
            if not row_ipp.empty:
                r = row_ipp.iloc[0]
                amount_per_portion = float(r["quantity"])
                unit = r.get("unit", unit)

            # Required for this dish for the forecast horizon
            required_for_dish = total_predicted_portions * amount_per_portion

            # Look up pantry stock (same for all dishes using this ingredient)
            row_p = pantry_clean[pantry_clean["ingredient_name_clean"] == ing_clean]
            if not row_p.empty:
                rp = row_p.iloc[0]
                current_stock = float(rp["quantity"])
                pantry_unit = rp.get("unit", unit)
                if isinstance(pantry_unit, str) and pantry_unit.strip():
                    unit = pantry_unit
            else:
                current_stock = 0.0

            # Initialize aggregate entry for this ingredient if needed
            if ing_name not in all_recommendations:
                all_recommendations[ing_name] = {
                    "ingredient_name": ing_name,
                    "required_qty": 0.0,
                    "current_stock": current_stock,
                    "unit": unit,
                    "to_buy": 0.0,
                    "status": "ENOUGH",
                }

            entry = all_recommendations[ing_name]
            # Add this dish's requirement to the total required quantity
            entry["required_qty"] += required_for_dish

            # Recompute deficit and status based on aggregated requirement
            deficit = entry["required_qty"] - entry["current_stock"]
            entry["to_buy"] = max(deficit, 0.0)
            entry["status"] = "NEED_TO_BUY" if deficit > 0 else "ENOUGH"

    return all_recommendations

def readData(json_path: str = 'upload/processed/processed_data.json'):
    """
    Read processed_data.json file and convert it to the dictionary format
    expected by forecast_next_days().
    
    Args:
        json_path (str): Path to the processed_data.json file
        
    Returns:
        dict[dish_name -> DataFrame]: Dictionary mapping dish names to their
            historical data DataFrames with columns: date, quantity, time_idx,
            year, weekOfYear, pastWeeklySalesAvg, dish_name
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    json_path = os.path.join(base_dir, 'upload', 'processed', 'processed_data.json')
    
    # Check if file exists
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Processed data file not found: {json_path}")
    
    # Load JSON file - it's structured as {dish_name: [list of records]}
    with open(json_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    # Convert to dictionary of DataFrames
    processed_data = {}
    
    for dish_name, records in json_data.items():
        if not records:  # Skip empty lists
            continue
            
        # Convert list of records to DataFrame
        df = pd.DataFrame(records)
        
        # Convert date string to datetime
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Ensure data is sorted by date
        df = df.sort_values('date').reset_index(drop=True)
        
        # Store in dictionary
        processed_data[dish_name] = df
    
    return processed_data


def _ingredients_dict_to_list(ingredients_dict: dict) -> list:
    """
    Convert the ingredient recommendations dict to a list of plain-Python dicts
    safe for JSON serialization.
    """
    result = []
    for ing_name, rec in ingredients_dict.items():
        result.append(
            {
                "ingredient_name": str(rec.get("ingredient_name", ing_name)),
                "required_qty": float(rec.get("required_qty", 0.0)),
                "current_stock": float(rec.get("current_stock", 0.0)),
                "unit": str(rec.get("unit", "")),
                "to_buy": float(rec.get("to_buy", 0.0)),
                "status": str(rec.get("status", "")),
            }
        )
    return result


def _forecasts_dict_to_list(forecasts_dict: dict) -> list:
    """
    Convert the forecasts dict (dish_name -> DataFrame) to a list of plain-Python dicts
    safe for JSON serialization.
    
    Returns:
        list: [
            {
                "dish_name": str,
                "points": [
                    {"date": "YYYY-MM-DD", "predicted_quantity": float},
                    ...
                ]
            },
            ...
        ]
    """
    result = []
    for dish_name, df in forecasts_dict.items():
        points = []
        for _, row in df.iterrows():
            # Convert date to ISO string format
            date_str = str(row.get("date", ""))
            if pd.notna(row.get("date")):
                if isinstance(row["date"], pd.Timestamp):
                    date_str = row["date"].strftime('%Y-%m-%d')
                else:
                    date_str = str(row["date"])
            
            points.append({
                "date": date_str,
                "predicted_quantity": float(row.get("predicted_quantity", 0.0)),
            })
        
        result.append({
            "dish_name": str(dish_name),
            "points": points,
        })
    
    return result


def main():
    """
    CLI entry point.

    Usage:
        python utils/forecast.py --days 14

    Prints a JSON object with aggregated ingredient recommendations:
        {
            "success": true,
            "ingredients": [
                {
                    "ingredient_name": "...",
                    "required_qty": ...,
                    "current_stock": ...,
                    "unit": "...",
                    "to_buy": ...,
                    "status": "NEED_TO_BUY" | "ENOUGH"
                },
                ...
            ]
        }
    """
    parser = argparse.ArgumentParser(description="Run sales forecast and ingredient stock check.")
    parser.add_argument(
        "--days",
        type=int,
        default=14,
        help="Number of DAYS to forecast into the future (default: 14).",
    )

    args = parser.parse_args()

    try:
        forecasts_dict, ingredient_recommendation = forecast_next_days(x_days=args.days)

        ingredients_list = _ingredients_dict_to_list(ingredient_recommendation)
        sales_list = _forecasts_dict_to_list(forecasts_dict)

        payload = {
            "success": True,
            "ingredients": ingredients_list,
            "sales_data": sales_list,
        }

        print(json.dumps(payload, ensure_ascii=False))
    except Exception as exc:
        error_payload = {
            "success": False,
            "error": str(exc),
        }
        # Print error as JSON so the caller can parse it if needed
        print(json.dumps(error_payload, ensure_ascii=False))
        raise


if __name__ == "__main__":
    main()