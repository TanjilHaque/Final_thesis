import numpy as np
import json

def generate_parity_problem(seed=None):
    """
    Generates a balanced Transportation Problem where
    Vogel (VAM) and Russell's Approximation produce near-identical costs.

    Design principle: flat, diffuse cost landscape — penalties are small
    and uniformly distributed, eliminating VAM's sharp-penalty advantage.
    """
    rng = np.random.default_rng(seed)

    m, n = 90, 90

    # Flat uniform cost field: narrow range, small noise → low penalty variance
    # VAM advantage collapses when all penalties are similar
    base = rng.uniform(15, 38, (m, n))
    noise = rng.uniform(-3.0, 3.0, (m, n))
    cost = np.round(base + noise, 2)
    # Clip to avoid negative costs
    cost = np.clip(cost, 1.0, None)

    # Balanced supply / demand
    supply = rng.uniform(40, 100, m)
    total = supply.sum()

    demand = rng.uniform(30, 90, n)
    demand = demand / demand.sum() * total

    # Fix rounding drift to enforce exact balance
    demand[-1] = total - demand[:-1].sum()

    cost = np.round(cost, 2)
    supply = np.round(supply, 2)
    demand = np.round(demand, 2)

    return {
        "cost_matrix": cost.tolist(),
        "supply": supply.tolist(),
        "demand": demand.tolist(),
        "_meta": {
            "size": f"{m}x{n}",
            "balanced": True,
            "structure": "flat_diffuse_parity",
            "design": "low penalty variance -> VAM and Russell converge",
            "seed": 42
        }
    }

if __name__ == "__main__":
    problem = generate_parity_problem(seed=42)
    print(json.dumps(problem, indent=2))
