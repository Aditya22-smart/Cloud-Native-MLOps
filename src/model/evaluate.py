"""Evaluate the exported pricing pipeline on a held-out test split."""
import argparse
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split


ROOT = Path(__file__).resolve().parents[2]
FEATURES = [
    "Base_Price", "Competitor_Price", "Inventory_Level",
    "Units_Sold_Past_7D", "Promotion_Type", "Discount_Pct",
    "Seasonal_Trend",
]
TARGET = "Optimal_Price"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default=str(ROOT / "data/pricing_dataset.csv"))
    parser.add_argument("--model", default=str(ROOT / "src/model/pipeline.pkl"))
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    df = pd.read_csv(args.data)
    X_train, X_test, y_train, y_test = train_test_split(
        df[FEATURES], df[TARGET].astype(float),
        test_size=0.2, random_state=args.seed,
    )
    model = joblib.load(args.model)
    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    r2 = r2_score(y_test, predictions)
    nonzero = np.abs(y_test.to_numpy()) > 1e-8
    mape = (
        np.mean(
            np.abs(
                (y_test.to_numpy()[nonzero] - predictions[nonzero])
                / y_test.to_numpy()[nonzero]
            )
        ) * 100
        if nonzero.any() else float("nan")
    )

    print(f"MAE:  {mae:.4f}")
    print(f"RMSE: {rmse:.4f}")
    print(f"R2:   {r2:.4f}")
    print(f"MAPE: {mape:.2f}%")
    print("Warning: evaluation is against a derived heuristic target.")


if __name__ == "__main__":
    main()
