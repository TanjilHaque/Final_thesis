"""
================================================================================
IT2-TFS FUZZIFICATION SYSTEM
Research-Grade Interval Type-2 Trapezoidal Fuzzy Fuzzifier
for Transportation Problem Datasets
================================================================================

THEORETICAL FRAMEWORK
─────────────────────
Three strictly separated uncertainty dimensions:

  A. GEOMETRIC UNCERTAINTY  → UMF only (δ, α, β, γ)
  B. EPISTEMIC UNCERTAINTY  → LMF only (reliability r)
  C. CONFIDENCE             → Height hL only (variability v)

These dimensions NEVER influence each other.

REFERENCES
──────────
[1] Mendel, J.M. (2001). Uncertain Rule-Based Fuzzy Systems.
[2] Karnik, N.N. & Mendel, J.M. (2001). Centroid of a type-2 fuzzy set.
    Information Sciences, 132(1-4), 195–220.
[3] John, R.I. & Coupland, S. (2007). Type-2 Fuzzy Logic: A Historical View.
    IEEE Computational Intelligence Magazine.
================================================================================
"""

import json
import math
import numpy as np
from typing import Any


# ================================================================================
# LAYER 1 — INPUT VALIDATION
# ================================================================================

class InputValidator:
    """
    Validates the JSON input structure before any computation begins.

    Rules enforced:
      - Required keys present: cost_matrix, supply, demand
      - cost_matrix is rectangular (all rows same length)
      - supply length == number of rows in cost_matrix
      - demand length == number of columns in cost_matrix
      - All values strictly positive (cost matrix, supply, demand)
    """

    @staticmethod
    def validate(data: dict) -> None:
        required = {"cost_matrix", "supply", "demand"}
        missing = required - data.keys()
        if missing:
            raise ValueError(f"[Validation] Missing keys: {missing}")

        cost = data["cost_matrix"]
        supply = data["supply"]
        demand = data["demand"]

        if not isinstance(cost, (list, np.ndarray)) or len(cost) == 0:
            raise ValueError("[Validation] cost_matrix must be a non-empty 2D array.")

        n_rows = len(cost)
        n_cols = len(cost[0])

        for i, row in enumerate(cost):
            if len(row) != n_cols:
                raise ValueError(
                    f"[Validation] cost_matrix row {i} has {len(row)} elements; "
                    f"expected {n_cols}. Matrix must be rectangular."
                )

        if len(supply) != n_rows:
            raise ValueError(
                f"[Validation] supply length {len(supply)} != "
                f"cost_matrix rows {n_rows}."
            )

        if len(demand) != n_cols:
            raise ValueError(
                f"[Validation] demand length {len(demand)} != "
                f"cost_matrix columns {n_cols}."
            )

        flat_cost = np.array(cost, dtype=float).flatten()
        flat_supply = np.array(supply, dtype=float)
        flat_demand = np.array(demand, dtype=float)

        if np.any(flat_cost <= 0):
            raise ValueError("[Validation] All cost_matrix values must be > 0.")
        if np.any(flat_supply <= 0):
            raise ValueError("[Validation] All supply values must be > 0.")
        if np.any(flat_demand <= 0):
            raise ValueError("[Validation] All demand values must be > 0.")


# ================================================================================
# LAYER 2 — STATISTICAL LAYER
# ================================================================================

class StatisticsEngine:
    """
    Computes all global and local statistics required by downstream layers.

    Attributes populated after calling `fit`:
      gmin, gmax, gmean, gstd  — global scalar statistics over cost matrix
      row_var                   — per-row variance (shape: m,)
      col_var                   — per-column variance (shape: n,)
      cost_min, cost_max        — for normalization within cost cells
    """

    def __init__(self, eps: float = 1e-9):
        self.eps = eps
        self.gmin: float = None
        self.gmax: float = None
        self.gmean: float = None
        self.gstd: float = None
        self.row_std: np.ndarray = None
        self.col_std: np.ndarray = None
        self.cost_min: float = None
        self.cost_max: float = None

    def fit(self, cost_matrix: np.ndarray) -> None:
        flat = cost_matrix.flatten()

        self.gmin = float(np.min(flat))
        self.gmax = float(np.max(flat))
        self.gmean = float(np.mean(flat))
        self.gstd = float(np.std(flat))

        # Row and column standard deviations (ddof=0, population)
        self.row_std = np.std(cost_matrix, axis=1)   # shape (m,)
        self.col_std = np.std(cost_matrix, axis=0)   # shape (n,)

        self.cost_min = self.gmin
        self.cost_max = self.gmax

    def as_dict(self) -> dict:
        return {
            "global_min": round(self.gmin, 8),
            "global_max": round(self.gmax, 8),
            "global_mean": round(self.gmean, 8),
            "global_std": round(self.gstd, 8),
        }


# ================================================================================
# LAYER 3 — UNCERTAINTY (VARIABILITY) LAYER
# ================================================================================

class VariabilityEngine:
    """
    Computes deterministic, normalized variability scores.

    COST MATRIX FORMULA (Specification §4.1):
        v_ij = (2·σ_row(i) + σ_col(j)) / (σ_global + ε)

    The 2:1 weighting gives row variance higher influence, reflecting that
    within a transportation row (a single origin), cost spread is more
    structurally informative than column spread.

    VECTOR FORMULA (supply / demand):
        v_k = σ_vector / (σ_global + ε)

    All outputs clamped to [0, 1].
    """

    def __init__(self, stats: StatisticsEngine):
        self.stats = stats

    def cost_matrix_variability(self, m: int, n: int) -> np.ndarray:
        """
        Returns variability matrix V of shape (m, n).

        V[i,j] = clip( (2*σ_row[i] + σ_col[j]) / (σ_global + ε), 0, 1 )
        """
        # Broadcast: (m,1) + (1,n) → (m,n)
        raw = (
            2.0 * self.stats.row_std[:, np.newaxis]
            + self.stats.col_std[np.newaxis, :]
        ) / (self.stats.gstd + self.stats.eps)

        return np.clip(raw, 0.0, 1.0)

    def vector_variability(self, vec: np.ndarray) -> np.ndarray:
        """
        Returns variability array for a 1D supply or demand vector.

        Each element receives the same variability derived from the
        vector's own standard deviation, normalised by global std.
        """
        local_std = float(np.std(vec))
        v_scalar = local_std / (self.stats.gstd + self.stats.eps)
        v_scalar = float(np.clip(v_scalar, 0.0, 1.0))
        # All elements of a vector share the same variability
        return np.full(len(vec), v_scalar)


# ================================================================================
# LAYER 4 — RELIABILITY LAYER
# ================================================================================

class ReliabilityEngine:
    """
    Computes deterministic reliability scores r ∈ [0.3, 0.9].

    Three separate formulas (Specification §5.1):

      Cost:    S = 0.65·e^(−v) + 0.35·(1 − x_norm)
      Supply:  S = 0.70·e^(−v) + 0.30·x_norm
      Demand:  S = 0.55·e^(−v) + 0.45·x_norm

    r = clip(0.3 + 0.6·S, 0.3, 0.9)

    x_norm is always computed against the global cost min/max
    for a unified reference frame.
    """

    def __init__(self, stats: StatisticsEngine):
        self.stats = stats

    def _x_norm(self, x: np.ndarray) -> np.ndarray:
        return (x - self.stats.cost_min) / (
            self.stats.cost_max - self.stats.cost_min + self.stats.eps
        )

    def cost(self, X: np.ndarray, V: np.ndarray) -> np.ndarray:
        """
        Vectorized reliability for the full cost matrix.

        Parameters
        ----------
        X : (m, n) crisp cost values
        V : (m, n) normalized variability

        Returns
        -------
        R : (m, n) reliability scores
        """
        x_norm = self._x_norm(X)
        S = 0.65 * np.exp(-V) + 0.35 * (1.0 - x_norm)
        return np.clip(0.3 + 0.6 * S, 0.3, 0.9)

    def supply(self, x_vec: np.ndarray, v_vec: np.ndarray) -> np.ndarray:
        x_norm = self._x_norm(x_vec)
        S = 0.70 * np.exp(-v_vec) + 0.30 * x_norm
        return np.clip(0.3 + 0.6 * S, 0.3, 0.9)

    def demand(self, x_vec: np.ndarray, v_vec: np.ndarray) -> np.ndarray:
        x_norm = self._x_norm(x_vec)
        S = 0.55 * np.exp(-v_vec) + 0.45 * x_norm
        return np.clip(0.3 + 0.6 * S, 0.3, 0.9)


# ================================================================================
# LAYER 5 — UMF CONSTRUCTION LAYER (Geometric Uncertainty)
# ================================================================================

class UMFBuilder:
    """
    Builds the Upper Membership Function (UMF) trapezoid.

    The UMF encodes ONLY geometric uncertainty — the support width
    of the IT2 fuzzy number. It is parameterised exclusively by
    δ (base spread) and the asymmetry coefficients α, β, γ.

    Formula (Specification §3.1):
        a1 = x(1 − δ)
        a2 = x(1 − αδ)
        a3 = x(1 + βδ)
        a4 = x(1 + γδ)
        height = 1.0 (UMF always has full height)

    Asymmetry:
        α < 1  → inner left shoulder closer to core
        β < 1  → inner right shoulder closer to core
        γ > 1  → outer right boundary wider than outer left

    This asymmetry captures the realistic observation that cost
    over-estimation is typically bounded while under-estimation
    can extend further.
    """

    def __init__(self, delta: float, alpha: float, beta: float, gamma: float):
        self.d = delta
        self.a = alpha
        self.b = beta
        self.g = gamma

    def build(self, X: np.ndarray) -> np.ndarray:
        """
        Vectorized UMF construction.

        Parameters
        ----------
        X : array of any shape — crisp input values

        Returns
        -------
        umf : shape (*X.shape, 5) — [a1, a2, a3, a4, 1.0]
        """
        a1 = X * (1.0 - self.d)
        a2 = X * (1.0 - self.a * self.d)
        a3 = X * (1.0 + self.b * self.d)
        a4 = X * (1.0 + self.g * self.d)
        h  = np.ones_like(X)

        return np.stack([a1, a2, a3, a4, h], axis=-1)


# ================================================================================
# LAYER 6 — LMF CONSTRUCTION LAYER (Epistemic Uncertainty)
# ================================================================================

class LMFBuilder:
    """
    Builds the Lower Membership Function (LMF) trapezoid.

    The LMF encodes ONLY epistemic (knowledge) uncertainty.
    It contracts toward the crisp value as reliability r → 1.

    Formula (Specification §3.2):
        b1 = x(1 − r·δ)
        b2 = x(1 − r·α·δ)
        b3 = x(1 + r·β·δ)
        b4 = x(1 + r·γ·δ)

    Note: The LMF height hL is NOT computed here.
    Height is computed independently by the HeightEngine (Layer 7)
    and attached to the LMF array at the Output layer.
    This enforces strict separation of concerns.
    """

    def __init__(self, delta: float, alpha: float, beta: float, gamma: float):
        self.d = delta
        self.a = alpha
        self.b = beta
        self.g = gamma

    def build(self, X: np.ndarray, R: np.ndarray) -> np.ndarray:
        """
        Vectorized LMF construction.

        Parameters
        ----------
        X : array of crisp values
        R : array of reliability scores (same shape as X)

        Returns
        -------
        lmf_no_height : shape (*X.shape, 4) — [b1, b2, b3, b4]
                        Height is NOT included here; appended at output.
        """
        b1 = X * (1.0 - R * self.d)
        b2 = X * (1.0 - R * self.a * self.d)
        b3 = X * (1.0 + R * self.b * self.d)
        b4 = X * (1.0 + R * self.g * self.d)

        return np.stack([b1, b2, b3, b4], axis=-1)


# ================================================================================
# LAYER 7 — HEIGHT LAYER (Confidence)
# ================================================================================

class HeightEngine:
    """
    Computes the LMF height hL — a pure confidence scalar.

    Formula (Specification §3.3):
        hL = hmin + (1 − v)(hmax − hmin)

    Interpretation:
      v → 0  (low variability / stable data)  → hL → hmax (high confidence)
      v → 1  (high variability / noisy data)  → hL → hmin (low confidence)

    hL ∈ [hmin, hmax] ⊂ (0, 1)

    CRITICAL: height is NOT part of the trapezoidal geometry.
    It is a secondary-grade scalar that scales the membership
    surface of the LMF independently of b1…b4.
    """

    def __init__(self, h_min: float = 0.4, h_max: float = 0.95):
        self.h_min = h_min
        self.h_max = h_max

    def compute(self, V: np.ndarray) -> np.ndarray:
        """
        Vectorized height computation.

        Parameters
        ----------
        V : variability array (any shape), values in [0, 1]

        Returns
        -------
        H : height array (same shape as V), values in [hmin, hmax]
        """
        return np.clip(
            self.h_min + (1.0 - V) * (self.h_max - self.h_min),
            self.h_min,
            self.h_max
        )


# ================================================================================
# LAYER 8 — VALIDATION LAYER
# ================================================================================

class StructuralValidator:
    """
    Enforces nesting constraints on every IT2FS object.

    NESTING REQUIREMENT (Specification §6.1):
        a1 ≤ b1 ≤ b2 ≤ b3 ≤ b4 ≤ a4

    If violated, a DETERMINISTIC clamp-based correction is applied:
      - b1 is raised to max(b1, a1)
      - b4 is lowered to min(b4, a4)
      - b2 is clamped between b1 and b3
      - b3 is clamped between b2 and b4

    No randomness. No structure is discarded.
    The correction is logged (count only) for reproducibility auditing.
    """

    def __init__(self):
        self.correction_count = 0

    def enforce(
        self,
        umf_coords: np.ndarray,   # shape (..., 4)  [a1,a2,a3,a4]
        lmf_coords: np.ndarray,   # shape (..., 4)  [b1,b2,b3,b4]
    ) -> np.ndarray:
        """
        Returns corrected lmf_coords (same shape).
        umf_coords is read-only; UMF is always valid by construction.
        """
        a1 = umf_coords[..., 0]
        a4 = umf_coords[..., 3]

        b1 = lmf_coords[..., 0].copy()
        b2 = lmf_coords[..., 1].copy()
        b3 = lmf_coords[..., 2].copy()
        b4 = lmf_coords[..., 3].copy()

        # Step 1: outer boundaries
        b1 = np.maximum(b1, a1)
        b4 = np.minimum(b4, a4)

        # Step 2: inner monotonicity
        b2 = np.clip(b2, b1, b4)
        b3 = np.clip(b3, b2, b4)

        # Detect corrections (any element changed)
        corrected = (
            np.any(b1 != lmf_coords[..., 0])
            or np.any(b4 != lmf_coords[..., 3])
            or np.any(b2 != lmf_coords[..., 1])
            or np.any(b3 != lmf_coords[..., 2])
        )
        if corrected:
            self.correction_count += 1

        return np.stack([b1, b2, b3, b4], axis=-1)

    def validate_monotonicity(self, lmf: np.ndarray, umf: np.ndarray) -> bool:
        """Full post-correction check. Returns True if all constraints pass."""
        a1, a4 = umf[..., 0], umf[..., 3]
        b1, b2, b3, b4 = lmf[..., 0], lmf[..., 1], lmf[..., 2], lmf[..., 3]

        return bool(
            np.all(a1 <= b1)
            and np.all(b1 <= b2)
            and np.all(b2 <= b3)
            and np.all(b3 <= b4)
            and np.all(b4 <= a4)
        )


# ================================================================================
# LAYER 9 — OUTPUT SERIALIZER
# ================================================================================

class OutputSerializer:
    """
    Converts NumPy arrays into strict JSON-serializable IT2FS objects.

    Each output object:
        {
            "umf": [a1, a2, a3, a4, 1.0],    ← 5 elements, height always 1.0
            "lmf": [b1, b2, b3, b4, hL]       ← 5 elements, height = confidence
        }

    All floats rounded to 6 decimal places for readability.
    """

    @staticmethod
    def _r6(x: float) -> float:
        return round(float(x), 2)

    def build_it2fs(
        self,
        umf_row: np.ndarray,   # [a1,a2,a3,a4,1.0]  shape (5,)
        lmf_row: np.ndarray,   # [b1,b2,b3,b4]       shape (4,)
        h: float
    ) -> dict:
        return {
            "umf": [self._r6(v) for v in umf_row],
            "lmf": [self._r6(v) for v in lmf_row] + [self._r6(h)]
        }

    def serialize_matrix(
        self,
        umf_arr: np.ndarray,   # (m, n, 5)
        lmf_arr: np.ndarray,   # (m, n, 4)
        H: np.ndarray          # (m, n)
    ) -> list:
        m, n = H.shape
        return [
            [
                self.build_it2fs(umf_arr[i, j], lmf_arr[i, j], H[i, j])
                for j in range(n)
            ]
            for i in range(m)
        ]

    def serialize_vector(
        self,
        umf_arr: np.ndarray,   # (k, 5)
        lmf_arr: np.ndarray,   # (k, 4)
        H: np.ndarray          # (k,)
    ) -> list:
        return [
            self.build_it2fs(umf_arr[k], lmf_arr[k], H[k])
            for k in range(len(H))
        ]


# ================================================================================
# MAIN PIPELINE — IT2TFSFuzzifier
# ================================================================================

class IT2TFSFuzzifier:
    """
    Research-Grade Interval Type-2 Trapezoidal Fuzzy Fuzzifier.

    Transforms a crisp transportation problem dataset into a full
    IT2-TFS representation with strict theoretical separation of:

        DIMENSION A  →  Geometric uncertainty (UMF, δ/α/β/γ)
        DIMENSION B  →  Epistemic uncertainty (LMF, reliability r)
        DIMENSION C  →  Confidence           (Height hL, variability v)

    Parameters
    ----------
    delta   : base spread parameter δ ∈ (0, 1)
    alpha   : left inner asymmetry coefficient α
    beta    : right inner asymmetry coefficient β
    gamma   : right outer asymmetry coefficient γ
    h_min   : minimum LMF height (confidence floor)
    h_max   : maximum LMF height (confidence ceiling)
    eps     : numerical stability constant

    Usage
    -----
    >>> fuzz = IT2TFSFuzzifier()
    >>> result = fuzz.transform(data)
    >>> fuzz.export(result, "output.json")
    """

    def __init__(
        self,
        delta: float = 0.15,
        alpha: float = 0.45,
        beta: float  = 0.75,
        gamma: float = 1.15,
        h_min: float = 0.40,
        h_max: float = 0.95,
        eps: float   = 1e-9,
    ):
        self.delta = delta
        self.alpha = alpha
        self.beta  = beta
        self.gamma = gamma
        self.h_min = h_min
        self.h_max = h_max
        self.eps   = eps

        # Instantiate all layers
        self._validator   = InputValidator()
        self._stats       = StatisticsEngine(eps=eps)
        self._height      = HeightEngine(h_min=h_min, h_max=h_max)
        self._struct      = StructuralValidator()
        self._serializer  = OutputSerializer()

        # UMF and LMF builders share the same geometric parameters
        self._umf_builder = UMFBuilder(delta, alpha, beta, gamma)
        self._lmf_builder = LMFBuilder(delta, alpha, beta, gamma)

    # ──────────────────────────────────────────────────────────────
    # PUBLIC API
    # ──────────────────────────────────────────────────────────────

    def transform(self, data: dict) -> dict:
        """
        Full pipeline entry point.

        Steps:
            1. Validate input
            2. Fit global statistics on cost matrix
            3. Compute variability
            4. Compute reliability (type-specific)
            5. Build UMF (geometry)
            6. Build LMF (epistemic)
            7. Compute height (confidence)
            8. Enforce structural constraints
            9. Serialize to JSON-ready dict
        """

        # ── Step 1: Validation ────────────────────────────────────
        self._validator.validate(data)

        C = np.array(data["cost_matrix"], dtype=float)   # (m, n)
        S = np.array(data["supply"],      dtype=float)   # (m,)
        D = np.array(data["demand"],      dtype=float)   # (n,)
        m, n = C.shape

        # ── Step 2: Global statistics ─────────────────────────────
        self._stats.fit(C)

        # ── Step 3: Instantiate context-dependent engines ─────────
        var_engine = VariabilityEngine(self._stats)
        rel_engine = ReliabilityEngine(self._stats)

        # ── Step 4a: Cost matrix pipeline ─────────────────────────
        V_cost = var_engine.cost_matrix_variability(m, n)       # (m,n)
        R_cost = rel_engine.cost(C, V_cost)                     # (m,n)

        umf_cost = self._umf_builder.build(C)                   # (m,n,5)
        lmf_cost_coords = self._lmf_builder.build(C, R_cost)    # (m,n,4)
        lmf_cost_coords = self._struct.enforce(
            umf_cost[..., :4], lmf_cost_coords
        )
        H_cost = self._height.compute(V_cost)                   # (m,n)

        # ── Step 4b: Supply vector pipeline ───────────────────────
        V_sup = var_engine.vector_variability(S)                # (m,)
        R_sup = rel_engine.supply(S, V_sup)                     # (m,)

        umf_sup = self._umf_builder.build(S)                    # (m,5)
        lmf_sup_coords = self._lmf_builder.build(S, R_sup)      # (m,4)
        lmf_sup_coords = self._struct.enforce(
            umf_sup[..., :4], lmf_sup_coords
        )
        H_sup = self._height.compute(V_sup)                     # (m,)

        # ── Step 4c: Demand vector pipeline ───────────────────────
        V_dem = var_engine.vector_variability(D)                # (n,)
        R_dem = rel_engine.demand(D, V_dem)                     # (n,)

        umf_dem = self._umf_builder.build(D)                    # (n,5)
        lmf_dem_coords = self._lmf_builder.build(D, R_dem)      # (n,4)
        lmf_dem_coords = self._struct.enforce(
            umf_dem[..., :4], lmf_dem_coords
        )
        H_dem = self._height.compute(V_dem)                     # (n,)

        # ── Step 5: Post-correction structural audit ───────────────
        assert self._struct.validate_monotonicity(
            lmf_cost_coords, umf_cost[..., :4]
        ), "[Structural] Cost matrix nesting constraint violated post-correction."
        assert self._struct.validate_monotonicity(
            lmf_sup_coords, umf_sup[..., :4]
        ), "[Structural] Supply nesting constraint violated post-correction."
        assert self._struct.validate_monotonicity(
            lmf_dem_coords, umf_dem[..., :4]
        ), "[Structural] Demand nesting constraint violated post-correction."

        # ── Step 6: Serialize ─────────────────────────────────────
        return {
            "metadata": {
                "delta":      self.delta,
                "alpha":      self.alpha,
                "beta":       self.beta,
                "gamma":      self.gamma,
                "h_min":      self.h_min,
                "h_max":      self.h_max,
                "corrections_applied": self._struct.correction_count,
                "statistics": self._stats.as_dict(),
            },
            "cost_matrix": self._serializer.serialize_matrix(
                umf_cost, lmf_cost_coords, H_cost
            ),
            "supply": self._serializer.serialize_vector(
                umf_sup, lmf_sup_coords, H_sup
            ),
            "demand": self._serializer.serialize_vector(
                umf_dem, lmf_dem_coords, H_dem
            ),
        }

    def export(self, result: dict, path: str = "it2_output.json") -> None:
        """Writes the result dict to a JSON file."""
        with open(path, "w") as f:
            json.dump(result, f, indent=4)
        print(f"[Export] Written to: {path}")


# ================================================================================
# ENTRY POINT — EXAMPLE USAGE
# ================================================================================

if __name__ == "__main__":

    # ── Benchmark dataset (small, verifiable by hand) ─────────────
#     data = {
#   "cost_matrix": [
#     [2.32, 5.19, 7.25, 6.5],
#     [2.13, 5.19, 8.12, 2.13],
#     [2.32, 6.5, 9.3, 2.13]
#   ],
#   "supply": [5.41, 8.01, 2.59],
#   "demand": [2.19, 2.19, 5.13, 6.5]
# }
    with open("crisp_data/problem_200x200_crisp.json", "r") as f:
        data = json.load(f)

    model = IT2TFSFuzzifier(
        delta=0.15,
        alpha=0.45,
        beta=0.75,
        gamma=1.15,
        h_min=0.40,
        h_max=0.95,
    )

    result = model.transform(data)

    model.export(result, "fuzzy_data/fuzzy_test_data/problem_200x200_fuzzy.json")

    # ── Spot-check: print first cost cell ─────────────────────────
    cell = result["cost_matrix"][0][0]
    print("\nSample IT2FS [cost_matrix[0][0]]:")
    print(f"  UMF: {cell['umf']}")
    print(f"  LMF: {cell['lmf']}")

    # ── Verify nesting a1 ≤ b1, b4 ≤ a4 ─────────────────────────
    a1, a4 = cell["umf"][0], cell["umf"][3]
    b1, b4 = cell["lmf"][0], cell["lmf"][3]
    print(f"\nNesting check: {a1} ≤ {b1} and {b4} ≤ {a4}")
    print(f"  → {'PASS ✓' if a1 <= b1 and b4 <= a4 else 'FAIL ✗'}")

    # ── Metadata ──────────────────────────────────────────────────
    print("\nMetadata:")
    print(json.dumps(result["metadata"], indent=4))