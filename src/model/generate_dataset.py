import argparse
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "pricing_dataset.csv"


def generate_dataset(rows=50000, seed=42):
    """Generate reproducible synthetic dynamic-pricing data."""
    if rows < 1:
        raise ValueError("rows must be at least 1")

    rng = np.random.default_rng(seed)

    base_price = rng.uniform(5, 500, rows).round(2)
    competitor_price = (
        base_price * rng.uniform(0.75, 1.25, rows)
    ).round(2)

    inventory_level = rng.integers(0, 1001, rows)
    units_sold = rng.integers(0, 501, rows)

    promotion_type = rng.choice(
        ["none", "percentage", "bundle", "clearance"],
        size=rows,
        p=[0.45, 0.30, 0.15, 0.10],
    )

    discount_pct = np.where(
        promotion_type == "none",
        0.0,
        rng.uniform(5, 50, rows),
    ).round(2)

    seasonal_trend = rng.uniform(0.7, 1.4, rows).round(3)

    demand_factor = 1 + (units_sold - 100) / 1000
    inventory_factor = 1 + (300 - inventory_level) / 3000
    promotion_factor = 1 - discount_pct / 200

    optimal_price = (
        0.45 * base_price
        + 0.35 * competitor_price
        + 0.20 * base_price
        * demand_factor
        * inventory_factor
        * seasonal_trend
    ) * promotion_factor

    optimal_price = np.clip(
        optimal_price,
        base_price * 0.5,
        base_price * 1.5,
    )

    return pd.DataFrame({
        "Base_Price": base_price,
        "Competitor_Price": competitor_price,
        "Inventory_Level": inventory_level,
        "Units_Sold_Past_7D": units_sold,
        "Promotion_Type": promotion_type,
        "Discount_Pct": discount_pct,
        "Seasonal_Trend": seasonal_trend,
        "Optimal_Price": optimal_price.round(2),
    })


def main():
    parser = argparse.ArgumentParser(
        description="Generate synthetic pricing data."
    )
    parser.add_argument("--rows", type=int, default=50000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    dataset = generate_dataset(args.rows, args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    dataset.to_csv(args.output, index=False)

    print(f"Generated {len(dataset)} rows at {args.output}")
    print(f"Columns: {', '.join(dataset.columns)}")


if __name__ == "__main__":
    main()
