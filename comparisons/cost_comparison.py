"""
cost_comparison.py
==========================================================
Compares transportation costs between:

1. Russell's Approximation Method (RAM)
2. Vogel's Approximation Method (VAM)
3. RAM + MODI Optimization
4. VAM + MODI Optimization

The script:
------------
- Loads transportation problem data from:
      ../test_data/test_data_1.json

- Solves the same problem using:
      RAM
      VAM
      RAM + MODI
      VAM + MODI

- Displays:
      Initial IBFS costs
      Optimized MODI costs
      Percentage improvements

- Generates comparison-ready outputs
  suitable for thesis experiments.

Expected JSON format:
---------------------

{
    "cost_matrix": [
        [2, 3, 1],
        [5, 4, 8]
    ],
    "supply": [30, 40],
    "demand": [20, 25, 25]
}
"""

import json
import numpy as np

from algorithms.russell import RussellsApproximationMethod
from algorithms.vogel import VogelsApproximationMethod
from algorithms.modi import MODI


# =========================================================
# LOAD JSON DATA
# =========================================================

def load_problem(file_path: str):

    with open(file_path, "r") as file:
        data = json.load(file)

    cost_matrix = np.array(
        data["cost_matrix"],
        dtype=float
    )

    supply = np.array(
        data["supply"],
        dtype=float
    )

    demand = np.array(
        data["demand"],
        dtype=float
    )

    return cost_matrix, supply, demand


# =========================================================
# RAM PIPELINE
# =========================================================

def run_ram_pipeline(
    cost_matrix,
    supply,
    demand
):

    # -----------------------------
    # RAM Initial Solution
    # -----------------------------

    ram = RussellsApproximationMethod(
        cost_matrix,
        supply,
        demand
    )

    ram_allocations = ram.solve()

    ram_initial_cost = ram.initial_cost

    # -----------------------------
    # MODI Optimization
    # -----------------------------

    ram_modi = MODI(
        cost_matrix,
        ram_allocations
    )

    ram_modi.solve()

    ram_optimized_cost = (
        ram_modi.calculate_total_cost()
    )

    return {
        "method": "RAM",
        "initial_cost": ram_initial_cost,
        "optimized_cost": ram_optimized_cost,
        "improvement": (
            ram_initial_cost
            - ram_optimized_cost
        ),
        "improvement_percentage": (
            (
                (
                    ram_initial_cost
                    - ram_optimized_cost
                )
                / ram_initial_cost
            ) * 100
            if ram_initial_cost != 0
            else 0
        ),
        "initial_iterations": ram.iterations,
        "modi_iterations": ram_modi.iterations,
        "initial_time": ram.execution_time,
    }


# =========================================================
# VAM PIPELINE
# =========================================================

def run_vam_pipeline(
    cost_matrix,
    supply,
    demand
):

    # -----------------------------
    # VAM Initial Solution
    # -----------------------------

    vam = VogelsApproximationMethod(
        cost_matrix,
        supply,
        demand
    )

    vam_allocations = vam.solve()

    vam_initial_cost = vam.initial_cost

    # -----------------------------
    # MODI Optimization
    # -----------------------------

    vam_modi = MODI(
        cost_matrix,
        vam_allocations
    )

    vam_modi.solve()

    vam_optimized_cost = (
        vam_modi.calculate_total_cost()
    )

    return {
        "method": "VAM",
        "initial_cost": vam_initial_cost,
        "optimized_cost": vam_optimized_cost,
        "improvement": (
            vam_initial_cost
            - vam_optimized_cost
        ),
        "improvement_percentage": (
            (
                (
                    vam_initial_cost
                    - vam_optimized_cost
                )
                / vam_initial_cost
            ) * 100
            if vam_initial_cost != 0
            else 0
        ),
        "initial_iterations": vam.iterations,
        "modi_iterations": vam_modi.iterations,
        "initial_time": vam.execution_time,
    }


# =========================================================
# DISPLAY RESULTS
# =========================================================

def print_comparison(
    ram_results,
    vam_results
):

    print("\n" + "=" * 70)
    print("        TRANSPORTATION COST COMPARISON")
    print("=" * 70)

    # -----------------------------------------------------
    # RAM
    # -----------------------------------------------------

    print("\n[RUSSELL'S APPROXIMATION METHOD]")

    print(
        f"Initial IBFS Cost        : "
        f"{ram_results['initial_cost']:.4f}"
    )

    print(
        f"Optimized MODI Cost      : "
        f"{ram_results['optimized_cost']:.4f}"
    )

    print(
        f"Cost Improvement         : "
        f"{ram_results['improvement']:.4f}"
    )

    print(
        f"Improvement Percentage   : "
        f"{ram_results['improvement_percentage']:.2f}%"
    )

    print(
        f"RAM Iterations           : "
        f"{ram_results['initial_iterations']}"
    )

    print(
        f"MODI Iterations          : "
        f"{ram_results['modi_iterations']}"
    )

    print(
        f"RAM Execution Time       : "
        f"{ram_results['initial_time']:.6f} seconds"
    )

    # -----------------------------------------------------
    # VAM
    # -----------------------------------------------------

    print("\n[VOGEL'S APPROXIMATION METHOD]")

    print(
        f"Initial IBFS Cost        : "
        f"{vam_results['initial_cost']:.4f}"
    )

    print(
        f"Optimized MODI Cost      : "
        f"{vam_results['optimized_cost']:.4f}"
    )

    print(
        f"Cost Improvement         : "
        f"{vam_results['improvement']:.4f}"
    )

    print(
        f"Improvement Percentage   : "
        f"{vam_results['improvement_percentage']:.2f}%"
    )

    print(
        f"VAM Iterations           : "
        f"{vam_results['initial_iterations']}"
    )

    print(
        f"MODI Iterations          : "
        f"{vam_results['modi_iterations']}"
    )

    print(
        f"VAM Execution Time       : "
        f"{vam_results['initial_time']:.6f} seconds"
    )

    # -----------------------------------------------------
    # FINAL COMPARISON
    # -----------------------------------------------------

    print("\n" + "-" * 70)

    if (
        ram_results["optimized_cost"]
        < vam_results["optimized_cost"]
    ):

        print(
            "RAM + MODI produced "
            "the lower final transportation cost."
        )

    elif (
        vam_results["optimized_cost"]
        < ram_results["optimized_cost"]
    ):

        print(
            "VAM + MODI produced "
            "the lower final transportation cost."
        )

    else:

        print(
            "Both methods produced "
            "the same final transportation cost."
        )

    print("=" * 70 + "\n")


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    # -----------------------------------------------------
    # Load Test Problem
    # -----------------------------------------------------

    #FILE_PATH = "data_for_sensitivity/problem_40x60_fou_sensitive/p_40x60_fou_plus_10_crisp.json"
    FILE_PATH = "crisp_data/problem_3x4_crisp.json"

    cost_matrix, supply, demand = load_problem(
        FILE_PATH
    )

    # -----------------------------------------------------
    # Run RAM Pipeline
    # -----------------------------------------------------

    ram_results = run_ram_pipeline(
        cost_matrix,
        supply,
        demand
    )

    # -----------------------------------------------------
    # Run VAM Pipeline
    # -----------------------------------------------------

    vam_results = run_vam_pipeline(
        cost_matrix,
        supply,
        demand
    )

    # -----------------------------------------------------
    # Print Comparison
    # -----------------------------------------------------

    print_comparison(
        ram_results,
        vam_results
    )