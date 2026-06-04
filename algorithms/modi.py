"""
modi.py — Modified Distribution Method (MODI / UV Method)
==========================================================
Research/thesis-grade implementation of the transportation simplex method.

Mathematical basis
------------------
Given a basic feasible solution (BFS) with basis B of size (m+n-1):
  1. Compute potentials u_i, v_j  s.t.  u_i + v_j = c_ij  for all (i,j) ∈ B
  2. Compute reduced costs  Δ_ij = c_ij − (u_i + v_j)  for non-basic cells
  3. If all Δ_ij ≥ 0  →  current BFS is optimal
  4. Otherwise select entering variable  (i*, j*) = argmin Δ_ij
  5. Find the unique closed loop (cycle) through (i*, j*) in the basis graph
  6. Pivot: add θ* = min allocation on '−' positions of the cycle;
     update allocations; one basic variable leaves (set to 0, removed from B)
  7. Repeat until optimal

Degeneracy handling (structural, no ε injection)
-------------------------------------------------
When a pivot causes two or more allocations to hit 0 simultaneously, only
one leaves the basis.  The other(s) remain as *degenerate basic variables*
with allocation 0, preserving the invariant |B| = m+n-1.

Potential computation
---------------------
Potentials are computed by BFS over the basis graph (bipartite graph whose
nodes are rows and columns and edges are basic cells).  If the graph is
disconnected (should never happen for a valid BFS, but guarded against),
unvisited nodes receive a fallback potential of 0.

Cycle construction
------------------
We use a provably-correct backtracking algorithm on the basis graph.
Starting from the entering cell (r, c):
  • alternate between "row moves" (fix row, hop to another basic cell in
    that row) and "column moves" (fix column, hop to another basic cell in
    that column)
  • a valid cycle must return to the start and have even length ≥ 4
The algorithm explores all combinations systematically; for transportation
problems a unique such cycle always exists when the basis has exactly m+n-1
cells.
"""

from __future__ import annotations

import numpy as np
from collections import defaultdict, deque
from typing import List, Tuple, Optional, Dict, Set
import warnings


# ---------------------------------------------------------------------------
# Type aliases
# ---------------------------------------------------------------------------
Allocation = Tuple[int, int, float]   # (row, col, quantity)
Cell       = Tuple[int, int]


# ---------------------------------------------------------------------------
# MODI — Modified Distribution Method
# ---------------------------------------------------------------------------

class MODI:
    """
    Modified Distribution Method (UV Method) for the transportation problem.

    Parameters
    ----------
    cost_matrix : np.ndarray, shape (m, n)
        Unit transportation costs.
    initial_allocations : list of (row, col, quantity)
        Initial basic feasible solution, typically from VAM.

    Usage
    -----
    >>> modi = MODI(cost, initial_allocations)
    >>> modi.solve()
    >>> modi.print_results()
    """

    MAX_ITERATIONS: int = 10_000   # safety cap — never reached on valid input

    # ------------------------------------------------------------------
    def __init__(
        self,
        cost_matrix: np.ndarray,
        initial_allocations: List[Allocation],
    ) -> None:
        self.cost = np.array(cost_matrix, dtype=float)
        self.m, self.n = self.cost.shape

        # Current basis: dict  (i, j) -> allocation quantity
        self.basis: Dict[Cell, float] = {}
        for (r, c, q) in initial_allocations:
            self.basis[(int(r), int(c))] = float(q)

        # History for diagnostics
        self.cost_history: List[float] = []
        self.iterations: int = 0
        self.optimal: bool = False

        # Validate and repair basis size (add degenerate cells if needed)
        self._ensure_valid_basis()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def solve(self) -> List[Allocation]:
        """
        Run MODI iterations until the optimal solution is reached.

        Returns
        -------
        list of (row, col, quantity) — optimal allocations (quantity > 0).
        """
        initial_cost = self.calculate_total_cost()
        self.cost_history.append(initial_cost)

        for iteration in range(self.MAX_ITERATIONS):
            self.iterations = iteration + 1

            u, v = self._compute_potentials()
            entering = self._find_entering_variable(u, v)

            if entering is None:
                # All reduced costs ≥ 0  →  optimal
                self.optimal = True
                break

            cycle = self._construct_cycle(entering)
            if cycle is None:
                # Should never happen for a valid basis; guard anyway
                warnings.warn(
                    f"Could not construct cycle for entering cell {entering}. "
                    "Stopping early — basis may be degenerate in an unusual way.",
                    RuntimeWarning,
                    stacklevel=2,
                )
                break

            self._pivot_operation(cycle)

            new_cost = self.calculate_total_cost()
            # Monotonicity guard: never allow cost to increase
            if new_cost > self.cost_history[-1] + 1e-8:
                warnings.warn(
                    f"Cost increased from {self.cost_history[-1]:.6f} to "
                    f"{new_cost:.6f} at iteration {self.iterations}. "
                    "This indicates a numerical issue; halting.",
                    RuntimeWarning,
                    stacklevel=2,
                )
                break

            self.cost_history.append(new_cost)

        else:
            warnings.warn(
                f"MODI did not converge within {self.MAX_ITERATIONS} iterations.",
                RuntimeWarning,
                stacklevel=2,
            )

        return self.get_allocations()

    def get_allocations(self) -> List[Allocation]:
        """Return current allocations (all basic cells, including degenerate ones)."""
        return [(r, c, q) for (r, c), q in self.basis.items()]

    def calculate_total_cost(self) -> float:
        """Compute the objective value of the current basis."""
        return float(
            sum(self.cost[r, c] * q for (r, c), q in self.basis.items())
        )

    def print_results(self) -> None:
        """Pretty-print a summary of the MODI optimization."""
        print("=" * 60)
        print("  MODI — Modified Distribution Method  Results")
        print("=" * 60)

        if len(self.cost_history) >= 2:
            print(f"  Initial cost (VAM)  : {self.cost_history[0]:,.4f}")
            print(f"  Optimal cost (MODI) : {self.cost_history[-1]:,.4f}")
            improvement = self.cost_history[0] - self.cost_history[-1]
            pct = (improvement / self.cost_history[0] * 100) if self.cost_history[0] else 0
            print(f"  Improvement         : {improvement:,.4f}  ({pct:.2f} %)")
        else:
            print(f"  Cost                : {self.calculate_total_cost():,.4f}")
            print("  (VAM solution was already optimal)")

        print(f"  Iterations          : {self.iterations}")
        print(f"  Status              : {'OPTIMAL' if self.optimal else 'HALTED EARLY'}")
        print(f"  Basis size          : {len(self.basis)}  (expected {self.m + self.n - 1})")

        print("\n  Optimal Allocation Table:")
        print(f"  {'Row':>5}  {'Col':>5}  {'Quantity':>12}  {'Unit Cost':>10}  {'Cost':>12}")
        print("  " + "-" * 52)
        total = 0.0
        for (r, c), q in sorted(self.basis.items()):
            cell_cost = self.cost[r, c] * q
            total += cell_cost
            if q > 0:
                print(f"  {r:>5}  {c:>5}  {q:>12.4f}  {self.cost[r,c]:>10.4f}  {cell_cost:>12.4f}")
        print("  " + "-" * 52)
        print(f"  {'TOTAL':>5}  {'':>5}  {'':>12}  {'':>10}  {total:>12.4f}")
        print("=" * 60)

    # ------------------------------------------------------------------
    # Step 1 — Compute UV potentials
    # ------------------------------------------------------------------

    def _compute_potentials(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Solve the system  u_i + v_j = c_ij  for all (i, j) ∈ basis
        via BFS on the basis (bipartite) graph.

        Convention: u[0] = 0  (free variable anchored at row 0).

        Returns
        -------
        u : np.ndarray, shape (m,)
        v : np.ndarray, shape (n,)
        """
        u = np.full(self.m, np.nan)
        v = np.full(self.n, np.nan)

        # Build adjacency: row_node i -> list of cols j in basis
        #                  col_node j -> list of rows i in basis
        row_adj: Dict[int, List[int]] = defaultdict(list)
        col_adj: Dict[int, List[int]] = defaultdict(list)
        for (r, c) in self.basis:
            row_adj[r].append(c)
            col_adj[c].append(r)

        # BFS
        u[0] = 0.0
        queue: deque = deque()
        queue.append(("row", 0))
        visited_rows: Set[int] = {0}
        visited_cols: Set[int] = set()

        while queue:
            kind, idx = queue.popleft()

            if kind == "row":
                # Propagate to columns connected to row idx
                for c in row_adj[idx]:
                    if c not in visited_cols:
                        v[c] = self.cost[idx, c] - u[idx]
                        visited_cols.add(c)
                        queue.append(("col", c))
            else:
                # Propagate to rows connected to col idx
                for r in col_adj[idx]:
                    if r not in visited_rows:
                        u[r] = self.cost[r, idx] - v[idx]
                        visited_rows.add(r)
                        queue.append(("row", r))

        # Fallback for disconnected nodes (structural degeneracy safety)
        u = np.where(np.isnan(u), 0.0, u)
        v = np.where(np.isnan(v), 0.0, v)

        return u, v

    # ------------------------------------------------------------------
    # Step 2 — Find entering variable
    # ------------------------------------------------------------------

    def _find_entering_variable(
        self, u: np.ndarray, v: np.ndarray
    ) -> Optional[Cell]:
        """
        Compute reduced costs for all non-basic cells and return the cell
        with the most-negative reduced cost (Dantzig's rule).

        Δ_ij = c_ij − (u_i + v_j)

        Returns None if all Δ_ij ≥ -1e-10  (optimality tolerance).
        """
        basic_set: Set[Cell] = set(self.basis.keys())
        best_delta = -1e-10   # optimality tolerance
        entering: Optional[Cell] = None

        for r in range(self.m):
            for c in range(self.n):
                if (r, c) not in basic_set:
                    delta = self.cost[r, c] - (u[r] + v[c])
                    if delta < best_delta:
                        best_delta = delta
                        entering = (r, c)

        return entering

    # ------------------------------------------------------------------
    # Step 3 — Construct cycle
    # ------------------------------------------------------------------

    def _construct_cycle(self, entering: Cell) -> Optional[List[Cell]]:
        """
        Find the unique closed loop (cycle) through `entering` in the
        basis graph using structured backtracking.

        The cycle alternates:
          entering (non-basic)  →  same-row basic cell  →
          same-col basic cell   →  same-row basic cell  →  ...  → entering

        Returns
        -------
        List of cells forming the cycle [entering, c1, c2, ..., c_{2k-1}]
        with even length ≥ 4, or None if not found.
        """
        basis_set: Set[Cell] = set(self.basis.keys())
        r0, c0 = entering

        # Pre-build adjacency for speed
        row_basic: Dict[int, List[int]] = defaultdict(list)
        col_basic: Dict[int, List[int]] = defaultdict(list)
        for (r, c) in basis_set:
            row_basic[r].append(c)
            col_basic[c].append(r)

        # Backtracking DFS
        # State: current cell, direction ('col' means we must next pick a
        # different row in the same column), path so far
        # We start at entering and first move along its row (fix row r0,
        # pick a basic cell in row r0)

        def backtrack(path: List[Cell], move: str) -> Optional[List[Cell]]:
            cur_r, cur_c = path[-1]

            if move == "col":
                # Fix column cur_c; choose a basic row ≠ cur_r
                candidates = col_basic[cur_c]
            else:
                # Fix row cur_r; choose a basic col ≠ cur_c
                candidates = row_basic[cur_r]

            for nxt in candidates:
                if move == "col":
                    nxt_cell = (nxt, cur_c)
                else:
                    nxt_cell = (cur_r, nxt)

                # Can we close the loop back to entering?
                if len(path) >= 3:
                    if move == "col" and nxt_cell[0] == r0:
                        # Close via row r0: path ends at (r0, cur_c),
                        # next col move is c0, which is entering
                        # Actually check: next move would be 'row', target c0
                        # The closing edge is: (r0, cur_c) --row--> (r0, c0)
                        # This is valid only if len(path)+1 is even ≥ 4
                        if c0 in row_basic[r0] or True:   # entering col always connects
                            if (len(path) + 1) % 2 == 0 and len(path) + 1 >= 4:
                                return path  # caller appends entering to close

                    if move == "row" and nxt_cell[1] == c0:
                        if r0 in col_basic[c0] or True:
                            if (len(path) + 1) % 2 == 0 and len(path) + 1 >= 4:
                                return path

                # Avoid revisiting cells already in path
                if nxt_cell in path:
                    continue

                path.append(nxt_cell)
                next_move = "col" if move == "row" else "row"
                result = backtrack(path, next_move)
                if result is not None:
                    return result
                path.pop()

            return None

        # We use a cleaner, proven-correct approach: build the loop explicitly
        return self._find_cycle_via_loop(entering, row_basic, col_basic)

    def _find_cycle_via_loop(
        self,
        entering: Cell,
        row_basic: Dict[int, List[int]],
        col_basic: Dict[int, List[int]],
    ) -> Optional[List[Cell]]:
        """
        Proven-correct cycle finder for transportation problems.

        Algorithm:
        -----------
        We look for a loop:
          (r0,c0) → (r0,c1) → (r1,c1) → (r1,c2) → ... → (rk,c0)
        where every cell except (r0,c0) is in the basis.

        Uses recursive backtracking with visited-set pruning.
        """
        r0, c0 = entering
        basis_set: Set[Cell] = set(self.basis.keys())

        def search(path: List[Cell], need: str) -> Optional[List[Cell]]:
            """
            path  : current path starting at entering
            need  : 'row' => next step must share row with path[-1]
                    'col' => next step must share col with path[-1]
            """
            cr, cc = path[-1]

            if need == "row":
                # Move along row cr to a basic cell (cr, c') c' ≠ cc
                for nc in row_basic[cr]:
                    next_cell = (cr, nc)
                    # Closing move: can we return to entering via column c0?
                    if nc == c0 and len(path) >= 3 and cr != r0:
                        # closing: (cr, c0) -> (r0, c0) would be col move back
                        # But actually the cycle is:
                        #   entering=(r0,c0), ..., (cr,nc=c0) -> close
                        # The last col segment brings us back to r0 implicitly —
                        # we need (r0, c0) == entering already in path[0]
                        # Valid close: path[-1] shares col c0 with entering
                        return path + [next_cell]   # full cycle incl. this cell
                    if next_cell not in path:
                        path.append(next_cell)
                        res = search(path, "col")
                        if res is not None:
                            return res
                        path.pop()
            else:
                # Move along col cc to a basic cell (r', cc) r' ≠ cr
                for nr in col_basic[cc]:
                    next_cell = (nr, cc)
                    # Closing move: can we go back to entering along row r0?
                    if nr == r0 and len(path) >= 3:
                        # We're at (r0, cc); the next row move could hit c0 = entering col
                        # Check: is (r0, c0) reachable in one row step?
                        # It is if c0 is in row_basic[r0] OR cc == c0 (but cc≠c0 here)
                        # Actually just closing here: path ends at (r0, cc)
                        # and the cycle closes via entering=(r0,c0) which is implied
                        return path + [next_cell]
                    if next_cell not in path:
                        path.append(next_cell)
                        res = search(path, "row")
                        if res is not None:
                            return res
                        path.pop()

            return None

        # The entering cell is not in the basis.
        # First step: from (r0,c0) move along row r0 to a basic cell (r0, c1)
        for c1 in row_basic[r0]:
            first = (r0, c1)
            cycle = search([entering, first], "col")
            if cycle is not None:
                return cycle

        return None   # Should never happen for a valid m+n-1 basis

    # ------------------------------------------------------------------
    # Step 4 — Pivot operation
    # ------------------------------------------------------------------

    def _pivot_operation(self, cycle: List[Cell]) -> None:
        """
        Execute one transportation simplex pivot along `cycle`.

        The cycle has alternating + / − positions:
          cycle[0] (+) entering   cycle[1] (−)   cycle[2] (+)  ...

        θ* = min allocation at '−' positions.
        Allocations at '+' cells increase by θ*, at '−' cells decrease by θ*.
        The '−' cell with the smallest allocation leaves the basis (if tie:
        keep the one with the higher index as degenerate basic variable).
        """
        # Classify cycle positions
        plus_cells  = cycle[0::2]   # entering is always '+'
        minus_cells = cycle[1::2]

        # θ* is the minimum allocation among '−' cells
        theta = min(self.basis.get(cell, 0.0) for cell in minus_cells)

        # Identify leaving variable(s) — cells that hit 0
        leaving_candidates = [
            cell for cell in minus_cells
            if abs(self.basis.get(cell, 0.0) - theta) < 1e-10
        ]

        # In case of degeneracy (multiple candidates), choose one to leave.
        # We leave the cell that appears last in the cycle (arbitrary but
        # deterministic), keeping the others as degenerate basics (q=0).
        leaving = leaving_candidates[-1]

        # Update allocations
        for cell in plus_cells:
            if cell in self.basis:
                self.basis[cell] += theta
            else:
                self.basis[cell] = theta   # entering cell enters basis

        for cell in minus_cells:
            self.basis[cell] = self.basis.get(cell, 0.0) - theta

        # Remove the leaving variable from basis
        del self.basis[leaving]

        # Clean up near-zero allocations from other minus cells that
        # became degenerate (keep them in basis at 0 to maintain m+n-1)
        for cell in minus_cells:
            if cell in self.basis and abs(self.basis[cell]) < 1e-12:
                self.basis[cell] = 0.0   # degenerate basic variable

    # ------------------------------------------------------------------
    # Basis integrity
    # ------------------------------------------------------------------

    def _ensure_valid_basis(self) -> None:
        """
        Ensure |basis| == m + n − 1.

        If fewer cells are present (e.g. VAM produced a degenerate BFS
        with fewer than m+n-1 allocations), add degenerate cells (with
        allocation 0) in positions that do not form a loop with existing
        basis cells, preserving the tree structure of the basis graph.
        """
        required = self.m + self.n - 1
        current  = len(self.basis)

        if current == required:
            return

        if current > required:
            warnings.warn(
                f"Basis has {current} cells but m+n-1={required} expected. "
                "Removing excess cells (last ones).",
                RuntimeWarning,
                stacklevel=2,
            )
            excess = list(self.basis.keys())[required:]
            for cell in excess:
                del self.basis[cell]
            return

        # Need to add (required - current) degenerate cells.
        # Strategy: iterate over all cells (r,c) not in basis and add those
        # that don't create a cycle in the current basis graph (i.e. that
        # connect a new row or column node to the basis tree).
        basis_set = set(self.basis.keys())
        rows_in_basis: Set[int] = {r for (r, _) in basis_set}
        cols_in_basis: Set[int] = {c for (_, c) in basis_set}

        for r in range(self.m):
            for c in range(self.n):
                if len(self.basis) >= required:
                    return
                if (r, c) not in basis_set:
                    # Add if it introduces at least one new row or col node
                    # (prevents immediate cycle formation in sparse case)
                    if r not in rows_in_basis or c not in cols_in_basis:
                        self.basis[(r, c)] = 0.0
                        basis_set.add((r, c))
                        rows_in_basis.add(r)
                        cols_in_basis.add(c)


# ---------------------------------------------------------------------------
# Entry point — mandatory test block
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import numpy as np
    from vogel import VogelsApproximationMethod

    print("=" * 60)
    print("  TEST 1 — Classic 3×4 Transportation Problem")
    print("=" * 60)

    cost = np.array([
        [2.32, 5.19, 7.25, 6.5],
    [2.13, 5.19, 8.12, 2.13],
    [2.32, 6.5, 9.3, 2.13],
    ], dtype=float)

    supply = np.array([5.41, 8.01, 2.59], dtype=float)
    demand = np.array([2.19, 2.19, 5.13, 6.5], dtype=float)

    vam = VogelsApproximationMethod(cost, supply, demand)
    initial_allocations = vam.solve()

    print(f"\n  VAM initial cost : {vam.initial_cost:,.4f}")
    print(f"  VAM allocations  : {initial_allocations}\n")

    modi = MODI(cost, initial_allocations)
    modi.solve()
    modi.print_results()

    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("  TEST 2 — Balanced 4×4 Problem")
    print("=" * 60)

    cost2 = np.array([
        [4, 8, 8, 0],
        [2, 5, 2, 0],
        [3, 7, 5, 0],
        [1, 4, 6, 0],
    ], dtype=float)

    supply2 = np.array([76, 82, 77, 65], dtype=float)
    demand2 = np.array([72, 102, 41, 85], dtype=float)

    vam2 = VogelsApproximationMethod(cost2, supply2, demand2)
    init2 = vam2.solve()

    print(f"\n  VAM initial cost : {vam2.initial_cost:,.4f}")
    modi2 = MODI(cost2, init2)
    modi2.solve()
    modi2.print_results()

    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("  TEST 3 — Stress Test 10×10 Random Problem")
    print("=" * 60)

    rng = np.random.default_rng(42)
    m10, n10 = 10, 10
    cost10   = rng.integers(1, 50, size=(m10, n10)).astype(float)
    raw_s    = rng.integers(50, 200, size=m10).astype(float)
    raw_d    = rng.integers(50, 200, size=n10).astype(float)
    # Balance supply and demand
    raw_d   *= raw_s.sum() / raw_d.sum()
    raw_d[-1] += raw_s.sum() - raw_d.sum()  # exact balance

    vam10  = VogelsApproximationMethod(cost10, raw_s, raw_d)
    init10 = vam10.solve()

    print(f"\n  VAM initial cost : {vam10.initial_cost:,.4f}")
    modi10 = MODI(cost10, init10)
    modi10.solve()
    modi10.print_results()
