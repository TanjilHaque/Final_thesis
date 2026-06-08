# Final_Thesis_Codes

A comprehensive research repository for **transportation problem algorithms**, **Interval Type-2 Fuzzy Logic systems**, and **sensitivity analysis** — designed for thesis-level computational experiments and benchmarking.

---

## Table of Contents

1. [Overview](#overview)
2. [Repository Structure](#repository-structure)
3. [Core Algorithms](#core-algorithms)
4. [Fuzzy Logic System](#fuzzy-logic-system)
5. [Data Generators](#data-generators)
6. [Comparisons & Benchmarking](#comparisons--benchmarking)
7. [Sensitivity Analysis](#sensitivity-analysis)
8. [Installation & Requirements](#installation--requirements)
9. [Usage Guide](#usage-guide)
10. [Data Formats](#data-formats)
11. [Research Context](#research-context)

---

## Overview

This repository implements and benchmarks transportation problem solvers at multiple levels of complexity:

- **Crisp transportation problems** — classical operations research
- **Interval Type-2 Trapezoidal Fuzzy Transportation Problems (IT2-TrFTP)** — advanced fuzzy logic extension
- **Sensitivity analysis** — cost magnitude and FOU (Footprint of Uncertainty) perturbations
- **Algorithm comparison** — statistical benchmarking of IBFS methods

The codebase is designed for **reproducible research**, with structured data generators, comprehensive timing benchmarks, and modular algorithm implementations.

---

## Repository Structure

```
Final_Thesis_Codes/
├── algorithms/                    # Core transportation algorithms
│   ├── modi.py                    # Modified Distribution Method (optimization)
│   ├── russell.py                 # Russell's Approximation Method (IBFS)
│   └── vogel.py                   # Vogel's Approximation Method (IBFS)
│
├── comparisons/                   # Algorithm comparison tools
│   ├── cost_comparison.py         # Cost comparison: RAM vs VAM vs MODI
│   ├── time_comparision.py        # Statistical timing benchmarks
│   └── instruction.txt            # Quick usage commands
│
├── data_generators/               # Synthetic problem generators
│   ├── data_generator_1.py        # RAM-biased 200×200 problems
│   ├── data_generator_2.py        # Parity 90×90 problems (VAM ≈ RAM)
│   └── data_generator.md          # Generator documentation
│
├── sensitivity/                   # Sensitivity analysis tools
│   ├── cost_sensitivity.py        # Cost magnitude perturbations (±10%, ±20%)
│   ├── FOU_sensitivity.py         # FOU expansion/contraction (±10%, ±20%)
│   └── command.txt                # Quick usage commands
│
├── fuzzy_data/                    # IT2-TFS fuzzy logic system
│   ├── it2_fuzzifier.py           # Crisp → IT2-TFS conversion (9-layer architecture)
│   ├── it2_defuzzifier.py         # IT2-TFS → Crisp conversion (KM + balance enforcement)
│   ├── fuzzy_instruction.md       # Comprehensive theoretical guide
│   └── fuzzy_test_data/           # Pre-generated fuzzy test problems
│
├── crisp_data/                    # Crisp transportation problems
│   ├── problem_*x*_crisp.json     # Problem instances (3×4 to 200×200)
│   └── problem_*x*_crisp_time_report.txt  # Timing reports
│
├── data_for_sensitivity/          # Sensitivity analysis datasets
│   └── problem_*x*_*_sensitive/   # Perturbed problem instances
│
├── test_data/                     # Small test problems
│   └── test_data_*.json           # Various sizes for quick testing
│
├── table_maker.html               # HTML table generator for results
├── findings.md                    # Research findings & insights
└── readme.md                      # This file
```

---

## Core Algorithms

### 1. Russell's Approximation Method (RAM)

**File:** [`algorithms/russell.py`](algorithms/russell.py)

Generates an Initial Basic Feasible Solution (IBFS) for balanced transportation problems.

**Key Features:**

- Non-destructive implementation
- Modular architecture
- Large-scale compatible (tested up to 200×200)
- MODI-compatible allocation format
- Sensitivity-analysis ready

**How it works:**

1. Compute row and column maximum costs
2. For each cell, calculate penalty = row_max + col_max - 2×cost_ij
3. Select cell with maximum penalty
4. Allocate min(supply, demand)
5. Repeat until all supplies/demands are exhausted

---

### 2. Vogel's Approximation Method (VAM)

**File:** [`algorithms/vogel.py`](algorithms/vogel.py)

Generates an IBFS using penalty-based allocation.

**Key Features:**

- Non-destructive implementation
- Modular architecture
- Large-scale compatible
- MODI-compatible allocation format
- Sensitivity-analysis ready

**How it works:**

1. Compute row and column penalties (difference between two smallest costs)
2. Select row/column with highest penalty
3. Allocate to the cell with minimum cost in that row/column
4. Adjust supply/demand, eliminate exhausted rows/columns
5. Repeat until all allocations complete

---

### 3. Modified Distribution Method (MODI)

**File:** [`algorithms/modi.py`](algorithms/modi.py)

Optimizes an existing BFS to find the optimal solution.

**Key Features:**

- Research/thesis-grade implementation
- Structural degeneracy handling (no ε injection)
- BFS-based potential computation
- Provably-correct cycle construction via backtracking

**How it works:**

1. Compute potentials u_i, v_j such that u_i + v_j = c_ij for all basic cells
2. Compute reduced costs Δ_ij = c_ij - (u_i + v_j) for non-basic cells
3. If all Δ_ij ≥ 0 → current BFS is optimal
4. Otherwise, select entering variable with minimum reduced cost
5. Find unique closed loop through entering cell
6. Pivot: add θ\* = min allocation on '−' positions
7. Repeat until optimal

---

## Fuzzy Logic System

### IT2-TFS Fuzzifier

**File:** [`fuzzy_data/it2_fuzzifier.py`](fuzzy_data/it2_fuzzifier.py)

Converts crisp transportation problems into **Interval Type-2 Trapezoidal Fuzzy Set (IT2-TFS)** representation.

**Architecture (9 Layers):**

| Layer | Class                 | Responsibility                                          |
| ----- | --------------------- | ------------------------------------------------------- |
| 1     | `InputValidator`      | Validates JSON structure                                |
| 2     | `StatisticsEngine`    | Computes global & local statistics                      |
| 3     | `VariabilityEngine`   | Computes normalized variability scores v ∈ [0, 1]       |
| 4     | `ReliabilityEngine`   | Computes reliability scores r ∈ [0.3, 0.9]              |
| 5     | `UMFBuilder`          | Builds UMF trapezoid coordinates [a1, a2, a3, a4]       |
| 6     | `LMFBuilder`          | Builds LMF trapezoid coordinates [b1, b2, b3, b4]       |
| 7     | `HeightEngine`        | Computes LMF height hL ∈ [h_min, h_max]                 |
| 8     | `StructuralValidator` | Enforces nesting constraint a1 ≤ b1 ≤ b2 ≤ b3 ≤ b4 ≤ a4 |
| 9     | `OutputSerializer`    | Converts arrays to JSON-serializable IT2FS objects      |

**Three Strictly Separated Uncertainty Dimensions:**

- **A. Geometric Uncertainty** → UMF only (δ, α, β, γ)
- **B. Epistemic Uncertainty** → LMF only (reliability r)
- **C. Confidence** → LMF height hL only (variability v)

---

### IT2-TFS Defuzzifier

**File:** [`fuzzy_data/it2_defuzzifier.py`](fuzzy_data/it2_defuzzifier.py)

Converts IT2-TFS objects back to crisp numbers using the **Karnik-Mendel (KM) algorithm** with balance enforcement.

**Key Innovation: Balance Enforcement**

The fuzzifier assigns different reliability r and variability v to supply vs demand elements, causing non-uniform KM upward bias:

- Supply bias: ~1.32-1.37% per element
- Demand bias: ~1.24-1.36% per element

**Solution:** After KM defuzzification, enforce balance by proportional normalization to preserve relative proportions while ensuring exact balance.

---

## Data Generators

### Generator 1: RAM-Biased (200×200)

**File:** [`data_generators/data_generator_1.py`](data_generators/data_generator_1.py)

Generates 200×200 transportation problems designed to favor RAM.

**Strategy:**

- Base costs: uniform range [25, 40]
- Each row has ONE globally strong candidate (permuted diagonal) with cost [1.0, 4.0]
- Second-best costs deliberately set to [10.0, 14.0] to weaken VAM penalty signals
- 10 column clusters with mild cost reinforcement
- Expected RAM advantage: >=5%

---

### Generator 2: Parity Generator (90×90)

**File:** [`data_generators/data_generator_2.py`](data_generators/data_generator_2.py)

Generates 90×90 problems where VAM and Russell produce near-identical costs.

**Strategy:**

- Flat uniform cost field: base [15, 38] with small noise [-3.0, 3.0]
- Creates diffuse cost landscape with low penalty variance
- VAM's sharp-penalty advantage is eliminated
- Both methods converge to similar total costs

---

## Comparisons & Benchmarking

### Cost Comparison

**File:** [`comparisons/cost_comparison.py`](comparisons/cost_comparison.py)

Compares transportation costs between:

1. Russell's Approximation Method (RAM)
2. Vogel's Approximation Method (VAM)
3. RAM + MODI Optimization
4. VAM + MODI Optimization

**Output:** Initial IBFS costs, optimized MODI costs, percentage improvements

**Usage:**

```bash
python3 -m comparisons.cost_comparison
```

---

### Time Comparison

**File:** [`comparisons/time_comparision.py`](comparisons/time_comparision.py)

Statistical timing benchmark with rigorous methodology.

**Features:**

- N_RUNS iterations (default 30) per method
- Clock taken tightly around solver call only
- Reported statistics: mean, std, variance, min, max, 95% CI (t-distribution), CV

**Usage:**

```bash
python3 comparisons/time_comparision.py path/to/problem.json
```

---

## Sensitivity Analysis

### Cost Magnitude Sensitivity

**File:** [`sensitivity/cost_sensitivity.py`](sensitivity/cost_sensitivity.py)

Systematically perturbs ONLY the trapezoidal numeric points of the cost matrix in fuzzy transportation datasets.

**Perturbation Levels:**

- −20% (multiplier 0.80)
- −10% (multiplier 0.90)
- +10% (multiplier 1.10)
- +20% (multiplier 1.20)

**Preserved:** Supply, demand, metadata, and all height values (h_u, h_l)

**Usage:**

```bash
python3 sensitivity/cost_sensitivity.py fuzzy_data/fuzzy_test_data/problem_6x8_fuzzy.json data_for_sensitivity
```

---

### FOU (Footprint of Uncertainty) Sensitivity

**File:** [`sensitivity/FOU_sensitivity.py`](sensitivity/FOU_sensitivity.py)

Expands or contracts the Footprint of Uncertainty by modifying ONLY the LMF trapezoidal points.

**Perturbation Levels:**

- FOU −20% (multiplier 0.80×)
- FOU −10% (multiplier 0.90×)
- FOU +10% (multiplier 1.10×)
- FOU +20% (multiplier 1.20×)

**Preserved:** UMF values, LMF height (alpha), supply, demand, metadata

**Usage:**

```bash
python3 sensitivity/FOU_sensitivity.py fuzzy_data/fuzzy_test_data/problem_3x4_fuzzy.json
```

---

## Installation & Requirements

### Dependencies

- Python 3.8+
- numpy
- json (standard library)
- math (standard library)
- time (standard library)
- pathlib (standard library)

### Setup

```bash
# Clone or download the repository
cd Final_Thesis_Codes

# No additional installation required — all dependencies are standard library + numpy
# Install numpy if not already available:
pip install numpy
```

---

## Usage Guide

### Running Algorithms

**RAM (Russell's Approximation):**

```python
from algorithms.russell import RussellsApproximationMethod
import numpy as np

cost = np.array([[2, 3, 1], [5, 4, 8]])
supply = np.array([30, 40])
demand = np.array([20, 25, 25])

ram = RussellsApproximationMethod(cost, supply, demand)
result = ram.solve()
print(result['total_cost'])
```

**VAM (Vogel's Approximation):**

```python
from algorithms.vogel import VogelsApproximationMethod
import numpy as np

vam = VogelsApproximationMethod(cost, supply, demand)
result = vam.solve()
print(result['total_cost'])
```

**MODI Optimization:**

```python
from algorithms.modi import MODI

modi = MODI(cost, supply, demand, initial_allocation)
result = modi.optimize()
print(result['total_cost'])
```

---

### Running Fuzzy Operations

**Fuzzification (Crisp → Fuzzy):**

```python
import json
from fuzzy_data.it2_fuzzifier import IT2TFSFuzzifier

with open("crisp_data.json", "r") as f:
    data = json.load(f)

fuzzifier = IT2TFSFuzzifier(
    delta=0.15,
    alpha=0.45,
    beta=0.75,
    gamma=1.15,
    h_min=0.40,
    h_max=0.95,
)

result = fuzzifier.transform(data)
fuzzifier.export(result, "fuzzy_data.json")
```

**Defuzzification (Fuzzy → Crisp):**

```python
import json
from fuzzy_data.it2_defuzzifier import IT2TFSDefuzzifier

with open("fuzzy_data.json", "r") as f:
    fuzzy_data = json.load(f)

defuzzifier = IT2TFSDefuzzifier(
    n_samples=1000,
    h_min=0.40,
    h_max=0.95,
)

result = defuzzifier.defuzzify(fuzzy_data)
print(result['defuzzified_cost_matrix'])
```

---

### Generating Test Data

**RAM-Biased Problem:**

```python
from data_generators.data_generator_1 import generate_200x200

problem = generate_200x200(seed=42)
# Save to JSON
import json
with open("ram_biased_200x200.json", "w") as f:
    json.dump(problem, f, indent=2)
```

**Parity Problem:**

```python
from data_generators.data_generator_2 import generate_parity_problem

problem = generate_parity_problem(seed=42)
with open("parity_90x90.json", "w") as f:
    json.dump(problem, f, indent=2)
```

---

## Data Formats

### Crisp Transportation Problem (JSON)

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

### IT2-TFS Fuzzy Transportation Problem (JSON)

```json
{
  "metadata": {
    "description": "IT2-TFS transportation problem",
    "m": 2,
    "n": 3,
    "parameters": {
      "delta": 0.15,
      "alpha": 0.45,
      "beta": 0.75,
      "gamma": 1.15,
      "h_min": 0.40,
      "h_max": 0.95
    }
  },
  "cost_matrix": [
    [
      {
        "umf": [1.97, 2.15, 2.49, 2.66, 1.0],
        "lmf": [2.05, 2.22, 2.42, 2.59, 0.85]
      },
      ...
    ],
    ...
  ],
  "supply": [
    {"umf": [4.60, 4.83, 5.99, 6.22, 1.0], "lmf": [4.72, 4.95, 5.87, 6.10, 0.78]},
    ...
  ],
  "demand": [
    {"umf": [1.86, 1.97, 2.41, 2.52, 1.0], "lmf": [1.91, 2.02, 2.36, 2.47, 0.82]},
    ...
  ]
}
```

---

## Research Context

This repository supports research in:

1. **Transportation Problem Algorithms** — Comparing IBFS methods (RAM, VAM) and optimization (MODI)
2. **Fuzzy Optimization** — Extending crisp problems to Interval Type-2 Fuzzy sets
3. **Sensitivity Analysis** — Understanding how cost and uncertainty variations affect solutions
4. **Algorithmic Benchmarking** — Statistical timing and cost comparisons at scale

### Key Research Questions Addressed

- Do RAM and VAM produce different total costs? Under what conditions?
- How does MODI optimization affect different IBFS methods?
- What is the impact of fuzzy uncertainty on transportation problem solutions?
- How sensitive are solutions to cost magnitude changes vs FOU expansion?
- Can we generate controlled problem instances that favor specific algorithms?

### Notable Findings

See [`findings.md`](findings.md) for detailed research findings including:

- Mathematical proof that IBFS iteration counts are invariant (m+n−1)
- Three-dimensional uncertainty model for IT2-TFS
- Balance enforcement algorithm for defuzzified problems
- Scalability results up to 200×200 problems

---

## Contributing

This is a thesis/research codebase. For questions or collaborations, please refer to the documentation in each module's docstrings and the comprehensive guide in [`fuzzy_data/fuzzy_instruction.md`](fuzzy_data/fuzzy_instruction.md).

---

## License

Academic use for thesis and research purposes.

---

**Last Updated:** 2026-06-08
