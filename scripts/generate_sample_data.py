import os
import random
from pathlib import Path

import numpy as np
import pandas as pd

random.seed(42)
np.random.seed(42)

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

output_file = RAW_DIR / "shipments_sample.csv"

suppliers = [
    "EcoRoute Ltd",
    "NorthSea Global",
    "SkyBridge Cargo",
    "GreenRail Freight",
    "TerraLogix",
    "UrbanMove Transport",
]

transport_modes = ["road", "sea", "rail", "air"]
regions = ["Dublin", "Cork", "Galway", "Limerick", "Belfast", "London", "Paris", "Berlin"]
categories = ["Electronics", "Food", "Clothing", "Machinery", "Pharma", "Furniture"]

emission_factors = {
    "road": 0.15,
    "sea": 0.008,
    "rail": 0.03,
    "air": 0.65,
}

rows = []

for _ in range(2000):
    supplier_name = random.choice(suppliers)
    transport_mode = random.choice(transport_modes)
    weight_tons = round(random.uniform(0.5, 20.0), 2)
    distance_km = round(random.uniform(50, 3000), 2)
    origin_region = random.choice(regions)
    destination_region = random.choice(regions)
    product_category = random.choice(categories)

    base_co2 = weight_tons * distance_km * emission_factors[transport_mode]

    # Add realistic variation/noise
    supplier_factor = random.uniform(0.95, 1.10)
    category_factor = random.uniform(0.97, 1.08)
    noise = np.random.normal(0, base_co2 * 0.05)

    co2_emission = max(0, round(base_co2 * supplier_factor * category_factor + noise, 2))

    if co2_emission < 100:
        high_emission_risk = "Low"
    elif co2_emission < 300:
        high_emission_risk = "Medium"
    else:
        high_emission_risk = "High"

    rows.append(
        {
            "supplier_name": supplier_name,
            "transport_mode": transport_mode,
            "weight_tons": weight_tons,
            "distance_km": distance_km,
            "origin_region": origin_region,
            "destination_region": destination_region,
            "product_category": product_category,
            "co2_emission": co2_emission,
            "high_emission_risk": high_emission_risk,
        }
    )

df = pd.DataFrame(rows)
df.to_csv(output_file, index=False)

print(f"Sample dataset created: {output_file}")
print(df.head())
print(f"Total rows: {len(df)}")