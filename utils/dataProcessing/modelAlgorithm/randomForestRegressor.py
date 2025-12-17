import os
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline

def train_random_forest(data):
    # Features and target
    feature_cols = ["dish_name", "year", "time_idx","weekOfYear", "pastWeeklySalesAvg"]
    target_col = "quantity"

    processed_data = dataPrep(data)

    for dish_name, dish_sales in processed_data.items():
        if len(dish_sales) < 8:  # Need at least 8 rows (7 for pastWeeklySalesAvg + 1 for training)
            print(f"Skipping {dish_name}: insufficient data ({len(dish_sales)} rows)")
            continue

        X = dish_sales[feature_cols]
        y = dish_sales[target_col]

        # Split train / test by time (80% / 20%)
        split_idx = int(len(dish_sales) * 0.8)
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

        # Categorical + numeric preprocessing
        categorical_cols = ["dish_name"]
        numeric_cols = ["year", "weekOfYear", "time_idx", "pastWeeklySalesAvg"]

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
        
        model_path = "model/" + dish_name + ".pkl"

        # Persist model to disk so it can be reused without retraining
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        joblib.dump(model, model_path)
        print(f"Model saved to {model_path}")

    return processed_data

def dataPrep(salesData):
    required_cols = {"date", "dish_name", "quantity"}
    if not required_cols.issubset(set(salesData.columns)):
        missing = required_cols - set(salesData.columns)
        raise ValueError(f"Sales is missing required columns: {missing}")

    # Make sure date is a datetime
    salesData["date"] = pd.to_datetime(salesData["date"])

    # Set index to date for resampling
    sales_idx = salesData.set_index("date")

    # Daily quantity per dish_name
    daily = (
        sales_idx
        .groupby("dish_name")
        .resample("D")["quantity"]
        .sum()
        .reset_index()
    )

    # Sort to ensure correct time order per dish
    daily = daily.sort_values(["dish_name", "date"])

    # Calendar features
    daily["year"] = daily["date"].dt.year
    daily["weekOfYear"] = daily["date"].dt.isocalendar().week.astype(int)

    # Split dataframe by dish_name into smaller dataframes
    dish_dataframes = {}
    for dish_name in daily["dish_name"].unique():
        dish_df = daily[daily["dish_name"] == dish_name].copy()
        
        dish_df['pastWeeklySalesAvg'] = (
            dish_df["quantity"].rolling(window=7, min_periods=7).mean().shift(1)
        )
        dish_df = dish_df.dropna(subset=["pastWeeklySalesAvg"])

        dish_df = dish_df.reset_index(drop=True)
        dish_df["time_idx"] = dish_df.index

        dish_dataframes[dish_name] = dish_df

        # print(dish_dataframes[dish_name].head(30))

    return dish_dataframes