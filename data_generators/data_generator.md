# Data Generator Insights

## Overview

Two data generators for transportation problem instances with different structural biases.

---

## data_generator_1.py - RAM-Biased Generator

**Purpose:** Generates 200x200 transportation problems designed to favor the RAM (Russell's Approximation Method) algorithm.

### Key Characteristics:

- **Size:** 200x200 (m=n=200)
- **Structure:** `deterministic_RAM_biased`
- **Expected RAM Advantage:** >=5%

### Generation Strategy:

1. **Cost Matrix Structure:**
   - Base costs: uniform range [25, 40]
   - Each row has ONE globally strong candidate (permuted diagonal) with cost [1.0, 4.0]
   - Second-best costs deliberately set to [10.0, 14.0] to weaken VAM penalty signals

2. **Column Clustering:**
   - 10 cluster centers in range [5, 12]
   - Columns grouped into 10 clusters, each with mild cost reinforcement
   - Creates soft column structure important for RAM advantage

3. **Supply/Demand:**
   - Supply: uniform [50, 120]
   - Demand: uniform [40, 110], balanced to match total supply
   - Rounding drift corrected on last demand value

---

## data_generator_2.py - Parity Generator

**Purpose:** Generates 90x90 transportation problems where VAM and Russell's Approximation produce near-identical costs.

### Key Characteristics:

- **Size:** 90x90 (m=n=90)
- **Structure:** `flat_diffuse_parity`
- **Design:** Low penalty variance → VAM and Russell converge

### Generation Strategy:

1. **Cost Matrix Structure:**
   - Flat uniform cost field: base [15, 38] with small noise [-3.0, 3.0]
   - Creates diffuse cost landscape with small penalty variance
   - VAM's sharp-penalty advantage is eliminated

2. **Supply/Demand:**
   - Supply: uniform [40, 100]
   - Demand: uniform [30, 90], balanced to match total supply
   - Rounding drift corrected on last demand value

---

## Comparison Summary

| Aspect        | Generator 1                                 | Generator 2                        |
| ------------- | ------------------------------------------- | ---------------------------------- |
| Size          | 200x200                                     | 90x90                              |
| Structure     | RAM-favoring (strong diagonal + clustering) | Parity (flat, diffuse)             |
| VAM Advantage | Weakened (second-best costs raised)         | Eliminated (low penalty variance)  |
| Use Case      | Benchmark RAM performance                   | Compare VAM vs Russell equivalence |
