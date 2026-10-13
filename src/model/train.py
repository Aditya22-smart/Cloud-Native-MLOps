from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "data" / "pricing_dataset.csv"
MODEL_PATH = PROJECT_ROOT / "src" / "model" / "pipeline.pkl"

TARGET = "Optimal_Price"

NUMERIC_FEATURES = [
    "Base_Price",
    "Competitor_Price",
    "Inventory_Level",
    "Units_Sold_Past_7D",
    "Discount_Pct",
    "Seasonal_Trend",
]
CATEGORICAL_FEATURES = ["Promotion_Type"]
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES


def main():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_PATH}. "
            "Run generate_dataset.py first."
        )

    data = pd.read_csv(DATA_PATH)
    required = FEATURES + [TARGET]
    missing = sorted(set(required) - set(data.columns))
    if missing:
        raise ValueError(f"Dataset is missing columns: {missing}")
    if data.empty or data[required].isna().any().any():
        raise ValueError("Dataset is empty or contains missing values.")

    X = data[FEATURES]
    y = data[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    preprocessing = ColumnTransformer(
        transformers=[
            ("categorical", OneHotEncoder(handle_unknown="ignore"),
             CATEGORICAL_FEATURES),
            ("numeric", "passthrough", NUMERIC_FEATURES),
        ]
    )

    pipeline = Pipeline([
        ("preprocessing", preprocessing),
        ("regressor", RandomForestRegressor(
            n_estimators=20,
            max_depth=16,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1,
        )),
    ])

    pipeline.fit(X_train, y_train)
    predictions = pipeline.predict(X_test)

    print(f"MAE:  {mean_absolute_error(y_test, predictions):.3f}")
    print(f"RMSE: {mean_squared_error(y_test, predictions) ** 0.5:.3f}")
    print(f"R2:   {r2_score(y_test, predictions):.4f}")

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    print(f"Saved trained pipeline: {MODEL_PATH}")
    print(f"Model size: {MODEL_PATH.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
