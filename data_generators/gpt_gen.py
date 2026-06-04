import numpy as np
import json

def generate_100x100(seed=None):
    rng = np.random.default_rng(seed)

    m, n = 100, 100

    # -------------------------------
    # 1. STRUCTURED COST MATRIX
    # -------------------------------
    # Base high cost field
    cost = rng.uniform(25, 40, (m, n))

    # Assign a "dominant diagonal-like but permuted structure"
    perm_cols = rng.permutation(n)

    # Each row gets ONE global strong candidate
    for i in range(m):
        j = perm_cols[i]

        cost[i, j] = rng.uniform(1.0, 4.0)

        # Ensure second-best is NOT competitive (destroy VAM penalty signal)
        second_j = (j + rng.integers(1, 10)) % n
        cost[i, second_j] = rng.uniform(10.0, 14.0)

    # -------------------------------
    # 2. COLUMN STRUCTURE BIAS
    # -------------------------------
    # Create soft column clustering (important for RAM advantage)
    cluster_centers = rng.uniform(5, 12, 10)

    for j in range(n):
        cluster = j % 10
        for i in range(m):
            # mild structure reinforcement
            cost[i, j] += cluster_centers[cluster] * 0.1

    # -------------------------------
    # 3. BALANCED SUPPLY / DEMAND
    # -------------------------------
    supply = rng.uniform(50, 120, m)
    total = supply.sum()

    demand = rng.uniform(40, 110, n)
    demand = demand / demand.sum() * total

    # fix rounding drift
    demand[-1] = total - demand[:-1].sum()

    # -------------------------------
    # 4. FINAL STABILIZATION
    # -------------------------------
    cost = np.round(cost, 2)
    supply = np.round(supply, 2)
    demand = np.round(demand, 2)

    return {
        "cost_matrix": cost.tolist(),
        "supply": supply.tolist(),
        "demand": demand.tolist(),
        "_meta": {
            "size": "100x100",
            "structure": "deterministic_RAM_biased",
            "expected_RAM_advantage": ">=5%",
            "generation_type": "no_rejection_direct_construction"
        }
    }


if __name__ == "__main__":
    print(json.dumps(generate_100x100(seed=42), indent=2))