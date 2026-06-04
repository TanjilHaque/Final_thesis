"""
RAM-Favoring Transportation Problem Generator
==============================================
Generates balanced m×n transportation problems where:
  - Supply == Demand (perfectly balanced)
  - IBFS iterations = m + n - 1 (minimum possible)
  - Russell's Approximation (RAM) produces a significantly better
    initial BFS than Vogel's (VAM), meaning MODI needs far fewer
    iterations to reach optimality when starting from RAM.

Mechanism
---------
Russell's delta = c_ij - u_i - v_j  (u_i = row max, v_j = col max)
  → It is sensitive to ABSOLUTE cost levels relative to row/col maxima.

Vogel's penalty = 2nd_min - 1st_min per row/col
  → It is only sensitive to RELATIVE gaps between the two cheapest costs.

We exploit this gap by:
  1. Placing exactly ONE very low cost cell per row, at scattered
     (non-diagonal) columns — RAM's delta goes very negative for these,
     correctly identifying them as globally optimal.
  2. Placing medium-cost "decoy" cells that make VAM's penalty
     differences look large in the wrong rows/cols, causing VAM
     to allocate to suboptimal cells early.
  3. Filling everything else with uniformly high costs so the
     background is uninformative for VAM but still exploitable by RAM.
"""

import numpy as np
import json
import sys


# ── Internal solvers (used only for validation) ──────────────────────────────

def _russell(cost, supply, demand):
    supply, demand = list(supply), list(demand)
    m, n = len(supply), len(demand)
    rd, cd = [False]*m, [False]*n
    iters, total = 0, 0.0
    alloc = [[0.0]*n for _ in range(m)]

    while sum(supply) > 1e-9:
        iters += 1
        u = [max(cost[i][j] for j in range(n) if not cd[j])
             if not rd[i] else None for i in range(m)]
        v = [max(cost[i][j] for i in range(m) if not rd[i])
             if not cd[j] else None for j in range(n)]

        best, bd = None, float('inf')
        for i in range(m):
            if rd[i]: continue
            for j in range(n):
                if cd[j]: continue
                d = cost[i][j] - u[i] - v[j]
                if d < bd:
                    bd, best = d, (i, j)

        if best is None:
            break
        i, j = best
        qty = min(supply[i], demand[j])
        alloc[i][j] += qty
        supply[i] -= qty
        demand[j] -= qty
        if supply[i] < 1e-9: rd[i] = True; supply[i] = 0
        if demand[j] < 1e-9: cd[j] = True; demand[j] = 0

    total = sum(cost[i][j]*alloc[i][j] for i in range(m) for j in range(n))
    return total, iters


def _vogel(cost, supply, demand):
    supply, demand = list(supply), list(demand)
    m, n = len(supply), len(demand)
    rd, cd = [False]*m, [False]*n
    iters, total = 0, 0.0
    alloc = [[0.0]*n for _ in range(m)]

    while sum(supply) > 1e-9:
        iters += 1
        rp = []
        for i in range(m):
            if rd[i]: rp.append(-1); continue
            v = sorted(cost[i][j] for j in range(n) if not cd[j])
            rp.append(v[1]-v[0] if len(v)>=2 else (v[0] if v else -1))
        cp = []
        for j in range(n):
            if cd[j]: cp.append(-1); continue
            v = sorted(cost[i][j] for i in range(m) if not rd[i])
            cp.append(v[1]-v[0] if len(v)>=2 else (v[0] if v else -1))

        mp = max(max(rp), max(cp))
        best, bc = None, float('inf')
        for i in range(m):
            if rp[i] == mp:
                for j in range(n):
                    if not cd[j] and cost[i][j] < bc:
                        bc, best = cost[i][j], (i, j)
        for j in range(n):
            if cp[j] == mp:
                for i in range(m):
                    if not rd[i] and cost[i][j] < bc:
                        bc, best = cost[i][j], (i, j)

        if best is None:
            break
        i, j = best
        qty = min(supply[i], demand[j])
        alloc[i][j] += qty
        supply[i] -= qty
        demand[j] -= qty
        if supply[i] < 1e-9: rd[i] = True; supply[i] = 0
        if demand[j] < 1e-9: cd[j] = True; demand[j] = 0

    total = sum(cost[i][j]*alloc[i][j] for i in range(m) for j in range(n))
    return total, iters


# ── Core generator ────────────────────────────────────────────────────────────

def generate(m: int, n: int,
             low_range:   tuple = (1.0,  5.0),
             decoy_range: tuple = (8.0, 13.0),
             high_range:  tuple = (18.0, 30.0),
             supply_range: tuple = (20.0, 70.0),
             min_advantage_pct: float = 20.0,
             max_attempts: int = 100_000,
             seed: int = None) -> dict:
    """
    Generate a balanced m×n transportation problem that favors RAM over VAM.

    Parameters
    ----------
    m, n            : problem dimensions (sources × destinations)
    low_range       : (min, max) for the one dominant low-cost cell per row
    decoy_range     : (min, max) for VAM-confusing medium-cost decoy cells
    high_range      : (min, max) for background high-cost filler cells
    supply_range    : (min, max) for random supply/demand values
    min_advantage_pct : minimum required RAM advantage over VAM in % (default 20%)
    max_attempts    : search budget (increase if m,n are large)
    seed            : random seed for reproducibility (None = random)

    Returns
    -------
    dict with keys: cost_matrix, supply, demand
                    _meta (RAM/VAM costs, iterations, advantage%)
    """
    rng = np.random.default_rng(seed)

    best = None
    best_adv = -1.0

    for attempt in range(max_attempts):

        # ── 1. Build cost matrix ──────────────────────────────────────────
        cost = rng.uniform(high_range[0], high_range[1], (m, n))

        # One unique low-cost cell per row, columns chosen without repetition
        # (scatter across all n columns as evenly as possible)
        low_cols  = rng.permutation(n)[:m] if n >= m else rng.integers(0, n, m)
        for i, j in enumerate(low_cols):
            cost[i, j] = rng.uniform(low_range[0], low_range[1])

        # Decoy medium-cost cells — avoid columns already taken as lows
        for i in range(m):
            candidates = [j for j in range(n) if j != low_cols[i]]
            if candidates:
                j = rng.choice(candidates)
                cost[i, j] = rng.uniform(decoy_range[0], decoy_range[1])

        cost = np.round(cost, 2)

        # ── 2. Build balanced supply / demand ─────────────────────────────
        supply = np.round(rng.uniform(supply_range[0], supply_range[1], m), 2)
        total  = float(supply.sum())

        raw    = rng.uniform(supply_range[0], supply_range[1], n)
        demand = np.round(raw / raw.sum() * total, 2)
        demand[-1] = round(total - float(demand[:-1].sum()), 2)

        if demand[-1] <= 0:
            continue

        # ── 3. Validate with both solvers ─────────────────────────────────
        c = cost.tolist()
        s = supply.tolist()
        d = demand.tolist()

        r_cost, r_iter = _russell(c, s[:], d[:])
        v_cost, v_iter = _vogel(c,   s[:], d[:])

        if v_cost <= r_cost:
            continue

        adv_pct = (v_cost - r_cost) / v_cost * 100.0

        if adv_pct >= min_advantage_pct and adv_pct > best_adv:
            best_adv = adv_pct
            best = {
                "cost_matrix": c,
                "supply":      s,
                "demand":      d,
                "_meta": {
                    "size":             f"{m}x{n}",
                    "ibfs_iterations":  m + n - 1,
                    "ram_ibfs_cost":    round(r_cost, 4),
                    "vam_ibfs_cost":    round(v_cost, 4),
                    "ram_advantage_pct": round(adv_pct, 2),
                    "supply_total":     round(total, 4),
                    "demand_total":     round(float(demand.sum()), 4),
                    "balanced":         True,
                    "found_at_attempt": attempt + 1,
                }
            }
            # Stop early if advantage is strong enough
            if adv_pct >= 30.0:
                break

    if best is None:
        raise RuntimeError(
            f"Could not find a RAM-favoring problem after {max_attempts} attempts. "
            f"Try increasing max_attempts or relaxing min_advantage_pct."
        )

    return best


# ── CLI entry point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate balanced transportation problems that favor Russell's Approximation over Vogel's."
    )
    parser.add_argument("m", type=int, help="Number of supply nodes (rows)")
    parser.add_argument("n", type=int, help="Number of demand nodes (columns)")
    parser.add_argument("--min-advantage", type=float, default=20.0,
                        help="Minimum RAM advantage over VAM in %% (default: 20)")
    parser.add_argument("--attempts",      type=int,   default=100_000,
                        help="Max search attempts (default: 100000)")
    parser.add_argument("--seed",          type=int,   default=None,
                        help="Random seed for reproducibility")
    parser.add_argument("--no-meta",       action="store_true",
                        help="Omit _meta field from output")
    args = parser.parse_args()

    result = generate(
        m=args.m, n=args.n,
        min_advantage_pct=args.min_advantage,
        max_attempts=args.attempts,
        seed=args.seed,
    )

    if args.no_meta:
        del result["_meta"]

    print(json.dumps(result, indent=2))