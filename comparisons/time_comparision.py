"""
time_comparison.py — Research-Grade Timing Benchmark
=====================================================
Compares execution time of:
  • VAM  (Vogel's Approximation Method)
  • RAM  (Russell's Approximation Method)
  • VAM + MODI  (VAM as initial BFS → MODI optimisation)
  • RAM + MODI  (RAM as initial BFS → MODI optimisation)

Statistical justification
--------------------------
Each method is run N_RUNS times (default 30).  For each run, the clock is
taken as tightly as possible around the solver call only — I/O, imports, and
object construction outside the timed region.

Reported statistics per method:
  mean, std, variance, min, max, 95 % confidence interval (t-distribution),
  coefficient of variation (CV).

Input
-----
Pass the path to a JSON file as the first CLI argument:

    python time_comparison.py path/to/problem.json

JSON schema (single problem):
{
    "cost":   [[c00, c01, ...], [c10, ...], ...],
    "supply": [s0, s1, ...],
    "demand": [d0, d1, ...]
}

Output
------
A formatted report printed to stdout and also saved as
  time_comparison_report.txt  (next to the JSON file).
"""

from __future__ import annotations

import json
import math
import os
import sys
import time
import warnings
from pathlib import Path
from typing import Callable, Dict, List, Tuple

import numpy as np

# ---------------------------------------------------------------------------
# Resolve package root so this script works when run directly from
# comparisons/ or from FINAL_THESIS_CODES/
# ---------------------------------------------------------------------------
_THIS_DIR  = Path(__file__).resolve().parent          # .../comparisons/
_ROOT_DIR  = _THIS_DIR.parent                         # .../FINAL_THESIS_CODES/
if str(_ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(_ROOT_DIR))

from algorithms.vogel   import VogelsApproximationMethod   # noqa: E402
from algorithms.russell import RussellsApproximationMethod  # noqa: E402
from algorithms.modi    import MODI                         # noqa: E402

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
N_RUNS      = 30      # number of timed repetitions — minimum for CLT
ALPHA       = 0.05    # significance level for CI  (two-tailed t, 95 %)

# t* critical values (two-tailed, df = N_RUNS - 1 = 29, α = 0.05) ≈ 2.045
# Hard-coded so scipy is not required.
_T_CRIT: Dict[int, float] = {
    29: 2.045, 49: 2.010, 99: 1.984,
}

def _t_critical(df: int) -> float:
    """Return approximate t* for 95 % CI given degrees of freedom."""
    # Use closest tabulated value (conservative for small df)
    for threshold, t in sorted(_T_CRIT.items()):
        if df <= threshold:
            return t
    return 1.960   # z* for large samples


# ---------------------------------------------------------------------------
# Utility — load problem
# ---------------------------------------------------------------------------

def load_problem(json_path: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Load cost matrix, supply, demand from a JSON file."""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    cost_key = "cost" if "cost" in data else "cost_matrix"
    cost   = np.array(data[cost_key],   dtype=float)
    supply = np.array(data["supply"], dtype=float)
    demand = np.array(data["demand"], dtype=float)
    return cost, supply, demand


# ---------------------------------------------------------------------------
# Timed runner helpers
# ---------------------------------------------------------------------------

def _time_vam(cost: np.ndarray, supply: np.ndarray, demand: np.ndarray
              ) -> Tuple[float, List, float]:
    """Run VAM once; return (elapsed_seconds, allocations, initial_cost)."""
    vam = VogelsApproximationMethod(cost, supply, demand)
    t0  = time.perf_counter()
    allocs = vam.solve()
    elapsed = time.perf_counter() - t0
    return elapsed, allocs, vam.initial_cost


def _time_ram(cost: np.ndarray, supply: np.ndarray, demand: np.ndarray
              ) -> Tuple[float, List, float]:
    """Run RAM once; return (elapsed_seconds, allocations, initial_cost)."""
    ram = RussellsApproximationMethod(cost, supply, demand)
    t0  = time.perf_counter()
    allocs = ram.solve()
    elapsed = time.perf_counter() - t0
    return elapsed, allocs, ram.initial_cost


def _time_modi(cost: np.ndarray, initial_allocs: List
               ) -> Tuple[float, float]:
    """Run MODI once on pre-computed allocations; return (elapsed, optimal_cost)."""
    modi = MODI(cost, initial_allocs)
    t0   = time.perf_counter()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        modi.solve()
    elapsed = time.perf_counter() - t0
    return elapsed, modi.calculate_total_cost()


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------

class Stats:
    """Descriptive statistics for a list of timing samples."""

    def __init__(self, name: str, samples: List[float]) -> None:
        self.name    = name
        self.n       = len(samples)
        arr          = np.array(samples, dtype=float)
        self.mean    = float(np.mean(arr))
        self.std     = float(np.std(arr, ddof=1))
        self.var     = float(np.var(arr, ddof=1))
        self.minimum = float(np.min(arr))
        self.maximum = float(np.max(arr))
        self.cv      = (self.std / self.mean * 100) if self.mean > 0 else 0.0
        # 95 % CI  via t-distribution
        df            = self.n - 1
        t_star        = _t_critical(df)
        margin        = t_star * self.std / math.sqrt(self.n)
        self.ci_lo    = self.mean - margin
        self.ci_hi    = self.mean + margin


# ---------------------------------------------------------------------------
# Core benchmark loop
# ---------------------------------------------------------------------------

def run_benchmark(
    cost: np.ndarray,
    supply: np.ndarray,
    demand: np.ndarray,
    n_runs: int = N_RUNS,
) -> Dict[str, Stats]:
    """
    Run all four methods n_runs times each and return a dict of Stats objects.

    Keys: "VAM", "RAM", "VAM+MODI", "RAM+MODI"
    """
    vam_times:      List[float] = []
    ram_times:      List[float] = []
    vam_modi_times: List[float] = []
    ram_modi_times: List[float] = []

    # Also collect costs for the final summary (last run values are enough)
    costs: Dict[str, float] = {}

    for run in range(n_runs):
        # ---- VAM ----
        t_vam, vam_allocs, vam_cost = _time_vam(cost, supply, demand)
        vam_times.append(t_vam)

        # ---- RAM ----
        t_ram, ram_allocs, ram_cost = _time_ram(cost, supply, demand)
        ram_times.append(t_ram)

        # ---- VAM + MODI ----
        # Re-solve VAM to get fresh allocations (clock only MODI)
        _, fresh_vam, _ = _time_vam(cost, supply, demand)
        t_modi_vam, vm_cost = _time_modi(cost, fresh_vam)
        vam_modi_times.append(t_vam + t_modi_vam)   # combined pipeline time

        # ---- RAM + MODI ----
        _, fresh_ram, _ = _time_ram(cost, supply, demand)
        t_modi_ram, rm_cost = _time_modi(cost, fresh_ram)
        ram_modi_times.append(t_ram + t_modi_ram)

        # Store costs from last run
        if run == n_runs - 1:
            costs["VAM"]      = vam_cost
            costs["RAM"]      = ram_cost
            costs["VAM+MODI"] = vm_cost
            costs["RAM+MODI"] = rm_cost

    return (
        {
            "VAM":      Stats("VAM",      vam_times),
            "RAM":      Stats("RAM",      ram_times),
            "VAM+MODI": Stats("VAM+MODI", vam_modi_times),
            "RAM+MODI": Stats("RAM+MODI", ram_modi_times),
        },
        costs,
    )


# ---------------------------------------------------------------------------
# Report formatter
# ---------------------------------------------------------------------------

_W = 78   # report width

def _line(char: str = "─") -> str:
    return char * _W

def _header(title: str) -> str:
    pad = (_W - len(title) - 2) // 2
    return f"{'═' * pad}  {title}  {'═' * (_W - pad - len(title) - 2)}"


def build_report(
    stats_dict: Dict[str, Stats],
    costs: Dict[str, float],
    problem_path: str,
    cost: np.ndarray,
    supply: np.ndarray,
    demand: np.ndarray,
    n_runs: int,
) -> str:
    lines: List[str] = []
    m, n = cost.shape

    lines.append(_header("TRANSPORTATION METHOD — TIMING BENCHMARK"))
    lines.append(f"  Problem file  : {problem_path}")
    lines.append(f"  Problem size  : {m} × {n}  "
                 f"(supply sum = {supply.sum():.4f}, "
                 f"demand sum = {demand.sum():.4f})")
    lines.append(f"  Repetitions   : {n_runs}")
    lines.append(f"  Confidence    : 95 %  (two-tailed t, df = {n_runs - 1})")
    lines.append(f"  Timer         : time.perf_counter()  (highest resolution)")
    lines.append(_line())

    # ── Per-method detailed stats ──
    lines.append("")
    lines.append("  DETAILED TIMING STATISTICS  (all values in seconds)")
    lines.append("")

    col_w = 14
    header_row = (
        f"  {'Method':<14}"
        f"{'Mean':>{col_w}}"
        f"{'Std Dev':>{col_w}}"
        f"{'Variance':>{col_w}}"
        f"{'Min':>{col_w}}"
        f"{'Max':>{col_w}}"
    )
    lines.append(header_row)
    lines.append("  " + _line("─")[2:])

    method_order = ["VAM", "RAM", "VAM+MODI", "RAM+MODI"]
    for key in method_order:
        s = stats_dict[key]
        lines.append(
            f"  {s.name:<14}"
            f"{s.mean:>{col_w}.6f}"
            f"{s.std:>{col_w}.6f}"
            f"{s.var:>{col_w}.8f}"
            f"{s.minimum:>{col_w}.6f}"
            f"{s.maximum:>{col_w}.6f}"
        )

    lines.append("")

    # ── Confidence intervals ──
    lines.append("  95 % CONFIDENCE INTERVALS FOR MEAN EXECUTION TIME")
    lines.append("")
    ci_header = (
        f"  {'Method':<14}"
        f"{'Mean (s)':>14}"
        f"{'CI  Lower':>16}"
        f"{'CI  Upper':>16}"
        f"{'CV (%)':>12}"
    )
    lines.append(ci_header)
    lines.append("  " + _line("─")[2:])

    for key in method_order:
        s = stats_dict[key]
        lines.append(
            f"  {s.name:<14}"
            f"{s.mean:>14.6f}"
            f"{s.ci_lo:>16.6f}"
            f"{s.ci_hi:>16.6f}"
            f"{s.cv:>12.2f}"
        )

    lines.append("")
    lines.append(
        "  CV (Coefficient of Variation) < 10 % indicates stable, "
        "reproducible measurements."
    )

    # ── Solution quality ──
    lines.append("")
    lines.append(_line())
    lines.append("")
    lines.append("  SOLUTION QUALITY  (transportation cost, last run)")
    lines.append("")
    q_header = (
        f"  {'Method':<14}"
        f"{'Cost':>16}"
        f"{'vs. VAM+MODI':>18}"
        f"{'vs. RAM+MODI':>18}"
    )
    lines.append(q_header)
    lines.append("  " + _line("─")[2:])

    best_cost = min(costs["VAM+MODI"], costs["RAM+MODI"])
    for key in method_order:
        c = costs[key]
        diff_vm = c - costs["VAM+MODI"]
        diff_rm = c - costs["RAM+MODI"]
        lines.append(
            f"  {key:<14}"
            f"{c:>16.4f}"
            f"{diff_vm:>+18.4f}"
            f"{diff_rm:>+18.4f}"
        )

    # ── Speed comparison ──
    lines.append("")
    lines.append(_line())
    lines.append("")
    lines.append("  SPEED COMPARISON  (ratio of mean times)")
    lines.append("")

    pairs = [
        ("VAM  vs  RAM",       "VAM",      "RAM"),
        ("VAM+MODI  vs  RAM+MODI", "VAM+MODI", "RAM+MODI"),
        ("VAM  vs  VAM+MODI",  "VAM",      "VAM+MODI"),
        ("RAM  vs  RAM+MODI",  "RAM",      "RAM+MODI"),
    ]

    lines.append(f"  {'Comparison':<30}  {'Ratio':>10}  {'Interpretation'}")
    lines.append("  " + _line("─")[2:])

    for label, k1, k2 in pairs:
        m1 = stats_dict[k1].mean
        m2 = stats_dict[k2].mean
        ratio = m1 / m2 if m2 > 0 else float("inf")
        if ratio >= 1.0:
            interp = f"{k1} is {ratio:.2f}× slower than {k2}"
        else:
            interp = f"{k1} is {1/ratio:.2f}× faster than {k2}"
        lines.append(f"  {label:<30}  {ratio:>10.4f}  {interp}")

    # ── Summary verdict ──
    lines.append("")
    lines.append(_line())
    lines.append("")
    lines.append("  SUMMARY")
    lines.append("")

    fastest_ibfs = "VAM" if stats_dict["VAM"].mean <= stats_dict["RAM"].mean else "RAM"
    fastest_full = (
        "VAM+MODI"
        if stats_dict["VAM+MODI"].mean <= stats_dict["RAM+MODI"].mean
        else "RAM+MODI"
    )
    cheapest = min(costs, key=costs.get)

    lines.append(f"  • Fastest initial BFS         : {fastest_ibfs}")
    lines.append(f"  • Fastest complete pipeline   : {fastest_full}")
    lines.append(f"  • Lowest solution cost        : {cheapest}  "
                 f"({costs[cheapest]:.4f})")
    lines.append(f"  • VAM+MODI mean time          : "
                 f"{stats_dict['VAM+MODI'].mean:.6f} s  "
                 f"(95 % CI [{stats_dict['VAM+MODI'].ci_lo:.6f}, "
                 f"{stats_dict['VAM+MODI'].ci_hi:.6f}])")
    lines.append(f"  • RAM+MODI mean time          : "
                 f"{stats_dict['RAM+MODI'].mean:.6f} s  "
                 f"(95 % CI [{stats_dict['RAM+MODI'].ci_lo:.6f}, "
                 f"{stats_dict['RAM+MODI'].ci_hi:.6f}])")
    lines.append("")

    # Overlap check (do the CIs overlap?)
    vm = stats_dict["VAM+MODI"]
    rm = stats_dict["RAM+MODI"]
    overlap = vm.ci_lo <= rm.ci_hi and rm.ci_lo <= vm.ci_hi
    if overlap:
        lines.append(
            "  ⚠  The 95 % CIs of VAM+MODI and RAM+MODI OVERLAP — the "
            "difference in mean\n"
            "     execution time is NOT statistically significant at α = 0.05."
        )
    else:
        faster = "VAM+MODI" if vm.mean < rm.mean else "RAM+MODI"
        lines.append(
            f"  ✓  The 95 % CIs do NOT overlap — {faster} is statistically\n"
            f"     significantly faster at α = 0.05."
        )

    lines.append("")
    lines.append(_line("═"))
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    # ── Argument handling ──
    if len(sys.argv) < 2:
        print("Usage:  python time_comparison.py <path_to_problem.json>")
        print("        JSON must have keys: cost, supply, demand")
        sys.exit(1)

    json_path = sys.argv[1]
    if not os.path.isfile(json_path):
        print(f"Error: file not found — {json_path}")
        sys.exit(1)

    # ── Load problem ──
    print(f"\nLoading problem from: {json_path}")
    cost, supply, demand = load_problem(json_path)
    m, n = cost.shape
    print(f"  Size: {m} × {n}   Supply sum: {supply.sum():.4f}   "
          f"Demand sum: {demand.sum():.4f}")

    # ── Run benchmark ──
    print(f"\nRunning benchmark ({N_RUNS} repetitions per method) …")
    print("  This may take a moment for large problems.\n")

    stats_dict, costs = run_benchmark(cost, supply, demand, N_RUNS)

    # Quick progress summary to stdout
    for key in ["VAM", "RAM", "VAM+MODI", "RAM+MODI"]:
        s = stats_dict[key]
        print(f"  {key:<12}  mean = {s.mean:.6f} s   "
              f"std = {s.std:.6f} s   "
              f"CV = {s.cv:.2f} %")

    # ── Build and print report ──
    report = build_report(
        stats_dict, costs, json_path, cost, supply, demand, N_RUNS
    )

    print("\n")
    print(report)

    # ── Save report ──
    report_path = Path(json_path).with_suffix("") \
        .parent / (Path(json_path).stem + "_time_report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\nReport saved to: {report_path}")


if __name__ == "__main__":
    main()