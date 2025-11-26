# restaurant_final_forecast.py
#
# Forecast per dish with RandomForest, then aggregate
# total ingredient requirements and compare with pantry stock.

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor


# ============================================================
# 1. Load data
# ============================================================
def load_data(
    menu_path="Menu.csv",
    pantry_path="Pantry.csv",
    ingredients_path="Ingridients.csv",  # note spelling
    sales_path="Sales.csv",
):
    # Menu: dish definitions + ingredient list
    menu = pd.read_csv(menu_path, sep=";")

    # Pantry: current stock
    pantry = pd.read_csv(pantry_path)

    # Ingridients: per-ingredient usage per pizza
    ingredients = pd.read_csv(ingredients_path)

    # Sales history
    sales = pd.read_csv(sales_path, sep=";")
    sales["date"] = pd.to_datetime(sales["date"], dayfirst=True)
    sales["quantity"] = pd.to_numeric(sales["quantity"], errors="coerce").fillna(0)

    # Clean up columns
    menu.columns = [c.strip() for c in menu.columns]
    pantry.columns = [c.strip() for c in pantry.columns]
    ingredients.columns = [c.strip() for c in ingredients.columns]
    sales.columns = [c.strip() for c in sales.columns]

    return menu, pantry, ingredients, sales


# ============================================================
# 2. Build weekly aggregated sales
# ============================================================
def build_weekly_sales_dataset(sales: pd.DataFrame) -> pd.DataFrame:
    sales_idx = sales.set_index("date")

    weekly = (
        sales_idx
        .groupby("dish_name")
        .resample("W")["quantity"]
        .sum()
        .reset_index()
    )

    weekly["year"] = weekly["date"].dt.year
    weekly["weekofyear"] = weekly["date"].dt.isocalendar().week.astype(int)
    weekly["time_idx"] = weekly.groupby("dish_name").cumcount()
    return weekly


# ============================================================
# 3. Forecast per-dish using its own RandomForest
# ============================================================
def forecast_dish_portions(dish_name: str,
                           weekly: pd.DataFrame,
                           horizon_weeks: int) -> float:
    """
    Train a RandomForest on *only this dish* and forecast total portions
    for the next horizon_weeks.
    Returns: total_predicted_portions (float).
    """
    hist = weekly[weekly["dish_name"] == dish_name].sort_values("date")

    if hist.empty:
        return 0.0

    # If very few data points, just use mean as naive forecast
    if hist.shape[0] < 4:
        mean_q = hist["quantity"].mean()
        return float(mean_q * horizon_weeks)

    X = hist[["year", "weekofyear", "time_idx"]]
    y = hist["quantity"]

    # Time-based split (80% train)
    split_idx = int(len(hist) * 0.8)
    if split_idx < 1:
        split_idx = len(hist)  # fallback: all train

    X_train, y_train = X.iloc[:split_idx], y.iloc[:split_idx]

    rf = RandomForestRegressor(
        n_estimators=300,
        random_state=42,
        n_jobs=-1,
    )
    rf.fit(X_train, y_train)

    last_row = hist.iloc[-1]
    last_date = last_row["date"]
    last_time_idx = int(last_row["time_idx"])

    future_rows = []
    for i in range(1, horizon_weeks + 1):
        future_date = last_date + pd.Timedelta(weeks=i)
        future_rows.append({
            "year": future_date.year,
            "weekofyear": int(future_date.isocalendar().week),
            "time_idx": last_time_idx + i,
        })

    future_df = pd.DataFrame(future_rows)
    preds = rf.predict(future_df)

    return float(preds.sum())


# ============================================================
# 4. Ingredient parsing & per-ingredient usage
# ============================================================
def parse_ingredient_list(ingredient_str: str):
    if pd.isna(ingredient_str):
        return []
    return [x.strip() for x in str(ingredient_str).split(",") if x.strip()]


def build_per_pizza_usage_map(ingredients_df: pd.DataFrame):
    """
    Ingridients.csv structure assumed:

       ingredient_name, quantity, unit

    meaning: when an ingredient is used on a pizza, it uses
    `quantity` (in `unit`) per pizza.
    """
    usage = {}
    for _, row in ingredients_df.iterrows():
        name = str(row["ingredient_name"]).strip().lower()
        qty = float(row["quantity"])
        unit = str(row["unit"])
        usage[name] = (qty, unit)
    return usage


# ============================================================
# 5. Aggregate ingredient needs for all dishes
# ============================================================
def compute_total_ingredient_requirements(
    menu: pd.DataFrame,
    forecast_per_dish: dict,
    per_pizza_usage: dict,
    pantry: pd.DataFrame,
):
    """
    forecast_per_dish: dict[dish_name] = total_predicted_portions
    per_pizza_usage:  dict[ingredient_name_lower] = (qty_per_pizza, unit)
    pantry:           current stock

    Returns: list of dicts → final purchase list.
    """
    # Build menu mapping: dish -> [ingredient names]
    dish_to_ingredients = {}
    for _, row in menu.iterrows():
        dish = row["dish_name"]
        ing_list = parse_ingredient_list(row.get("ingredient", ""))
        dish_to_ingredients[dish] = ing_list

    # 1) Aggregate total need per ingredient (in the same unit as Ingridients.csv)
    agg_usage = {}  # ingredient_lower -> {"needed": float, "unit": str}

    for dish, portions in forecast_per_dish.items():
        if portions <= 0:
            continue
        ing_list = dish_to_ingredients.get(dish, [])
        for ing in ing_list:
            key = ing.strip().lower()
            if key not in per_pizza_usage:
                # No usage definition found for this ingredient; skip or log
                continue
            per_qty, unit = per_pizza_usage[key]
            needed = portions * per_qty  # total needed amount in 'unit'

            if key not in agg_usage:
                agg_usage[key] = {"needed": 0.0, "unit": unit}
            agg_usage[key]["needed"] += needed

    # 2) Compare with pantry
    pantry_clean = pantry.copy()
    pantry_clean["ingredient_name_clean"] = pantry_clean["ingredient_name"].str.lower()

    final_list = []
    for ing_key, info in agg_usage.items():
        needed = info["needed"]
        unit = info["unit"]

        row = pantry_clean[pantry_clean["ingredient_name_clean"] == ing_key]
        if not row.empty:
            stock = float(row.iloc[0]["quantity"])
            stock_unit = str(row.iloc[0]["unit"])
        else:
            stock = 0.0
            stock_unit = unit

        # (Assuming same unit; if not, you'd need conversion logic)
        deficit = needed - stock

        final_list.append({
            "ingredient": ing_key,  # lowercased name
            "needed": needed,
            "stock": stock,
            "unit": unit,
            "to_buy": max(deficit, 0.0),
            "status": "NEED_TO_BUY" if deficit > 0 else "ENOUGH",
        })

    # Sort by name for nicer output
    final_list.sort(key=lambda x: x["ingredient"])
    return final_list


# ============================================================
# 6. Main – glue it all together
# ============================================================
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Per-dish RandomForest forecast and total ingredient requirement calculator."
    )
    parser.add_argument(
        "--weeks",
        type=int,
        default=4,
        help="Number of weeks to forecast (1 = next week, 4 = ~next month).",
    )
    args = parser.parse_args()
    horizon_weeks = args.weeks

    # 1) Load everything
    menu, pantry, ingredients, sales = load_data()

    # 2) Build weekly sales
    weekly = build_weekly_sales_dataset(sales)

    # 3) Build per-ingredient per-pizza usage map
    per_pizza_usage = build_per_pizza_usage_map(ingredients)

    # 4) Forecast per dish
    forecast_per_dish = {}
    all_dishes = menu["dish_name"].unique()
    for dish in all_dishes:
        total_portions = forecast_dish_portions(dish, weekly, horizon_weeks)
        forecast_per_dish[dish] = total_portions

    # 5) Aggregate ingredient needs and compare with pantry
    final_purchase_list = compute_total_ingredient_requirements(
        menu=menu,
        forecast_per_dish=forecast_per_dish,
        per_pizza_usage=per_pizza_usage,
        pantry=pantry,
    )

    # 6) Print final result
    print(f"\n========= FINAL TOTAL INGREDIENT REQUIREMENTS (next {horizon_weeks} week(s)) =========\n")
    for item in final_purchase_list:
        if item["to_buy"] > 0:
            action = f"BUY {item['to_buy']:.2f}{item['unit']}"
        else:
            action = "ENOUGH"

        print(
            f"{item['ingredient']}: need={item['needed']:.2f}{item['unit']}, "
            f"stock={item['stock']:.2f}{item['unit']} → {action}"
        )