import numpy as np
import time
from typing import List, Tuple, Dict, Any


class VogelsApproximationMethod:
    """
    Vogel's Approximation Method (VAM)

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
    # PENALTY CALCULATIONS
    # =========================================================

    def _calculate_row_penalty(
        self,
        row_index: int,
        active_cols: set
    ) -> float:

        costs = sorted([
            self.cost_matrix[row_index][j]
            for j in active_cols
        ])

        if len(costs) == 1:
            return costs[0]

        return costs[1] - costs[0]

    def _calculate_col_penalty(
        self,
        col_index: int,
        active_rows: set
    ) -> float:

        costs = sorted([
            self.cost_matrix[i][col_index]
            for i in active_rows
        ])

        if len(costs) == 1:
            return costs[0]

        return costs[1] - costs[0]

    # =========================================================
    # FIND LOWEST COST CELL
    # =========================================================

    def _find_lowest_cost_in_row(
        self,
        row_index: int,
        active_cols: set
    ) -> Tuple[int, float]:

        min_cost = float("inf")
        selected_col = None

        for j in active_cols:

            cost = self.cost_matrix[row_index][j]

            if cost < min_cost:
                min_cost = cost
                selected_col = j

        return selected_col, min_cost

    def _find_lowest_cost_in_col(
        self,
        col_index: int,
        active_rows: set
    ) -> Tuple[int, float]:

        min_cost = float("inf")
        selected_row = None

        for i in active_rows:

            cost = self.cost_matrix[i][col_index]

            if cost < min_cost:
                min_cost = cost
                selected_row = i

        return selected_row, min_cost

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
            # STEP 1:
            # Calculate row penalties
            # -------------------------------------------------

            row_penalties = {}

            for i in active_rows:
                row_penalties[i] = (
                    self._calculate_row_penalty(
                        i,
                        active_cols
                    )
                )

            # -------------------------------------------------
            # STEP 2:
            # Calculate column penalties
            # -------------------------------------------------

            col_penalties = {}

            for j in active_cols:
                col_penalties[j] = (
                    self._calculate_col_penalty(
                        j,
                        active_rows
                    )
                )

            # -------------------------------------------------
            # STEP 3:
            # Find maximum penalty
            # -------------------------------------------------

            max_row_penalty = max(
                row_penalties.values()
            )

            max_col_penalty = max(
                col_penalties.values()
            )

            # -------------------------------------------------
            # STEP 4:
            # Select row or column
            # -------------------------------------------------

            if max_row_penalty >= max_col_penalty:

                # Select row with maximum penalty
                selected_row = max(
                    row_penalties,
                    key=row_penalties.get
                )

                # Find minimum cost cell in row
                selected_col, _ = (
                    self._find_lowest_cost_in_row(
                        selected_row,
                        active_cols
                    )
                )

            else:

                # Select column with maximum penalty
                selected_col = max(
                    col_penalties,
                    key=col_penalties.get
                )

                # Find minimum cost cell in column
                selected_row, _ = (
                    self._find_lowest_cost_in_col(
                        selected_col,
                        active_rows
                    )
                )

            # -------------------------------------------------
            # STEP 5:
            # Allocate maximum possible
            # -------------------------------------------------

            allocation = min(
                supply[selected_row],
                demand[selected_col]
            )

            self.allocation_matrix[
                selected_row
            ][selected_col] = allocation

            self.allocations.append(
                (
                    selected_row,
                    selected_col,
                    allocation
                )
            )

            supply[selected_row] -= allocation
            demand[selected_col] -= allocation

            # -------------------------------------------------
            # STEP 6:
            # Remove exhausted row/column
            # -------------------------------------------------

            if np.isclose(
                supply[selected_row],
                0
            ):
                active_rows.remove(selected_row)

            if np.isclose(
                demand[selected_col],
                0
            ):
                active_cols.remove(selected_col)

        self.execution_time = (
            time.perf_counter() - start_time
        )

        self.initial_cost = (
            self.calculate_total_cost()
        )

        return self.allocations

    # =========================================================
    # COST CALCULATION
    # =========================================================

    def calculate_total_cost(self) -> float:

        total_cost = 0.0

        for i, j, quantity in self.allocations:

            total_cost += (
                self.original_cost[i][j]
                * quantity
            )

        return total_cost

    # =========================================================
    # RESULTS
    # =========================================================

    def get_results(self) -> Dict[str, Any]:

        return {
            "method": "Vogels Approximation Method",
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

        print("\n========== VAM RESULTS ==========")

        print("\nAllocations:")

        for i, j, q in self.allocations:

            print(
                f"Cell ({i}, {j}) --> "
                f"Allocation = {q}"
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

    vam = VogelsApproximationMethod(
        cost,
        supply,
        demand
    )

    allocations = vam.solve()

    vam.print_results()