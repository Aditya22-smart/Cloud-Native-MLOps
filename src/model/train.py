"""Train and export the dynamic pricing regression pipeline."""
import argparse
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data/pricing_dataset.csv"
MODEL_PATH = ROOT / "src/model/pipeline.pkl"

FEATURES = [
    "Base_Price",
    "Competitor_Price",
    "Inventory_Level",
    "Units_Sold_Past_7D",
    "Promotion_Type",
    "Discount_Pct",
    "Seasonal_Trend",
]
TARGET = "Optimal_Price"
NUMERIC = [f for f in FEATURES if f != "Promotion_Type"]
CATEGORICAL = ["Promotion_Type"]


def make_pipeline(model):
    numeric_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])
    categorical_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ])
    prep = ColumnTransformer([
        ("numeric", numeric_pipeline, NUMERIC),
        ("categorical", categorical_pipeline, CATEGORICAL),
    ])
    return Pipeline([("preprocessor", prep), ("model", model)])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default=str(DATA_PATH))
    parser.add_argument("--output", default=str(MODEL_PATH))
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    df = pd.read_csv(args.data)
    missing = sorted(set(FEATURES + [TARGET]) - set(df.columns))
    if missing:
        raise ValueError(f"Training CSV missing columns: {missing}")
    if df.empty:
        raise ValueError("Training dataset is empty")

    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna(subset=[TARGET])
    X, y = df[FEATURES], df[TARGET].astype(float)

    x_train, x_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=args.seed
    )

    candidates = {
        "random_forest": RandomForestRegressor(
            n_estimators=150, min_samples_leaf=2,
            random_state=args.seed, n_jobs=-1,
        ),
        "gradient_boosting": GradientBoostingRegressor(
            random_state=args.seed, n_estimators=100,
        ),
    }

    results = []
    best_name, best_model, best_mae = None, None, float("inf")

    for name, estimator in candidates.items():
        pipeline = make_pipeline(estimator)
        pipeline.fit(x_train, y_train)
        predictions = pipeline.predict(x_test)
        mae = mean_absolute_error(y_test, predictions)
        rmse = np.sqrt(mean_squared_error(y_test, predictions))
        r2 = r2_score(y_test, predictions)
        results.append((name, mae, rmse, r2))
        print(f"{name}: MAE={mae:.4f}, RMSE={rmse:.4f}, R2={r2:.4f}")

        if mae < best_mae:
            best_name, best_model, best_mae = name, pipeline, mae

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_model, output)

    print(f"Selected model (lowest validation MAE): {best_name}")
    print(f"Saved pipeline: {output}")
    print(f"Training rows: {len(x_train)}; validation rows: {len(x_test)}")
    print("Reminder: scores measure fit to the derived heuristic target.")


if __name__ == "__main__":
    main()
