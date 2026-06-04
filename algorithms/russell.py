import numpy as np
import time
from typing import List, Tuple, Dict, Any


class RussellsApproximationMethod:
    """
    Russell's Approximation Method (RAM)

    Generates an Initial Basic Feasible Solution (IBFS)
    for a balanced transportation problem.

    Features:
    ----------
    - Non-destructive implementation
    - Modular architecture
    - Large-scale compatible
    - Comparison-ready
    - MODI-compatible allocation format
    - Timing compatible
    - Sensitivity-analysis ready
    - Future fuzzy-extension ready
    """

    def __init__(
        self,
        cost_matrix: np.ndarray,
        supply: np.ndarray,
        demand: np.ndarray
    ):

        self.cost_matrix = np.array(cost_matrix, dtype=float)
        self.supply = np.array(supply, dtype=float)
        self.demand = np.array(demand, dtype=float)

        # Validation
        self._validate_inputs()

        # Preserve originals
        self.original_cost = self.cost_matrix.copy()
        self.original_supply = self.supply.copy()
        self.original_demand = self.demand.copy()

        # Problem size
        self.rows, self.cols = self.cost_matrix.shape

        # Allocation matrix
        self.allocation_matrix = np.zeros((self.rows, self.cols))

        # Allocation list format:
        # [(row, col, quantity), ...]
        self.allocations: List[Tuple[int, int, float]] = []

        # Metrics
        self.iterations = 0
        self.execution_time = 0.0
        self.initial_cost = 0.0

    # =========================================================
    # VALIDATION
    # =========================================================

    def _validate_inputs(self):

        if self.cost_matrix.ndim != 2:
            raise ValueError("Cost matrix must be 2-dimensional.")

        if len(self.supply) != self.cost_matrix.shape[0]:
            raise ValueError(
                "Supply length must match number of rows."
            )

        if len(self.demand) != self.cost_matrix.shape[1]:
            raise ValueError(
                "Demand length must match number of columns."
            )

        if not np.isclose(
            np.sum(self.supply),
            np.sum(self.demand)
        ):
            raise ValueError(
                "Transportation problem must be balanced."
            )

    # =========================================================
    # MAIN SOLVER
    # =========================================================

    def solve(self) -> List[Tuple[int, int, float]]:

        start_time = time.perf_counter()

        # Working copies
        supply = self.supply.copy()
        demand = self.demand.copy()

        # Active rows/columns
        active_rows = set(range(self.rows))
        active_cols = set(range(self.cols))

        while active_rows and active_cols:

            self.iterations += 1

            # -------------------------------------------------
            # STEP 1: Compute Ui
            # Largest cost in each active row
            # -------------------------------------------------

            U = {}

            for i in active_rows:
                row_costs = [
                    self.cost_matrix[i][j]
                    for j in active_cols
                ]
                U[i] = max(row_costs)

            # -------------------------------------------------
            # STEP 2: Compute Vj
            # Largest cost in each active column
            # -------------------------------------------------

            V = {}

            for j in active_cols:
                col_costs = [
                    self.cost_matrix[i][j]
                    for i in active_rows
                ]
                V[j] = max(col_costs)

            # -------------------------------------------------
            # STEP 3:
            # Compute reduced costs:
            #
            # Δij = Cij - (Ui + Vj)
            # -------------------------------------------------

            min_delta = float("inf")
            selected_cell = None

            for i in active_rows:
                for j in active_cols:

                    delta = (
                        self.cost_matrix[i][j]
                        - (U[i] + V[j])
                    )

                    # Most negative delta
                    if delta < min_delta:
                        min_delta = delta
                        selected_cell = (i, j)

            # -------------------------------------------------
            # STEP 4:
            # Allocate maximum possible
            # -------------------------------------------------

            i, j = selected_cell

            allocation = min(supply[i], demand[j])

            self.allocation_matrix[i][j] = allocation

            self.allocations.append(
                (i, j, allocation)
            )

            supply[i] -= allocation
            demand[j] -= allocation

            # -------------------------------------------------
            # STEP 5:
            # Remove exhausted row/column
            # -------------------------------------------------

            if np.isclose(supply[i], 0):
                active_rows.remove(i)

            if np.isclose(demand[j], 0):
                active_cols.remove(j)

        self.execution_time = (
            time.perf_counter() - start_time
        )

        self.initial_cost = self.calculate_total_cost()

        return self.allocations

    # =========================================================
    # COST CALCULATION
    # =========================================================

    def calculate_total_cost(self) -> float:

        total_cost = 0.0

        for i, j, quantity in self.allocations:

            total_cost += (
                self.original_cost[i][j] * quantity
            )

        return total_cost

    # =========================================================
    # RESULTS
    # =========================================================

    def get_results(self) -> Dict[str, Any]:

        return {
            "method": "Russells Approximation Method",
            "allocations": self.allocations,
            "allocation_matrix": self.allocation_matrix,
            "initial_cost": self.initial_cost,
            "iterations": self.iterations,
            "execution_time": self.execution_time,
        }

    # =========================================================
    # DISPLAY
    # =========================================================

    def print_results(self):

        print("\n========== RAM RESULTS ==========")

        print("\nAllocations:")
        for i, j, q in self.allocations:
            print(
                f"Cell ({i}, {j}) --> Allocation = {q}"
            )

        print(
            f"\nInitial Transportation Cost: "
            f"{self.initial_cost}"
        )

        print(f"Iterations: {self.iterations}")

        print(
            f"Execution Time: "
            f"{self.execution_time:.6f} seconds"
        )

        print("=================================\n")


# =============================================================
# STANDALONE TEST
# =============================================================

if __name__ == "__main__":

    # Example balanced transportation problem

    cost = np.array([
        [2.32, 5.19, 7.25, 6.5],
    [2.13, 5.19, 8.12, 2.13],
    [2.32, 6.5, 9.3, 2.13]
    ])

    supply = np.array([5.41, 8.01, 2.59])

    demand = np.array([2.19, 2.19, 5.13, 6.5])

    ram = RussellsApproximationMethod(
        cost,
        supply,
        demand
    )

    allocations = ram.solve()

    ram.print_results()