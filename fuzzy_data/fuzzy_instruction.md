# Fuzzy Logic System — Instruction Guide

This document explains the **IT2-TFS Fuzzifier** and **IT2-TFS Defuzzifier** modules, what they do, and how to implement them.

---

## Table of Contents

1. [Overview](#overview)
2. [Part 1 — IT2-TFS Fuzzifier (`it2_fuzzifier.py`)](#part-1--it2-tfs-fuzzifier-it2_fuzzifierpy)
   - [What It Does](#what-it-does)
   - [Theoretical Framework](#theoretical-framework)
   - [Architecture (9 Layers)](#architecture-9-layers)
   - [How to Implement / Run](#how-to-implement--run)
   - [Parameters](#parameters)
   - [Input Format](#input-format)
   - [Output Format](#output-format)
3. [Part 2 — IT2-TFS Defuzzifier (`it2_defuzzifier.py`)](#part-2--it2-tfs-defuzzifier-it2_defuzzifierpy)
   - [What It Does](#what-it-does-1)
   - [Theoretical Framework](#theoretical-framework-1)
   - [Architecture (6 Layers)](#architecture-6-layers)
   - [How to Implement / Run](#how-to-implement--run-1)
   - [Parameters](#parameters-1)
   - [Input Format](#input-format-1)
   - [Output Format](#output-format-1)
4. [End-to-End Workflow](#end-to-end-workflow)

---

## Overview

The fuzzy logic system converts a **crisp transportation problem** into an **Interval Type-2 Trapezoidal Fuzzy Set (IT2-TFS)** representation and back. It consists of two complementary modules:

| Module          | File                 | Purpose                                  |
| --------------- | -------------------- | ---------------------------------------- |
| **Fuzzifier**   | `it2_fuzzifier.py`   | Converts crisp numbers → IT2-TFS objects |
| **Defuzzifier** | `it2_defuzzifier.py` | Converts IT2-TFS objects → crisp numbers |

---

## Part 1 — IT2-TFS Fuzzifier (`it2_fuzzifier.py`)

### What It Does

The fuzzifier transforms a crisp transportation problem dataset (cost matrix, supply vector, demand vector) into a full **Interval Type-2 Trapezoidal Fuzzy Set (IT2-TFS)** representation. Each crisp number becomes an IT2-TFS object defined by:

- **UMF (Upper Membership Function):** Encodes geometric uncertainty — the outer trapezoid with height always `1.0`.
- **LMF (Lower Membership Function):** Encodes epistemic (knowledge) uncertainty — the inner trapezoid with height `hL` representing confidence.

The fuzzifier introduces **three strictly separated uncertainty dimensions** that never influence each other:

| Dimension                    | Affects              | Parameters                                                                                              |
| ---------------------------- | -------------------- | ------------------------------------------------------------------------------------------------------- |
| **A. Geometric Uncertainty** | UMF only             | `δ` (base spread), `α` (left inner asymmetry), `β` (right inner asymmetry), `γ` (right outer asymmetry) |
| **B. Epistemic Uncertainty** | LMF only             | `r` (reliability score, derived from variability and position)                                          |
| **C. Confidence**            | LMF height `hL` only | `v` (variability score)                                                                                 |

### Theoretical Framework

**UMF Formula (Geometric Uncertainty):**

```
a1 = x × (1 − δ)
a2 = x × (1 − αδ)
a3 = x × (1 + βδ)
a4 = x × (1 + γδ)
height = 1.0
```

**LMF Formula (Epistemic Uncertainty):**

```
b1 = x × (1 − r·δ)
b2 = x × (1 − r·α·δ)
b3 = x × (1 + r·β·δ)
b4 = x × (1 + r·γ·δ)
```

**LMF Height (Confidence):**

```
hL = h_min + (1 − v) × (h_max − h_min)
```

**Variability (v):**

```
Cost matrix:  v_ij = (2·σ_row(i) + σ_col(j)) / (σ_global + ε)
Supply/Demand: v_k = σ_vector / (σ_global + ε)
```

**Reliability (r):**

```
Cost:    S = 0.65·e^(−v) + 0.35·(1 − x_norm)   → r = clip(0.3 + 0.6·S, 0.3, 0.9)
Supply:  S = 0.70·e^(−v) + 0.30·x_norm         → r = clip(0.3 + 0.6·S, 0.3, 0.9)
Demand:  S = 0.55·e^(−v) + 0.45·x_norm         → r = clip(0.3 + 0.6·S, 0.3, 0.9)
```

### Architecture (9 Layers)

The fuzzifier is organized into 9 strictly separated layers:

| Layer | Class                 | Responsibility                                                               |
| ----- | --------------------- | ---------------------------------------------------------------------------- |
| 1     | `InputValidator`      | Validates JSON structure: required keys, rectangular matrix, positive values |
| 2     | `StatisticsEngine`    | Computes global & local statistics (min, max, mean, std, row_std, col_std)   |
| 3     | `VariabilityEngine`   | Computes normalized variability scores `v ∈ [0, 1]`                          |
| 4     | `ReliabilityEngine`   | Computes reliability scores `r ∈ [0.3, 0.9]` (type-specific formulas)        |
| 5     | `UMFBuilder`          | Builds UMF trapezoid coordinates `[a1, a2, a3, a4]`                          |
| 6     | `LMFBuilder`          | Builds LMF trapezoid coordinates `[b1, b2, b3, b4]`                          |
| 7     | `HeightEngine`        | Computes LMF height `hL ∈ [h_min, h_max]`                                    |
| 8     | `StructuralValidator` | Enforces nesting constraint `a1 ≤ b1 ≤ b2 ≤ b3 ≤ b4 ≤ a4`                    |
| 9     | `OutputSerializer`    | Converts arrays to JSON-serializable IT2FS objects                           |

### How to Implement / Run

**Step 1: Prepare your crisp input JSON file** (e.g., `my_crisp_data.json`):

```json
{
  "cost_matrix": [
    [2.32, 5.19, 7.25],
    [2.13, 5.19, 8.12]
  ],
  "supply": [5.41, 8.01],
  "demand": [2.19, 2.19, 8.13]
}
```

**Step 2: Create a Python script** (e.g., `run_fuzzifier.py`):

```python
import json
from it2_fuzzifier import IT2TFSFuzzifier

# Load crisp data
with open("my_crisp_data.json", "r") as f:
    data = json.load(f)

# Initialize fuzzifier with desired parameters
fuzzifier = IT2TFSFuzzifier(
    delta=0.15,
    alpha=0.45,
    beta=0.75,
    gamma=1.15,
    h_min=0.40,
    h_max=0.95,
)

# Transform crisp data → fuzzy data
result = fuzzifier.transform(data)

# Export to JSON
fuzzifier.export(result, "my_fuzzy_data.json")
```

**Step 3: Run the script:**

```bash
python run_fuzzifier.py
```

### Parameters

| Parameter | Default | Range    | Description                                                               |
| --------- | ------- | -------- | ------------------------------------------------------------------------- |
| `delta`   | `0.15`  | `(0, 1)` | Base spread — controls overall width of the fuzzy support                 |
| `alpha`   | `0.45`  | `(0, 1)` | Left inner asymmetry — `α < 1` pulls inner left shoulder closer to core   |
| `beta`    | `0.75`  | `(0, 1)` | Right inner asymmetry — `β < 1` pulls inner right shoulder closer to core |
| `gamma`   | `1.15`  | `> 0`    | Right outer asymmetry — `γ > 1` makes outer right boundary wider          |
| `h_min`   | `0.40`  | `(0, 1)` | Minimum LMF height (confidence floor for high variability)                |
| `h_max`   | `0.95`  | `(0, 1)` | Maximum LMF height (confidence ceiling for low variability)               |

### Input Format

The fuzzifier expects a JSON object with three keys:

```json
{
  "cost_matrix": [[<float>, ...], ...],   // 2D list, m rows × n columns
  "supply":      [<float>, ...],           // 1D list, m elements
  "demand":      [<float>, ...]            // 1D list, n elements
}
```

**Validation rules enforced:**

- All three keys must be present.
- `cost_matrix` must be rectangular (all rows same length).
- `len(supply) == number of rows in cost_matrix`.
- `len(demand) == number of columns in cost_matrix`.
- All values must be strictly positive (`> 0`).

### Output Format

The output is a JSON object with `metadata` and three IT2-TFS arrays:

```json
{
  "metadata": {
    "delta": 0.15,
    "alpha": 0.45,
    "beta": 0.75,
    "gamma": 1.15,
    "h_min": 0.40,
    "h_max": 0.95,
    "corrections_applied": 0,
    "statistics": {
      "global_min": ...,
      "global_max": ...,
      "global_mean": ...,
      "global_std": ...
    }
  },
  "cost_matrix": [
    [
      {"umf": [a1, a2, a3, a4, 1.0], "lmf": [b1, b2, b3, b4, hL]},
      ...
    ],
    ...
  ],
  "supply": [
    {"umf": [a1, a2, a3, a4, 1.0], "lmf": [b1, b2, b3, b4, hL]},
    ...
  ],
  "demand": [
    {"umf": [a1, a2, a3, a4, 1.0], "lmf": [b1, b2, b3, b4, hL]},
    ...
  ]
}
```

**IT2FS object structure:**

- `umf`: 5-element list `[a1, a2, a3, a4, 1.0]` — height is always `1.0`.
- `lmf`: 5-element list `[b1, b2, b3, b4, hL]` — height is the confidence scalar.

**Nesting constraint (always enforced):**

```
a1 ≤ b1 ≤ b2 ≤ b3 ≤ b4 ≤ a4
```

---

## Part 2 — IT2-TFS Defuzzifier (`it2_defuzzifier.py`)

### What It Does

The defuzzifier converts IT2-TFS objects back into crisp numbers using the **Karnik-Mendel (KM) centroid algorithm**. Because IT2-TFS has an interval of membership grades (not a single grade), the centroid is also an interval `[y_l, y_r]`. The final crisp value is the mean:

```
y* = (y_l + y_r) / 2
```

After defuzzification, a **Balance Enforcement** layer restores the transportation balance constraint (`sum(supply) == sum(demand)`) using proportional normalization, because the fuzzifier's different reliability formulas for supply vs. demand cause a tiny imbalance in the defuzzified values.

### Theoretical Framework

**Trapezoidal Membership Function:**

```
mu(x) = 0                    if x <= p1 or x >= p4
mu(x) = h × (x − p1) / (p2 − p1)    if p1 < x <= p2
mu(x) = h                      if p2 < x <= p3
mu(x) = h × (p4 − x) / (p4 − p3)    if p3 < x < p4
```

**Karnik-Mendel Algorithm (per IT2FS):**

1. Discretize support `[a1, a4]` into `N` equally spaced sample points.
2. Evaluate `UMF(x_i)` and `LMF(x_i)` at every sample point.
3. Initialize weights `w_i = (UMF(x_i) + LMF(x_i)) / 2`.
4. Compute initial centroid `y = sum(x_i × w_i) / sum(w_i)`.
5. Find switch index `k = argmax { x_i : x_i <= y }`.
6. Update weights: `w_i = UMF(x_i)` if `i <= k` else `LMF(x_i)`.
7. Compute new `y` and repeat until convergence (`|y_new − y_old| < tolerance`).

**Left Centroid `y_l`:** samples left of `k*` use UMF, right use LMF.  
**Right Centroid `y_r`:** samples left of `k*` use LMF, right use UMF.

**Balance Enforcement (Proportional Normalization):**

```
T = (sum(supply_km) + sum(demand_km)) / 2

supply_final[i] = supply_km[i] / sum(supply_km) × T
demand_final[j] = demand_km[j] / sum(demand_km) × T
```

Properties:

1. `sum(supply_final) == sum(demand_final) == T` exactly.
2. Intra-supply ratios are preserved.
3. Intra-demand ratios are preserved.
4. Correction magnitude is tiny (~0.011% per element).
5. Fully deterministic.

### Architecture (6 Layers)

| Layer | Class                | Responsibility                                                       |
| ----- | -------------------- | -------------------------------------------------------------------- |
| 1     | `TrapezoidalMF`      | Evaluates trapezoidal membership function at sample points           |
| 2     | `KarnikMendelEngine` | Iterative KM centroid computation for IT2-TFS                        |
| 3     | `IT2FSParser`        | Validates fuzzified JSON structure (UMF/LMF keys, heights, nesting)  |
| 4     | `BalanceEnforcer`    | Enforces `sum(supply) == sum(demand)` via proportional normalization |
| 5     | `IT2TFSDefuzzifier`  | Main pipeline: KM defuzzification + balance enforcement              |
| 6     | `RecoveryAuditor`    | Computes recovery accuracy metrics (MAE, MAPE, RMSE, MaxAE)          |

### How to Implement / Run

**Step 1: Prepare your fuzzy input JSON file** (output from the fuzzifier, e.g., `my_fuzzy_data.json`).

**Step 2: Create a Python script** (e.g., `run_defuzzifier.py`):

```python
import json
from it2_defuzzifier import IT2TFSDefuzzifier

# Load fuzzy data (output from fuzzifier)
with open("my_fuzzy_data.json", "r") as f:
    fuzzy_data = json.load(f)

# Initialize defuzzifier
defuzzifier = IT2TFSDefuzzifier(
    N=1000,                # KM discretization resolution
    max_iter=100,          # max KM iterations per centroid
    tol=1e-8,              # convergence tolerance
    enforce_balance=True,  # apply proportional normalization
)

# Transform fuzzy data → crisp data
crisp_result = defuzzifier.transform(fuzzy_data)

# Export to JSON
defuzzifier.export(crisp_result, "my_crisp_recovered.json")

# Optional: print balance report
print("Balance report:", crisp_result["metadata"]["balance_report"])
```

**Step 3: Run the script:**

```bash
python run_defuzzifier.py
```

### Parameters

| Parameter         | Default | Description                                                                         |
| ----------------- | ------- | ----------------------------------------------------------------------------------- |
| `N`               | `1000`  | Number of discretization sample points for KM algorithm                             |
| `max_iter`        | `100`   | Maximum KM iterations per centroid computation                                      |
| `tol`             | `1e-8`  | Convergence tolerance for KM iteration                                              |
| `enforce_balance` | `True`  | If `True`, apply proportional normalization to enforce `sum(supply) == sum(demand)` |

### Input Format

The defuzzifier expects the JSON output produced by the fuzzifier:

```json
{
  "metadata": { ... },
  "cost_matrix": [
    [
      {"umf": [a1, a2, a3, a4, 1.0], "lmf": [b1, b2, b3, b4, hL]},
      ...
    ],
    ...
  ],
  "supply": [
    {"umf": [...], "lmf": [...]},
    ...
  ],
  "demand": [
    {"umf": [...], "lmf": [...]},
    ...
  ]
}
```

**Validation rules enforced:**

- Required keys: `cost_matrix`, `supply`, `demand`.
- Each IT2FS object must have `umf` (5 elements) and `lmf` (5 elements).
- UMF height must be `1.0`.
- LMF height must be in `(0, 1]`.
- Nesting constraint: `a1 ≤ b1 ≤ b2 ≤ b3 ≤ b4 ≤ a4`.

### Output Format

The output is a JSON object with crisp balanced values:

```json
{
  "metadata": {
    "method": "Karnik-Mendel Centroid + Proportional Balance",
    "km_resolution_N": 1000,
    "balance_enforced": true,
    "balance_report": {
      "method": "proportional_normalization",
      "T_supply_before": ...,
      "T_demand_before": ...,
      "imbalance_before": ...,
      "T_anchor": ...,
      "T_supply_after": ...,
      "T_demand_after": ...,
      "imbalance_after": ...,
      "supply_scale_factor": ...,
      "demand_scale_factor": ...
    },
    "source_delta": 0.15,
    "source_alpha": 0.45,
    "source_beta": 0.75,
    "source_gamma": 1.15,
    "source_statistics": { ... }
  },
  "cost_matrix": [[<float>, ...], ...],
  "supply": [<float>, ...],
  "demand": [<float>, ...]
}
```

**Guarantees:**

- `sum(supply) == sum(demand)` exactly (when `enforce_balance=True`).
- All values are rounded to 2 decimal places.

---

## End-to-End Workflow

```
Crisp JSON  ──[Fuzzifier]──►  Fuzzy JSON  ──[Defuzzifier]──►  Crisp JSON (recovered)
   │                              │                                  │
   └─ cost_matrix                  └─ IT2-TFS objects               └─ Balanced
   └─ supply                        (UMF + LMF per element)           cost_matrix
   └─ demand                                                          └─ supply
                                                                      └─ demand
```

**Complete pipeline script example:**

```python
import json
from it2_fuzzifier import IT2TFSFuzzifier
from it2_defuzzifier import IT2TFSDefuzzifier

# ── Step 1: Fuzzify ──────────────────────────────────────────────
with open("crisp_data/problem_60x60_crisp.json", "r") as f:
    crisp_data = json.load(f)

fuzzifier = IT2TFSFuzzifier(delta=0.15, alpha=0.45, beta=0.75, gamma=1.15)
fuzzy_data = fuzzifier.transform(crisp_data)
fuzzifier.export(fuzzy_data, "fuzzy_data/problem_60x60_fuzzy.json")

# ── Step 2: Defuzzify ────────────────────────────────────────────
defuzzifier = IT2TFSDefuzzifier(N=1000, enforce_balance=True)
recovered = defuzzifier.transform(fuzzy_data)
defuzzifier.export(recovered, "crisp_data/problem_60x60_crisp_recovered.json")

# ── Step 3: Audit recovery accuracy ──────────────────────────────
from it2_defuzzifier import RecoveryAuditor
report = RecoveryAuditor.audit(crisp_data, recovered)
print(json.dumps(report, indent=4))
```

---

## References

1. Mendel, J.M. (2001). _Uncertain Rule-Based Fuzzy Systems_. Prentice Hall.
2. Karnik, N.N. & Mendel, J.M. (2001). Centroid of a type-2 fuzzy set. _Information Sciences_, 132(1-4), 195–220.
3. John, R.I. & Coupland, S. (2007). Type-2 Fuzzy Logic: A Historical View. _IEEE Computational Intelligence Magazine_.
4. Wu, D. & Mendel, J.M. (2009). Enhanced Karnik-Mendel Algorithms. _IEEE Trans. Fuzzy Syst._, 17(4), 923–934.
5. Kumar, A., Kaur, P. & Singh, P. (2011). A new method for solving fully fuzzy linear programming problems. _Applied Mathematical Modelling_, 35(2), 817–823.
