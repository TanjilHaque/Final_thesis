
"""
generate_40x60_heterogeneous_dataset.py

Creates a 40×60 transportation problem dataset with:

- Heterogeneous cost regions
- Low-cost anomalies
- High-cost anomalies
- Balanced supply and demand
- Reproducible random seed

Output:
    dataset_40x60_heterogeneous.json
"""

import json
import numpy as np

# ==========================================================
# CONFIGURATION
# ==========================================================

SEED = 42

NUM_SOURCES = 40
NUM_DESTINATIONS = 60

LOW_ANOMALY_PERCENT = 0.05
HIGH_ANOMALY_PERCENT = 0.05

OUTPUT_FILE = "dataset_40x60_heterogeneous.json"

# ==========================================================
# RANDOM GENERATOR
# ==========================================================

rng = np.random.default_rng(SEED)

# ==========================================================
# COST MATRIX GENERATION
# ==========================================================

cost_matrix = np.zeros(
    (NUM_SOURCES, NUM_DESTINATIONS),
    dtype=int
)

# ----------------------------------------------------------
# Rows 1-10 : Low-cost region
# ----------------------------------------------------------

cost_matrix[0:10] = rng.integers(
    low=5,
    high=51,
    size=(10, NUM_DESTINATIONS)
)

# ----------------------------------------------------------
# Rows 11-20 : Medium-cost region
# ----------------------------------------------------------

cost_matrix[10:20] = rng.integers(
    low=50,
    high=251,
    size=(10, NUM_DESTINATIONS)
)

# ----------------------------------------------------------
# Rows 21-30 : High-cost region
# ----------------------------------------------------------

cost_matrix[20:30] = rng.integers(
    low=250,
    high=701,
    size=(10, NUM_DESTINATIONS)
)

# ----------------------------------------------------------
# Rows 31-40 : Very high-cost region
# ----------------------------------------------------------

cost_matrix[30:40] = rng.integers(
    low=700,
    high=1501,
    size=(10, NUM_DESTINATIONS)
)

# ==========================================================
# INJECT LOW-COST ANOMALIES
# ==========================================================

total_cells = NUM_SOURCES * NUM_DESTINATIONS

num_low_anomalies = int(
    total_cells * LOW_ANOMALY_PERCENT
)

low_indices = rng.choice(
    total_cells,
    size=num_low_anomalies,
    replace=False
)

rows = low_indices // NUM_DESTINATIONS
cols = low_indices % NUM_DESTINATIONS

cost_matrix[rows, cols] = rng.integers(
    low=1,
    high=6,
    size=num_low_anomalies
)

# ==========================================================
# INJECT HIGH-COST ANOMALIES
# ==========================================================

remaining_indices = np.setdiff1d(
    np.arange(total_cells),
    low_indices
)

num_high_anomalies = int(
    total_cells * HIGH_ANOMALY_PERCENT
)

high_indices = rng.choice(
    remaining_indices,
    size=num_high_anomalies,
    replace=False
)

rows = high_indices // NUM_DESTINATIONS
cols = high_indices % NUM_DESTINATIONS

cost_matrix[rows, cols] = rng.integers(
    low=2000,
    high=3001,
    size=num_high_anomalies
)

# ==========================================================
# SUPPLY GENERATION
# ==========================================================

supply = rng.integers(
    low=50,
    high=1001,
    size=NUM_SOURCES
)

total_supply = int(np.sum(supply))

# ==========================================================
# DEMAND GENERATION
# ==========================================================

raw_demand = rng.integers(
    low=50,
    high=1001,
    size=NUM_DESTINATIONS
)

scaled_demand = (
    raw_demand / raw_demand.sum()
) * total_supply

demand = np.round(
    scaled_demand
).astype(int)

# ==========================================================
# EXACT BALANCING
# ==========================================================

difference = total_supply - int(np.sum(demand))

demand[-1] += difference

assert np.sum(supply) == np.sum(demand), \
    "Balancing failed."

# ==========================================================
# DATASET OBJECT
# ==========================================================

dataset = {
    "metadata": {
        "name": "40x60 Heterogeneous Anomaly Dataset",
        "seed": SEED,
        "sources": NUM_SOURCES,
        "destinations": NUM_DESTINATIONS,
        "total_supply": int(np.sum(supply)),
        "total_demand": int(np.sum(demand))
    },
    "cost_matrix": cost_matrix.tolist(),
    "supply": supply.tolist(),
    "demand": demand.tolist()
}

# ==========================================================
# SAVE JSON
# ==========================================================

with open(OUTPUT_FILE, "w") as f:
    json.dump(
        dataset,
        f,
        indent=4
    )

print("=" * 60)
print("Dataset generated successfully.")
print(f"Saved to: {OUTPUT_FILE}")
print(f"Matrix size : {NUM_SOURCES} x {NUM_DESTINATIONS}")
print(f"Total Supply: {np.sum(supply)}")
print(f"Total Demand: {np.sum(demand)}")
print("=" * 60)

