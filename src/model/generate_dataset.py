"""Convert the Kaggle retail dataset into the project's pricing schema.

Optimal_Price is a documented heuristic target, not a measured business optimum.
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / "data/raw/retail_store_inventory.csv"
DEFAULT_OUTPUT = ROOT / "data/pricing_dataset.csv"

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


def build_dataset(input_path, output_path, rows=None, demand_shift=0.0, seed=42):
    df = pd.read_csv(input_path)

    required = [
        "Date", "Store ID", "Product ID", "Inventory Level",
        "Units Sold", "Price", "Discount", "Competitor Pricing",
        "Seasonality", "Holiday/Promotion",
    ]
    missing = sorted(set(required) - set(df.columns))
    if missing:
        raise ValueError(f"Missing required Kaggle columns: {missing}")

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    numeric_cols = [
        "Inventory Level", "Units Sold", "Price", "Discount",
        "Competitor Pricing",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["Date"] + numeric_cols).copy()
    df = df[
        (df["Price"] > 0)
        & (df["Competitor Pricing"] > 0)
        & (df["Inventory Level"] >= 0)
        & (df["Units Sold"] >= 0)
    ].copy()

    df = df.sort_values(["Store ID", "Product ID", "Date"])
    group_cols = ["Store ID", "Product ID"]

    # Rolling sales history: only current and previous records, never future rows.
    df["Units_Sold_Past_7D"] = (
        df.groupby(group_cols)["Units Sold"]
        .transform(lambda s: s.rolling(7, min_periods=1).sum())
    )

    df["Base_Price"] = df["Price"].astype(float)
    df["Competitor_Price"] = df["Competitor Pricing"].astype(float)
    df["Inventory_Level"] = df["Inventory Level"].astype(int)
    df["Discount_Pct"] = df["Discount"].clip(0, 100).astype(float)

    # Standardize seasonality to a numeric multiplier.
    season_map = {
        "winter": 0.95,
        "spring": 1.00,
        "summer": 1.05,
        "autumn": 1.02,
        "fall": 1.02,
    }
    df["Seasonal_Trend"] = (
        df["Seasonality"].astype(str).str.lower().map(season_map).fillna(1.0)
    )

    promotion = pd.Series("none", index=df.index, dtype="object")
    promotion.loc[df["Discount_Pct"] > 0] = "percentage"
    holiday = pd.to_numeric(
        df["Holiday/Promotion"], errors="coerce"
    ).fillna(0).astype(bool)
    promotion.loc[holiday & (df["Discount_Pct"] > 0)] = "bundle"
    promotion.loc[df["Discount_Pct"] >= 40] = "clearance"
    df["Promotion_Type"] = promotion

    # Apply optional synthetic demand shift for drift/retraining experiments.
    df["Units_Sold_Past_7D"] = (
        df["Units_Sold_Past_7D"] * (1.0 + demand_shift)
    ).clip(lower=0)

    # Documented heuristic target:
    # anchor toward competitor price; adjust modestly for demand and stock.
    # This is not a ground-truth optimal price from the Kaggle source.
    demand_ratio = (
        df["Units_Sold_Past_7D"] /
        (df["Units_Sold_Past_7D"].median() + 1e-6)
    ).clip(0.5, 1.5)

    inventory_ratio = (
        df["Inventory_Level"] /
        (df["Inventory_Level"].median() + 1e-6)
    ).clip(0.5, 1.5)

    competitor_anchor = (
        0.6 * df["Base_Price"] + 0.4 * df["Competitor_Price"]
    )
    demand_adjustment = 1.0 + 0.08 * (demand_ratio - 1.0)
    inventory_adjustment = 1.0 - 0.06 * (inventory_ratio - 1.0)

    result = df[FEATURES].copy()
    result[TARGET] = (
        competitor_anchor * demand_adjustment * inventory_adjustment
    ).clip(lower=0.01).round(2)

    result = result.replace([np.inf, -np.inf], np.nan).dropna()
    if rows is not None:
        result = result.head(rows)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False)

    print(f"Input: {input_path}")
    print(f"Output: {output_path}")
    print(f"Rows written: {len(result)}")
    print(f"Columns: {result.columns.tolist()}")
    print(f"Random seed recorded for reproducibility: {seed}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--rows", type=int, default=None)
    parser.add_argument("--demand-shift", type=float, default=0.0)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    if args.rows is not None and args.rows <= 0:
        parser.error("--rows must be positive")
    if args.demand_shift <= -1:
        parser.error("--demand-shift must be greater than -1")

    build_dataset(
        args.input, args.output, args.rows, args.demand_shift, args.seed
    )


if __name__ == "__main__":
    main()
