import numpy as np
import json
import time

def _vectorized_russell(cost_orig, supply_orig, demand_orig):
    """Vectorized Russell's Approximation Method using NumPy."""
    cost = cost_orig.copy()
    supply = supply_orig.copy()
    demand = demand_orig.copy()
    
    m, n = cost.shape
    alloc = np.zeros((m, n))
    
    row_active = np.ones(m, dtype=bool)
    col_active = np.ones(n, dtype=bool)
    
    # Large value used to mask inactive rows/columns
    INF = 1e12

    while np.sum(supply) > 1e-9:
        # Mask cost matrix to find active maximums
        masked_for_max = np.where(
            (row_active[:, None]) & (col_active[None, :]), 
            cost, 
            -INF
        )
        
        u = np.max(masked_for_max, axis=1) # Row maxes
        v = np.max(masked_for_max, axis=0) # Col maxes
        
        # Compute Delta matrix: c_ij - u_i - v_j
        # Using broadcasting, masked so we ignore inactive cells
        delta = cost - u[:, None] - v[None, :]
        delta = np.where((row_active[:, None]) & (col_active[None, :]), delta, INF)
        
        # Find global minimum delta
        idx = np.argmin(delta)
        i, j = divmod(idx, n)
        
        # Allocate
        qty = min(supply[i], demand[j])
        alloc[i, j] += qty
        supply[i] -= qty
        demand[j] -= qty
        
        if supply[i] < 1e-9:
            row_active[i] = False
            supply[i] = 0
        if demand[j] < 1e-9:
            col_active[j] = False
            demand[j] = 0

    total_cost = np.sum(cost_orig * alloc)
    return total_cost

def _vectorized_vogel(cost_orig, supply_orig, demand_orig):
    """Vectorized Vogel's Approximation Method using NumPy."""
    cost = cost_orig.copy()
    supply = supply_orig.copy()
    demand = demand_orig.copy()
    
    m, n = cost.shape
    alloc = np.zeros((m, n))
    
    row_active = np.ones(m, dtype=bool)
    col_active = np.ones(n, dtype=bool)
    
    INF = 1e12

    while np.sum(supply) > 1e-9:
        # Mask cost matrix to find active minimums
        masked_cost = np.where(
            (row_active[:, None]) & (col_active[None, :]), 
            cost, 
            INF
        )
        
        # Sort along rows and columns to find 1st and 2nd minimums efficiently
        sorted_rows = np.sort(masked_cost, axis=1)
        sorted_cols = np.sort(masked_cost, axis=0)
        
        # Calculate row and column penalties
        # If only 1 element remains, penalty is that element itself
        rp = np.where(row_active, 
                      np.where(sorted_rows[:, 1] < INF, sorted_rows[:, 1] - sorted_rows[:, 0], sorted_rows[:, 0]), 
                      -1.0)
        cp = np.where(col_active, 
                      np.where(sorted_cols[1, :] < INF, sorted_cols[1, :] - sorted_cols[0, :], sorted_cols[0, :]), 
                      -1.0)
        
        max_rp = np.max(rp)
        max_cp = np.max(cp)
        
        # Determine whether to pick from row or column penalty leader
        if max_rp >= max_cp:
            i = np.argmax(rp)
            j = np.argmin(masked_cost[i, :])
        else:
            j = np.argmax(cp)
            i = np.argmin(masked_cost[:, j])
            
        # Allocate
        qty = min(supply[i], demand[j])
        alloc[i, j] += qty
        supply[i] -= qty
        demand[j] -= qty
        
        if supply[i] < 1e-9:
            row_active[i] = False
            supply[i] = 0
        if demand[j] < 1e-9:
            col_active[j] = False
            demand[j] = 0

    total_cost = np.sum(cost_orig * alloc)
    return total_cost

def generate_fast(m: int, n: int,
                  low_range:   tuple = (1.0,  5.0),
                  decoy_range: tuple = (8.0, 13.0),
                  high_range:  tuple = (18.0, 30.0),
                  supply_range: tuple = (20.0, 70.0),
                  min_advantage_pct: float = 20.0,
                  max_attempts: int = 5000,
                  seed: int = None) -> dict:
    
    rng = np.random.default_rng(seed)
    best = None
    best_adv = -1.0

    for attempt in range(max_attempts):
        # 1. Faster Matrix Generation with scale-aware traps
        cost = rng.uniform(high_range[0], high_range[1], (m, n))

        # Disperse one perfect low-cost cell per row
        low_cols = rng.permutation(n)[:m] if n >= m else rng.integers(0, n, m)
        for i, j in enumerate(low_cols):
            cost[i, j] = rng.uniform(low_range[0], low_range[1])

        # SCALE ENHANCEMENT: Inject multiple decoys per row for large matrices
        # This keeps the VAM penalty trap structurally effective at 100x100
        num_decoys = max(1, n // 10) 
        for i in range(m):
            candidates = [j for j in range(n) if j != low_cols[i]]
            if candidates:
                decoy_cols = rng.choice(candidates, size=min(num_decoys, len(candidates)), replace=False)
                cost[i, decoy_cols] = rng.uniform(decoy_range[0], decoy_range[1])

        cost = np.round(cost, 2)

        # 2. Balanced supply / demand generation
        supply = np.round(rng.uniform(supply_range[0], supply_range[1], m), 2)
        total = float(supply.sum())

        raw = rng.uniform(supply_range[0], supply_range[1], n)
        demand = np.round(raw / raw.sum() * total, 2)
        demand[-1] = round(total - float(demand[:-1].sum()), 2)

        if demand[-1] <= 0:
            continue

        # 3. Validation via blazing-fast NumPy solvers
        r_cost = _vectorized_russell(cost, supply, demand)
        v_cost = _vectorized_vogel(cost, supply, demand)

        if v_cost <= r_cost:
            continue

        adv_pct = (v_cost - r_cost) / v_cost * 100.0

        if adv_pct >= min_advantage_pct and adv_pct > best_adv:
            best_adv = adv_pct
            best = {
                "cost_matrix": cost.tolist(),
                "supply":      supply.tolist(),
                "demand":      demand.tolist(),
                "_meta": {
                    "size":             f"{m}x{n}",
                    "ibfs_iterations":  m + n - 1,
                    "ram_ibfs_cost":    round(r_cost, 4),
                    "vam_ibfs_cost":    round(v_cost, 4),
                    "ram_advantage_pct": round(adv_pct, 2),
                    "supply_total":     round(total, 4),
                    "found_at_attempt": attempt + 1,
                }
            }
            # Break early if we hit a highly successful generation layout
            if adv_pct >= 25.0:
                break

    if best is None:
        raise RuntimeError(
            f"Could not find a matrix with a {min_advantage_pct}% RAM advantage within budget. "
            f"At 100x100, try setting '--min-advantage' slightly lower (e.g., 10-15%) for an instant result."
        )

    return best

if __name__ == "__main__":
    # Test run for 100x100 data size
    print("Generating 100x100 matrix layout...")
    start_time = time.time()
    
    try:
        # We look for a strict 20% advantage. 
        # (If it fails to hit 20% due to random distribution seed luck, drop to 15%)
        result = generate_fast(m=100, n=100, min_advantage_pct=20.0, max_attempts=1000, seed=42)
        print(f"Success! Found in {time.time() - start_time:.2f} seconds.")
        print(f"RAM Advantage achieved: {result['_meta']['ram_advantage_pct']}%")
        print(f"Result Preview (Metadata): {json.dumps(result['_meta'], indent=2)}")
    except RuntimeError as e:
        print(e)