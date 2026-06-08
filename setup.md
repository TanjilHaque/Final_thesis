# Setup Guide — Transportation Problem Solver with Fuzzy Logic & Sensitivity Analysis

This guide explains how to set up and run the complete transportation problem solver, including crisp algorithms, fuzzy logic fuzzification/defuzzification, and sensitivity analysis.

---

## 1. Prerequisites

- **Python 3.8+** (tested on Python 3.10+)
- **Git** (for cloning the repository)
- **pip** (Python package manager)

---

## 2. Clone the Repository

```bash
git clone https://github.com/<your-username>/<repository-name>.git
cd <repository-name>
```

---

## 3. Install Required Packages

```bash
pip install numpy pandas scipy matplotlib
```

| Package    | Purpose                                   |
| ---------- | ----------------------------------------- |
| numpy      | Numerical computations, matrix operations |
| pandas     | Data manipulation and tabular output      |
| scipy      | Scientific computing utilities            |
| matplotlib | Plotting and visualization                |

---

## 4. Project Structure

```
.
├── algorithms/
│   ├── modi.py          # Modified Distribution Method (optimization)
│   ├── russell.py       # Russell's Approximation Method (IBFS)
│   └── vogel.py         # Vogel's Approximation Method (IBFS)
├── comparisons/
│   ├── cost_comparison.py
│   └── time_comparision.py
├── crisp_data/          # Pre-generated crisp transportation datasets
├── data_generators/
│   ├── data_generator_1.py  # RAM-biased generator (200x200)
│   └── data_generator_2.py  # Parity generator (90x90)
├── fuzzy_data/
│   ├── it2_fuzzifier.py     # IT2-TFS Fuzzifier
│   └── it2_defuzzifier.py   # IT2-TFS Defuzzifier
├── sensitivity/
│   ├── cost_sensitivity.py  # Cost sensitivity analysis
│   └── FOU_sensitivity.py   # FOU (Footprint of Uncertainty) sensitivity
├── test_data/           # Small test datasets
└── setup.md             # This file
```

---

## 5. Generate Transportation Datasets

### Option A: Use pre-generated datasets

Pre-generated crisp datasets are available in the [`crisp_data/`](crisp_data) folder (e.g., `problem_60x60_crisp.json`, `problem_100x100_crisp.json`, etc.).

### Option B: Generate new datasets

```bash
# Generate RAM-biased 200x200 dataset
python data_generators/data_generator_1.py

# Generate parity 90x90 dataset
python data_generators/data_generator_2.py
```

---

## 6. Run Transportation Algorithms

### 6.1 Vogel's Approximation Method (VAM)

```bash
python algorithms/vogel.py
```

### 6.2 Russell's Approximation Method (RAM)

```bash
python algorithms/russell.py
```

### 6.3 Modified Distribution Method (MODI)

```bash
python algorithms/modi.py
```

---

## 7. Run Fuzzy Logic Pipeline

### 7.1 Fuzzification (Crisp → IT2-TFS)

Convert a crisp transportation problem into an Interval Type-2 Trapezoidal Fuzzy Set representation:

```bash
python fuzzy_data/it2_fuzzifier.py
```

**Input:** Crisp JSON file (e.g., `crisp_data/problem_60x60_crisp.json`)  
**Output:** Fuzzy JSON file with UMF/LMF trapezoidal representations

### 7.2 Defuzzification (IT2-TFS → Crisp)

Convert fuzzy data back to crisp values using Karnik-Mendel algorithm with balance enforcement:

```bash
python fuzzy_data/it2_defuzzifier.py
```

**Input:** Fuzzy JSON file (e.g., `fuzzy_data/fuzzy_test_data/problem_60x60_fuzzy.json`)  
**Output:** Recovered crisp JSON with balance report

---

## 8. Run Sensitivity Analysis

### 8.1 Cost Sensitivity Analysis

Perturb cost matrix values and analyze solution stability:

```bash
python sensitivity/cost_sensitivity.py fuzzy_data/fuzzy_test_data/problem_6x8_fuzzy.json data_for_sensitivity
```

### 8.2 FOU (Footprint of Uncertainty) Sensitivity

Expand or contract the FOU by modifying LMF trapezoidal points:

```bash
# Basic run
python sensitivity/FOU_sensitivity.py fuzzy_data/fuzzy_test_data/problem_3x4_fuzzy.json

# With diagnostic (recommended for new datasets)
python sensitivity/FOU_sensitivity.py fuzzy_data/fuzzy_test_data/problem_3x4_fuzzy.json --diagnose
```

**Output:** Four datasets in `fou_sensitivity_output/`:

- `F1_fou_minus_20.json` — FOU contracted by 20%
- `F2_fou_minus_10.json` — FOU contracted by 10%
- `F3_fou_plus_10.json` — FOU expanded by 10%
- `F4_fou_plus_20.json` — FOU expanded by 20%

---

## 9. Run Comparisons

### 9.1 Cost Comparison

```bash
python3 -m comparisons.cost_comparison
```

### 9.2 Time Comparison

```bash
python3 comparisons/time_comparision.py test_data/test_data_12.json
```

---

## 10. Reproduce Benchmark Results

All benchmark datasets are included in the repository:

| Dataset Folder                                              | Description                                      |
| ----------------------------------------------------------- | ------------------------------------------------ |
| [`crisp_data/`](crisp_data)                                 | Crisp transportation problems (60x60 to 200x200) |
| [`fuzzy_data/fuzzy_test_data/`](fuzzy_data/fuzzy_test_data) | IT2-TFS fuzzy datasets                           |
| [`data_for_sensitivity/`](data_for_sensitivity)             | Cost and FOU sensitivity datasets                |
| [`test_data/`](test_data)                                   | Small test cases                                 |

To reproduce results:

1. Load the desired dataset JSON file
2. Run the corresponding algorithm or analysis script
3. Compare outputs against the provided time/cost report files (e.g., `*_time_report.txt`)

---

## 11. Troubleshooting

| Issue                              | Solution                                                                                     |
| ---------------------------------- | -------------------------------------------------------------------------------------------- |
| `ModuleNotFoundError`              | Ensure you're running from the project root directory                                        |
| `FileNotFoundError` for JSON files | Check that the file path is correct relative to the project root                             |
| FOU clamping warnings              | Use `--diagnose` flag to inspect which cells are affected; reduce multiplier range if needed |
| Balance enforcement errors         | Ensure supply and demand sums are approximately equal before defuzzification                 |

---

## 12. Quick Start (All-in-One)

```bash
# 1. Clone and install
git clone https://github.com/<your-username>/<repository-name>.git
cd <repository-name>
pip install numpy pandas scipy matplotlib

# 2. Run VAM on a test dataset
python algorithms/vogel.py

# 3. Run Russell's method
python algorithms/russell.py

# 4. Optimize with MODI
python algorithms/modi.py

# 5. Fuzzify a crisp dataset
python fuzzy_data/it2_fuzzifier.py

# 6. Defuzzify with balance enforcement
python fuzzy_data/it2_defuzzifier.py

# 7. Run cost sensitivity
python sensitivity/cost_sensitivity.py fuzzy_data/fuzzy_test_data/problem_6x8_fuzzy.json data_for_sensitivity

# 8. Run FOU sensitivity with diagnostic
python sensitivity/FOU_sensitivity.py fuzzy_data/fuzzy_test_data/problem_3x4_fuzzy.json --diagnose

# 9. Compare costs
python3 -m comparisons.cost_comparison

# 10. Compare execution times
python3 comparisons/time_comparision.py test_data/test_data_12.json
```
