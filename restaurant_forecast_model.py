# restaurant_forecast_model.py

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline

# ============================================================
# 1. Load data
# ============================================================

def load_data(
    menu_path="Menu.csv",
    pantry_path="Pantry.csv",
    sales_path="Sales.csv"
):
    # Menu: semicolon separated
    menu = pd.read_csv(menu_path, sep=";")
    # Pantry: comma separated
    pantry = pd.read_csv(pantry_path)
    # Sales: semicolon separated
    sales = pd.read_csv(sales_path, sep=";")

    # Basic cleanups
    # Ensure column names are standard / trimmed
    menu.columns = [c.strip() for c in menu.columns]
    pantry.columns = [c.strip() for c in pantry.columns]
    sales.columns = [c.strip() for c in sales.columns]

    # Parse date
    sales["date"] = pd.to_datetime(sales["date"], dayfirst=True)

    # Make sure quantity is numeric
    sales["quantity"] = pd.to_numeric(sales["quantity"], errors="coerce").fillna(0).astype(int)

    return menu, pantry, sales


# ============================================================
# 2. Create weekly aggregated dataset
# ============================================================

def build_weekly_sales_dataset(sales: pd.DataFrame) -> pd.DataFrame:
    """
    Input: sales with columns [date, dish_name, quantity]
    Output: weekly aggregated dataframe with features for training
    """
    # Ensure correct columns
    required_cols = {"date", "dish_name", "quantity"}
    if not required_cols.issubset(set(sales.columns)):
        missing = required_cols - set(sales.columns)
        raise ValueError(f"Sales is missing required columns: {missing}")

    # Set index to date for resampling
    sales_idx = sales.set_index("date")

    # Weekly sum per dish_name
    weekly = (
        sales_idx
        .groupby("dish_name")
        .resample("W")["quantity"]
        .sum()
        .reset_index()
    )

    # Add time features
    weekly["year"] = weekly["date"].dt.year
    weekly["weekofyear"] = weekly["date"].dt.isocalendar().week.astype(int)

    # Time index per dish (0,1,2,... per dish)
    weekly["time_idx"] = weekly.groupby("dish_name").cumcount()

    return weekly


# ============================================================
# 3. Train RandomForestRegressor
# ============================================================

def train_random_forest(weekly: pd.DataFrame):
    """
    Train a RandomForestRegressor to predict weekly quantity for dish_name.
    Returns: (trained_model, weekly_with_features)
    """
    # Features and target
    feature_cols = ["dish_name", "year", "weekofyear", "time_idx"]
    target_col = "quantity"

    # Sort by date to keep temporal order
    weekly = weekly.sort_values("date").reset_index(drop=True)

    X = weekly[feature_cols]
    y = weekly[target_col]

    # Split train / test by time (80% / 20%)
    split_idx = int(len(weekly) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    # Categorical + numeric preprocessing
    categorical_cols = ["dish_name"]
    numeric_cols = ["year", "weekofyear", "time_idx"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols),
            ("num", "passthrough", numeric_cols),
        ]
    )

    rf = RandomForestRegressor(
        n_estimators=300,
        max_depth=None,
        min_samples_split=4,
        random_state=42,
        n_jobs=-1,
    )

    model = Pipeline(steps=[
        ("preprocess", preprocessor),
        ("rf", rf),
    ])

    model.fit(X_train, y_train)

    # Evaluate (optional)
    if len(X_test) > 0:
        y_pred = model.predict(X_test)
        mae = np.mean(np.abs(y_test - y_pred))
        rmse = np.sqrt(np.mean((y_test - y_pred) ** 2))
        print("Model evaluation:")
        print(f"  MAE  = {mae:.3f}")
        print(f"  RMSE = {rmse:.3f}")
    else:
        print("Warning: Not enough data for a test split; model trained on all data.")

    return model, weekly


# ============================================================
# 4. Forecast function for menu item X and Y weeks
# ============================================================

def forecast_menu_item_sales(
    dish_name: str,
    horizon_weeks: int,
    model,
    weekly_data: pd.DataFrame
):
    """
    Forecast future weekly sales for the given dish_name for next horizon_weeks.
    Returns: (forecast_df, total_predicted_quantity)
    """
    if dish_name not in weekly_data["dish_name"].unique():
        raise ValueError(f"Dish '{dish_name}' not found in historical weekly data.")

    # Filter historical data for this dish
    hist = weekly_data[weekly_data["dish_name"] == dish_name].sort_values("date")
    last_row = hist.iloc[-1]

    last_date = last_row["date"]
    last_time_idx = int(last_row["time_idx"])

    future_rows = []
    for i in range(1, horizon_weeks + 1):
        future_date = last_date + pd.Timedelta(weeks=i)
        year = future_date.year
        weekofyear = int(future_date.isocalendar().week)
        time_idx = last_time_idx + i

        future_rows.append({
            "dish_name": dish_name,
            "date": future_date,
            "year": year,
            "weekofyear": weekofyear,
            "time_idx": time_idx,
        })

    future_df = pd.DataFrame(future_rows)

    feature_cols = ["dish_name", "year", "weekofyear", "time_idx"]
    X_future = future_df[feature_cols]

    future_df["predicted_quantity"] = model.predict(X_future)

    # Total predicted portions over horizon
    total_predicted = future_df["predicted_quantity"].sum()

    return future_df, total_predicted


# ============================================================
# 5. Ingredient usage & stock check
# ============================================================

def parse_ingredients_from_menu(menu_row: pd.Series):
    """
    Parse ingredients from the 'ingredient' column in Menu.csv
    Assumes it's a comma-separated string.
    """
    ing_str = str(menu_row.get("ingredient", "")).strip()
    if not ing_str:
        return []
    return [x.strip() for x in ing_str.split(",") if x.strip()]


def compute_stock_recommendations(
    dish_name: str,
    total_predicted_portions: float,
    menu: pd.DataFrame,
    pantry: pd.DataFrame,
    ingredients_per_portion: pd.DataFrame,
):
    """
    For the predicted total portions of a dish, compute ingredient requirements
    using per-portion amounts from ingredients_per_portion (Ingridients.csv),
    and compare to current pantry stock.

    ingredients_per_portion is expected to have columns:
        - ingredient_name
        - quantity  (amount per portion, in the given unit)
        - unit
    """
    # Find the menu row for this dish
    match = menu[menu["dish_name"] == dish_name]
    if match.empty:
        raise ValueError(f"Dish '{dish_name}' not found in Menu.csv")

    menu_row = match.iloc[0]
    ingredients = parse_ingredients_from_menu(menu_row)

    if not ingredients:
        print(f"Dish '{dish_name}' has no ingredients listed in Menu.csv.")
        return []

    # Prepare pantry lookup
    if "ingredient_name" not in pantry.columns or "quantity" not in pantry.columns:
        raise ValueError("Pantry.csv must have 'ingredient_name' and 'quantity' columns.")

    pantry_clean = pantry.copy()
    pantry_clean["ingredient_name_clean"] = (
        pantry_clean["ingredient_name"].astype(str).str.strip().str.lower()
    )

    # Prepare per-portion quantity lookup (Ingridients.csv)
    ipp = ingredients_per_portion.copy()
    ipp["ingredient_name_clean"] = (
        ipp["ingredient_name"].astype(str).str.strip().str.lower()
    )

    results = []

    for ing in ingredients:
        ing_clean = ing.strip().lower()

        # Default per-portion quantity if not found in Ingridients.csv
        amount_per_portion = 1.0
        unit = "unit"

        row_ipp = ipp[ipp["ingredient_name_clean"] == ing_clean]
        if not row_ipp.empty:
            r = row_ipp.iloc[0]
            amount_per_portion = float(r["quantity"])
            unit = r.get("unit", unit)

        # Total required for the forecast horizon
        required_qty = float(total_predicted_portions) * amount_per_portion

        # Current stock from pantry
        row_p = pantry_clean[pantry_clean["ingredient_name_clean"] == ing_clean]
        if not row_p.empty:
            rp = row_p.iloc[0]
            current_stock = float(rp["quantity"])
            pantry_unit = rp.get("unit", unit)
            # If pantry unit is provided, prefer it
            if isinstance(pantry_unit, str) and pantry_unit.strip():
                unit = pantry_unit
        else:
            current_stock = 0.0

        deficit = required_qty - current_stock

        results.append({
            "ingredient_name": ing,
            "required_qty": required_qty,
            "current_stock": current_stock,
            "unit": unit,
            "to_buy": max(deficit, 0.0),
            "status": "NEED_TO_BUY" if deficit > 0 else "ENOUGH",
        })

    return results


# ============================================================
# 6. End-to-end helper
# ============================================================

def run_forecast_and_stock_check(
    dish_name: str,
    horizon_weeks: int,
    menu_path="Menu.csv",
    pantry_path="Pantry.csv",
    sales_path="Sales.csv",
    ingredients_path="Ingridients.csv",
):
    """
    End-to-end helper:
    - loads data
    - trains the model
    - forecasts future sales for the given dish
    - computes ingredient stock recommendations using Ingridients.csv
    """
    # Load core data
    menu, pantry, sales = load_data(menu_path, pantry_path, sales_path)

    # Load per-portion ingredient usage
    ingredients_per_portion = pd.read_csv(ingredients_path)

    # Build weekly dataset
    weekly = build_weekly_sales_dataset(sales)

    # Train model
    model, weekly_with_features = train_random_forest(weekly)

    # Forecast
    future_df, total_predicted = forecast_menu_item_sales(
        dish_name=dish_name,
        horizon_weeks=horizon_weeks,
        model=model,
        weekly_data=weekly_with_features,
    )

    print(f"\nForecast for '{dish_name}' over next {horizon_weeks} weeks:")
    print(future_df[["date", "predicted_quantity"]])

    print(f"\nTotal predicted portions over {horizon_weeks} weeks: {total_predicted:.2f}")

    # Stock recommendations using real per-portion quantities
    recommendations = compute_stock_recommendations(
        dish_name=dish_name,
        total_predicted_portions=total_predicted,
        menu=menu,
        pantry=pantry,
        ingredients_per_portion=ingredients_per_portion,
    )

    print("\nIngredient stock check:")
    for rec in recommendations:
        print(
            f" - {rec['ingredient_name']}: "
            f"required={rec['required_qty']:.2f}{rec['unit']}, "
            f"stock={rec['current_stock']:.2f}{rec['unit']} "
            f"-> status={rec['status']}"
            + (
                f", BUY {rec['to_buy']:.2f}{rec['unit']}"
                if rec["status"] == "NEED_TO_BUY"
                else ""
            )
        )

    return {
        "future_forecast": future_df,
        "total_predicted_portions": total_predicted,
        "stock_recommendations": recommendations,
    }


def aggregate_total_ingredient_needs(all_results, pantry):
    """
    Combine ingredient needs from all dishes to compute a global purchase list.
    """
    # ingredient -> total required
    aggregate = {}

    for result in all_results:
        dish_recs = result["stock_recommendations"]

        for rec in dish_recs:
            ing = rec["ingredient_name"]
            req = rec["required_qty"]

            if ing not in aggregate:
                aggregate[ing] = 0.0
            aggregate[ing] += req

    # Pantry lookup
    pantry_clean = pantry.copy()
    pantry_clean["ingredient_name_clean"] = pantry_clean["ingredient_name"].str.strip().str.lower()

    final_list = []

    for ing, total_required in aggregate.items():
        row = pantry_clean[pantry_clean["ingredient_name_clean"] == ing.lower()]

        if not row.empty:
            current_stock = float(row.iloc[0]["quantity"])
            unit = row.iloc[0].get("unit", "unit")
        else:
            current_stock = 0.0
            unit = "unit"

        deficit = total_required - current_stock

        final_list.append({
            "ingredient": ing,
            "total_required": total_required,
            "current_stock": current_stock,
            "to_buy": max(deficit, 0),
            "unit": unit,
            "status": "NEED_TO_BUY" if deficit > 0 else "ENOUGH"
        })

    return final_list


# ============================================================
# 7. CLI example
# ============================================================
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Restaurant Forecast System")
    parser.add_argument(
        "--dish",
        type=str,
        default="ALL",
        help="Dish name (exact as in Menu.csv) or 'ALL'",
    )
    parser.add_argument(
        "--weeks",
        type=int,
        default=4,
        help="Number of weeks to forecast",
    )

    args = parser.parse_args()

    menu_path = "Menu.csv"
    pantry_path = "Pantry.csv"
    sales_path = "Sales.csv"

    # Load once here to get list of dishes
    menu, pantry, sales = load_data(menu_path, pantry_path, sales_path)

    # ======================================================
    #   CASE 1: FORECAST ALL DISHES
    # ======================================================
    if args.dish.upper() == "ALL":

        all_dishes = menu["dish_name"].unique()
        all_results = []  # store all dishes' results

        for dish in all_dishes:
            print("\n====================================")
            print(f" FORECAST FOR: {dish}")
            print("====================================")

            try:
                result = run_forecast_and_stock_check(
                    dish_name=dish,
                    horizon_weeks=args.weeks,
                    menu_path=menu_path,
                    pantry_path=pantry_path,
                    sales_path=sales_path
                )
                all_results.append(result)

            except Exception as e:
                print(f"Skipping {dish}: {e}")

        # AFTER THE LOOP, now we can aggregate
        print("\n\n================ TOTAL PURCHASE LIST ================\n")

        final_list = aggregate_total_ingredient_needs(all_results, pantry)

        # Sort: NEED_TO_BUY first, highest to_buy on top
        final_list_sorted = sorted(
            final_list,
            key=lambda x: (x["status"] != "NEED_TO_BUY", -x["to_buy"])
        )

        # Header
        header = f"{'#':>3}  {'Ingredient':<30} {'Need':>15} {'Stock':>15} {'To buy':>15} {'Status':>10}"
        print(header)
        print("-" * len(header))

        # Rows
        for idx, item in enumerate(final_list_sorted, start=1):
            need_str  = f"{item['total_required']:,.2f} {item['unit']}"
            stock_str = f"{item['current_stock']:,.2f} {item['unit']}"
            buy_str   = "-" if item["status"] == "ENOUGH" else f"{item['to_buy']:,.2f} {item['unit']}"
            line = f"{idx:>3}  {item['ingredient']:<30} {need_str:>15} {stock_str:>15} {buy_str:>15} {item['status']:>10}"
            print(line)

    # ======================================================
    #   CASE 2: FORECAST ONE DISH ONLY
    # ======================================================
    else:
        dish = args.dish
        print("\n====================================")
        print(f" FORECAST FOR: {dish}")
        print("====================================")

        result = run_forecast_and_stock_check(
            dish_name=dish,
            horizon_weeks=args.weeks,
            menu_path=menu_path,
            pantry_path=pantry_path,
            sales_path=sales_path
        )
