# plot_ingredient_stock.py

import pandas as pd
import matplotlib.pyplot as plt

from restaurant_forecast_model import (
    load_data,
    run_forecast_and_stock_check,
    aggregate_total_ingredient_needs,
)


# How many weeks ahead to forecast
HORIZON_WEEKS = 4

# How many ingredients to show in the plot (sorted by shortage)
TOP_N = 20


def main():
    # File paths (adjust if yours are different)
    menu_path = "Menu.csv"
    pantry_path = "Pantry.csv"
    sales_path = "Sales.csv"
    ingredients_path = "Ingridients.csv"  # your per-portion file

    # Load base data so we can get dish list & pantry for aggregation
    menu, pantry, sales = load_data(menu_path, pantry_path, sales_path)

    all_dishes = menu["dish_name"].unique()
    all_results = []

    # 1) Run forecast + stock check for each dish
    for dish in all_dishes:
        print("\n====================================")
        print(f" FORECAST & STOCK CHECK FOR: {dish}")
        print("====================================")

        try:
            result = run_forecast_and_stock_check(
                dish_name=dish,
                horizon_weeks=HORIZON_WEEKS,
                menu_path=menu_path,
                pantry_path=pantry_path,
                sales_path=sales_path,
                ingredients_path=ingredients_path,
            )
            all_results.append(result)
        except Exception as e:
            print(f"  Skipping {dish}: {e}")

    # 2) Aggregate all ingredient needs across dishes
    final_list = aggregate_total_ingredient_needs(all_results, pantry)

    df = pd.DataFrame(final_list)

    # Sort by how much we need to buy (descending)
    df = df.sort_values("to_buy", ascending=False)

    # Optional: keep only ingredients where we actually need to buy something
    df_need = df[df["status"] == "NEED_TO_BUY"]

    # Limit to top N shortages for readability
    df_top = df_need.head(TOP_N)

    if df_top.empty:
        print("No ingredients need to be purchased. Pantry is sufficient.")
        return

    # 3) Plot Required vs In Stock
    x = range(len(df_top))

    plt.figure(figsize=(14, 6))
    plt.bar([i - 0.2 for i in x], df_top["total_required"], width=0.4, label="Required")
    plt.bar([i + 0.2 for i in x], df_top["current_stock"], width=0.4, label="In stock")

    plt.xticks(list(x), df_top["ingredient"], rotation=60, ha="right")
    plt.ylabel("Quantity")
    plt.title(f"Top {TOP_N} ingredients by shortage (required vs in stock)")
    plt.legend()
    plt.tight_layout()
    plt.show()

    # 4) (Optional) Plot just the shortage (to_buy)
    plt.figure(figsize=(14, 6))
    plt.bar(x, df_top["to_buy"])
    plt.xticks(list(x), df_top["ingredient"], rotation=60, ha="right")
    plt.ylabel("Quantity to buy")
    plt.title(f"Top {TOP_N} ingredients to buy over next {HORIZON_WEEKS} weeks")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()