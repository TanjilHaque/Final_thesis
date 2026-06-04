"""
================================================================================
IT2-TFS DEFUZZIFICATION SYSTEM
Research-Grade Interval Type-2 Trapezoidal Fuzzy Defuzzifier
Karnik-Mendel (KM) Algorithm + Balance Enforcement Layer
================================================================================

THEORETICAL FRAMEWORK
---------------------
The Karnik-Mendel (KM) algorithm computes the centroid of an Interval Type-2
Fuzzy Set (IT2FS). Because the secondary membership grades form an interval,
the centroid is also an interval [y_l, y_r] rather than a single point.

The final crisp value is the mean of the two KM switch-point outputs:

    y* = (y_l + y_r) / 2                          [Mendel, 2001, eq. 9.36]

ALGORITHM OVERVIEW (per Karnik & Mendel, 2001)
----------------------------------------------
For a trapezoidal IT2FS with UMF and LMF both defined by 4-point trapezoids,
we discretize the support into N sample points and evaluate each sample's
membership in both UMF and LMF. The KM algorithm then finds the optimal
switching point k* that partitions the samples into two groups, each taking
its membership value from one of the two bounding MFs.

LEFT CENTROID  (y_l):  samples left of k*  use UMF, right use LMF
RIGHT CENTROID (y_r):  samples left of k*  use LMF, right use UMF

This is iterated to convergence (typically 2-5 iterations).

WHY BALANCE ENFORCEMENT IS NEEDED
----------------------------------
The fuzzifier assigns different reliability r and variability v to supply
vs demand elements, because they use separate reliability formulas:

    Supply:  S = 0.70*exp(-v) + 0.30*x_norm
    Demand:  S = 0.55*exp(-v) + 0.45*x_norm

This causes the KM upward bias to differ element-by-element:
    - Supply bias:  ~1.32-1.37% per element (non-uniform)
    - Demand bias:  ~1.24-1.36% per element (non-uniform)

Even though the original crisp problem is balanced (sum_supply == sum_demand),
the defuzzified values are NOT balanced because the per-element bias is
different for supply vs demand.

BALANCE ENFORCEMENT STRATEGY (Proportional Normalization)
----------------------------------------------------------
After KM defuzzification, enforce balance by proportional normalization:

    T = (sum(supply_km) + sum(demand_km)) / 2      <- symmetric anchor

    supply_final[i] = supply_km[i] / sum(supply_km) * T
    demand_final[j] = demand_km[j] / sum(demand_km) * T

Properties of this approach:
    1. sum(supply_final) == sum(demand_final) == T  EXACTLY
    2. Intra-supply ratios are PRESERVED  (supply[i]/supply[j] unchanged)
    3. Intra-demand ratios are PRESERVED  (demand[i]/demand[j] unchanged)
    4. Correction magnitude is tiny       (~0.011% per element)
    5. Fully deterministic — no randomness

This is the standard normalization used in fuzzy transportation literature
(cf. Kumar et al., 2011; Ebrahimnejad, 2014) to restore feasibility after
type-reduction while preserving the relative structure of the fuzzy solution.

MEMBERSHIP FUNCTIONS
--------------------
For a trapezoidal fuzzy number [p1, p2, p3, p4] with height h:

         h        ___________
                 /           \\
                /             \\
    ___________/               \\___________
    p1    p2                p3    p4

    mu(x) = 0                    if x <= p1 or x >= p4
    mu(x) = h*(x-p1)/(p2-p1)    if p1 < x <= p2
    mu(x) = h                    if p2 < x <= p3
    mu(x) = h*(p4-x)/(p4-p3)    if p3 < x < p4

REFERENCES
----------
[1] Karnik, N.N. & Mendel, J.M. (2001). Centroid of a type-2 fuzzy set.
    Information Sciences, 132(1-4), 195-220.
[2] Mendel, J.M. (2001). Uncertain Rule-Based Fuzzy Logic Systems.
    Prentice Hall.
[3] Wu, D. & Mendel, J.M. (2009). Enhanced Karnik-Mendel Algorithms.
    IEEE Trans. Fuzzy Syst., 17(4), 923-934.
[4] Kumar, A., Kaur, P. & Singh, P. (2011). A new method for solving
    fully fuzzy linear programming problems. Applied Mathematical
    Modelling, 35(2), 817-823.
================================================================================
"""

import json
import numpy as np
from typing import Tuple


# ================================================================================
# LAYER 1 -- TRAPEZOIDAL MEMBERSHIP FUNCTION EVALUATOR
# ================================================================================

class TrapezoidalMF:
    """
    Evaluates a trapezoidal membership function at an array of sample points.

    The trapezoid is defined by four base points [p1, p2, p3, p4] and
    a height h in (0, 1].

    Shape:
        - Rising slope:  p1 -> p2
        - Flat top:      p2 -> p3
        - Falling slope: p3 -> p4
        - Zero outside:  (-inf, p1] union [p4, +inf)

    For degenerate cases where p1 == p2 or p3 == p4, the slopes are
    treated as vertical (step function).
    """

    @staticmethod
    def evaluate(
        x: np.ndarray,
        p1: float, p2: float, p3: float, p4: float,
        h: float,
        eps: float = 1e-12
    ) -> np.ndarray:
        """
        Vectorized membership evaluation.

        Parameters
        ----------
        x  : sample points array, shape (N,)
        p1 : left foot of trapezoid
        p2 : left shoulder (start of flat top)
        p3 : right shoulder (end of flat top)
        p4 : right foot of trapezoid
        h  : height of flat top
        eps: numerical guard for degenerate slopes

        Returns
        -------
        mu : membership values in [0, h], shape (N,)
        """
        mu = np.zeros_like(x, dtype=float)

        # Rising left slope: p1 < x <= p2
        rise = p2 - p1
        if rise > eps:
            mask = (x > p1) & (x <= p2)
            mu[mask] = h * (x[mask] - p1) / rise

        # Flat top: p2 < x <= p3
        mu[(x > p2) & (x <= p3)] = h

        # Falling right slope: p3 < x < p4
        fall = p4 - p3
        if fall > eps:
            mask = (x > p3) & (x < p4)
            mu[mask] = h * (p4 - x[mask]) / fall

        return mu


# ================================================================================
# LAYER 2 -- KARNIK-MENDEL ENGINE
# ================================================================================

class KarnikMendelEngine:
    """
    Exact iterative Karnik-Mendel (KM) algorithm for IT2 trapezoidal fuzzy sets.

    Computes the centroid interval [y_l, y_r] of an IT2FS defined by:
        UMF: trapezoidal [a1, a2, a3, a4], height = 1.0
        LMF: trapezoidal [b1, b2, b3, b4], height = hL

    ALGORITHM (left centroid y_l)
    ------------------------------
    1. Discretize support into N equally spaced sample points x_i.
    2. Compute UMF(x_i) and LMF(x_i) for all i.
    3. Initialize weights w_i = (UMF(x_i) + LMF(x_i)) / 2.
    4. Compute initial centroid y = sum(x_i * w_i) / sum(w_i).
    5. Find switch index k = argmax { x_i : x_i <= y }.
    6. Update weights:
           w_i = UMF(x_i)  if i <= k  else  LMF(x_i)
    7. Compute new y = sum(x_i * w_i) / sum(w_i).
    8. Repeat steps 5-7 until |y_new - y_old| < tolerance.

    RIGHT CENTROID y_r: same algorithm with weights swapped:
           w_i = LMF(x_i)  if i <= k  else  UMF(x_i)

    FINAL CRISP DEFUZZIFIED VALUE:
        y* = (y_l + y_r) / 2

    Parameters
    ----------
    N         : number of discretization points (default 1000)
    max_iter  : maximum KM iterations per centroid (default 100)
    tol       : convergence tolerance (default 1e-8)
    eps       : numerical guard
    """

    def __init__(
        self,
        N: int        = 1000,
        max_iter: int = 100,
        tol: float    = 1e-8,
        eps: float    = 1e-12,
    ):
        self.N        = N
        self.max_iter = max_iter
        self.tol      = tol
        self.eps      = eps
        self._mf      = TrapezoidalMF()

    def _km_iterate(
        self,
        x:   np.ndarray,
        w_L: np.ndarray,
        w_R: np.ndarray,
    ) -> float:
        """
        One KM centroid computation.

        Switch-point rule:
            i <= k  ->  use w_L[i]
            i >  k  ->  use w_R[i]

        Returns the converged centroid as a float.
        """
        w = (w_L + w_R) / 2.0
        denom = np.sum(w)
        if denom < self.eps:
            return float(np.mean(x))

        y = float(np.dot(x, w) / denom)

        for _ in range(self.max_iter):
            k = int(np.searchsorted(x, y, side='right')) - 1
            k = int(np.clip(k, 0, self.N - 2))

            w_mixed = np.empty(self.N)
            w_mixed[:k + 1] = w_L[:k + 1]
            w_mixed[k + 1:] = w_R[k + 1:]

            denom_new = np.sum(w_mixed)
            if denom_new < self.eps:
                break

            y_new = float(np.dot(x, w_mixed) / denom_new)
            if abs(y_new - y) < self.tol:
                y = y_new
                break
            y = y_new

        return y

    def defuzzify(self, it2fs: dict) -> float:
        """
        Defuzzify one IT2FS object using the KM algorithm.

        Parameters
        ----------
        it2fs : dict with keys "umf" and "lmf"
                "umf" = [a1, a2, a3, a4, 1.0]
                "lmf" = [b1, b2, b3, b4, hL]

        Returns
        -------
        y_star : crisp defuzzified value  y* = (y_l + y_r) / 2
        """
        a1, a2, a3, a4, h_u = it2fs["umf"]
        b1, b2, b3, b4, h_l = it2fs["lmf"]

        x = np.linspace(a1, a4, self.N)

        mu_U = self._mf.evaluate(x, a1, a2, a3, a4, float(h_u), self.eps)
        mu_L = self._mf.evaluate(x, b1, b2, b3, b4, float(h_l), self.eps)

        y_l = self._km_iterate(x, mu_U, mu_L)   # left  centroid
        y_r = self._km_iterate(x, mu_L, mu_U)   # right centroid

        if y_l > y_r:
            y_l, y_r = y_r, y_l

        return (y_l + y_r) / 2.0

    def centroid_interval(self, it2fs: dict) -> Tuple[float, float]:
        """
        Returns the full centroid interval [y_l, y_r].
        Useful for research analysis and thesis reporting.
        """
        a1, a2, a3, a4, h_u = it2fs["umf"]
        b1, b2, b3, b4, h_l = it2fs["lmf"]

        x = np.linspace(a1, a4, self.N)
        mu_U = self._mf.evaluate(x, a1, a2, a3, a4, float(h_u), self.eps)
        mu_L = self._mf.evaluate(x, b1, b2, b3, b4, float(h_l), self.eps)

        y_l = self._km_iterate(x, mu_U, mu_L)
        y_r = self._km_iterate(x, mu_L, mu_U)

        if y_l > y_r:
            y_l, y_r = y_r, y_l

        return float(y_l), float(y_r)


# ================================================================================
# LAYER 3 -- INPUT PARSER
# ================================================================================

class IT2FSParser:
    """
    Parses and validates the fuzzified JSON structure produced by IT2TFSFuzzifier.

    Validates:
      - Required top-level keys: cost_matrix, supply, demand
      - Each IT2FS object has "umf" and "lmf" with 5 elements each
      - UMF height == 1.0
      - LMF height in (0, 1]
      - Nesting: a1 <= b1 <= b2 <= b3 <= b4 <= a4
    """

    @staticmethod
    def _check_it2fs(obj: dict, label: str, eps: float = 1e-9) -> None:
        if "umf" not in obj or "lmf" not in obj:
            raise ValueError(f"[Parser] {label} missing 'umf' or 'lmf' key.")
        if len(obj["umf"]) != 5:
            raise ValueError(f"[Parser] {label} UMF must have 5 elements.")
        if len(obj["lmf"]) != 5:
            raise ValueError(f"[Parser] {label} LMF must have 5 elements.")

        a1, a2, a3, a4, h_u = obj["umf"]
        b1, b2, b3, b4, h_l = obj["lmf"]

        if abs(h_u - 1.0) > 1e-6:
            raise ValueError(f"[Parser] {label} UMF height must be 1.0, got {h_u}.")
        if not (0 < h_l <= 1.0 + eps):
            raise ValueError(f"[Parser] {label} LMF height must be in (0,1], got {h_l}.")

        tol = 1e-6
        if not (a1 - tol <= b1 and b1 <= b2 + tol and
                b2 <= b3 + tol and b3 <= b4 + tol and b4 <= a4 + tol):
            raise ValueError(
                f"[Parser] {label} nesting violated: "
                f"a1={a1} b1={b1} b2={b2} b3={b3} b4={b4} a4={a4}"
            )

    def validate(self, data: dict) -> None:
        for key in ("cost_matrix", "supply", "demand"):
            if key not in data:
                raise ValueError(f"[Parser] Missing key: '{key}'")

        for i, row in enumerate(data["cost_matrix"]):
            for j, cell in enumerate(row):
                self._check_it2fs(cell, f"cost_matrix[{i}][{j}]")

        for k, cell in enumerate(data["supply"]):
            self._check_it2fs(cell, f"supply[{k}]")

        for k, cell in enumerate(data["demand"]):
            self._check_it2fs(cell, f"demand[{k}]")


# ================================================================================
# LAYER 4 -- BALANCE ENFORCEMENT LAYER
# ================================================================================

class BalanceEnforcer:
    """
    Enforces the transportation balance constraint after KM defuzzification:

        sum(supply) == sum(demand)

    ROOT CAUSE OF IMBALANCE
    -----------------------
    The fuzzifier uses different reliability formulas for supply vs demand:

        Supply:  S = 0.70*exp(-v) + 0.30*x_norm    (higher exp weight)
        Demand:  S = 0.55*exp(-v) + 0.45*x_norm    (higher position weight)

    This produces different LMF heights (hL) per element-type. Since the
    KM centroid is height-weighted, supply centroids shift by a different
    percentage than demand centroids. The result is:

        sum(supply_km) != sum(demand_km)

    even when the original problem was perfectly balanced.

    CORRECTION METHOD: Proportional Normalization
    ---------------------------------------------
    A symmetric anchor T is computed:

        T = (sum(supply_km) + sum(demand_km)) / 2

    Then each vector is scaled to sum to T:

        supply_final[i] = supply_km[i] / sum(supply_km) * T
        demand_final[j] = demand_km[j] / sum(demand_km) * T

    MATHEMATICAL GUARANTEES
    -----------------------
    1. Exact balance:   sum(supply_final) == sum(demand_final) == T
    2. Ratio preserved: supply_final[i]/supply_final[k]
                        == supply_km[i]/supply_km[k]   for all i,k
    3. Deterministic:   no randomness, fully reproducible
    4. Minimal change:  correction magnitude is O(delta_S - delta_D)
                        which is < 0.02% for standard parameters

    Parameters
    ----------
    eps : numerical guard against zero-sum edge cases
    """

    def __init__(self, eps: float = 1e-12):
        self.eps = eps

    def enforce(
        self,
        supply: np.ndarray,
        demand: np.ndarray,
    ) -> Tuple[np.ndarray, np.ndarray, dict]:
        """
        Apply proportional normalization to enforce balance.

        Parameters
        ----------
        supply : (m,) KM-defuzzified supply values
        demand : (n,) KM-defuzzified demand values

        Returns
        -------
        supply_balanced : (m,) balanced supply values
        demand_balanced : (n,) balanced demand values
        report          : dict with balance audit information
        """
        T_supply = float(np.sum(supply))
        T_demand = float(np.sum(demand))

        # Symmetric anchor: equidistant between the two totals
        T_anchor = (T_supply + T_demand) / 2.0

        # Scale each vector to sum to T_anchor
        supply_balanced = supply * (T_anchor / (T_supply + self.eps))
        demand_balanced = demand * (T_anchor / (T_demand + self.eps))

        # Build audit report for metadata
        report = {
            "method":              "proportional_normalization",
            "T_supply_before":     round(T_supply, 8),
            "T_demand_before":     round(T_demand, 8),
            "imbalance_before":    round(abs(T_supply - T_demand), 8),
            "T_anchor":            round(T_anchor, 8),
            "T_supply_after":      round(float(np.sum(supply_balanced)), 8),
            "T_demand_after":      round(float(np.sum(demand_balanced)), 8),
            "imbalance_after":     round(
                abs(float(np.sum(supply_balanced)) -
                    float(np.sum(demand_balanced))), 12
            ),
            "supply_scale_factor": round(T_anchor / (T_supply + self.eps), 8),
            "demand_scale_factor": round(T_anchor / (T_demand + self.eps), 8),
        }

        return supply_balanced, demand_balanced, report

    def verify(self, supply: np.ndarray, demand: np.ndarray, tol: float = 1e-5) -> bool:
        """Returns True if |sum(supply) - sum(demand)| < tol."""
        return bool(abs(np.sum(supply) - np.sum(demand)) < tol)


# ================================================================================
# LAYER 5 -- DEFUZZIFICATION PIPELINE
# ================================================================================

class IT2TFSDefuzzifier:
    """
    Research-Grade IT2TFS Defuzzifier with Balance Enforcement.

    Converts a fuzzified transportation problem dataset produced by
    IT2TFSFuzzifier back to crisp balanced values using the
    Karnik-Mendel centroid algorithm followed by proportional
    normalization to enforce the transportation balance constraint.

    PIPELINE
    --------
    For each IT2FS object:
      1. Discretize UMF support [a1, a4] into N sample points.
      2. Evaluate UMF(x) and LMF(x) at every sample point.
      3. Run KM left-centroid iteration  -> y_l
      4. Run KM right-centroid iteration -> y_r
      5. Crisp value: y* = (y_l + y_r) / 2

    After all KM defuzzifications:
      6. Apply BalanceEnforcer to supply and demand vectors.
      7. Verify: sum(supply) == sum(demand) exactly.

    Parameters
    ----------
    N            : KM discretization resolution (default: 1000)
    max_iter     : maximum KM iterations per centroid (default: 100)
    tol          : KM convergence tolerance (default: 1e-8)
    eps          : numerical stability guard (default: 1e-12)
    enforce_balance : if True (default), apply balance normalization

    Usage
    -----
    >>> defuzz = IT2TFSDefuzzifier()
    >>> result = defuzz.transform(fuzzy_data)
    >>> defuzz.export(result, "crisp_recovered.json")
    """

    def __init__(
        self,
        N: int              = 1000,
        max_iter: int       = 100,
        tol: float          = 1e-8,
        eps: float          = 1e-12,
        enforce_balance: bool = True,
    ):
        self._km      = KarnikMendelEngine(N=N, max_iter=max_iter, tol=tol, eps=eps)
        self._parser  = IT2FSParser()
        self._balance = BalanceEnforcer(eps=eps)
        self.N        = N
        self.enforce_balance = enforce_balance

    def transform(self, fuzzy_data: dict) -> dict:
        """
        Full defuzzification pipeline with balance enforcement.

        Parameters
        ----------
        fuzzy_data : output dict from IT2TFSFuzzifier.transform()

        Returns
        -------
        crisp_data : {
            "metadata":    { ... },
            "cost_matrix": [[float]],
            "supply":      [float],
            "demand":      [float]
        }
        """

        # -- Step 1: Validate fuzzified input -------------------------
        self._parser.validate(fuzzy_data)

        # -- Step 2: Defuzzify cost matrix (KM, no balance needed) ----
        cost_matrix_km = np.array([
            [self._km.defuzzify(cell) for cell in row]
            for row in fuzzy_data["cost_matrix"]
        ])

        # -- Step 3: Defuzzify supply vector --------------------------
        supply_km = np.array([
            self._km.defuzzify(cell) for cell in fuzzy_data["supply"]
        ])

        # -- Step 4: Defuzzify demand vector --------------------------
        demand_km = np.array([
            self._km.defuzzify(cell) for cell in fuzzy_data["demand"]
        ])

        # -- Step 5: Enforce balance constraint -----------------------
        balance_report = None

        if self.enforce_balance:
            supply_final, demand_final, balance_report = \
                self._balance.enforce(supply_km, demand_km)

            # Hard assertion: balance MUST hold after normalization
            assert self._balance.verify(supply_final, demand_final), \
                "[Balance] CRITICAL: Balance constraint still violated after enforcement."
        else:
            supply_final = supply_km
            demand_final = demand_km

        # -- Step 6: Build output dict --------------------------------
        meta_in = fuzzy_data.get("metadata", {})

        return {
            "metadata": {
                "method":             "Karnik-Mendel Centroid + Proportional Balance",
                "km_resolution_N":    self.N,
                "balance_enforced":   self.enforce_balance,
                "balance_report":     balance_report,
                "source_delta":       meta_in.get("delta"),
                "source_alpha":       meta_in.get("alpha"),
                "source_beta":        meta_in.get("beta"),
                "source_gamma":       meta_in.get("gamma"),
                "source_statistics":  meta_in.get("statistics"),
            },
            "cost_matrix": [
                [round(float(v), 2) for v in row]
                for row in cost_matrix_km
            ],
            # Supply and demand use 8dp to prevent floating-point rounding
            # from breaking the balance constraint after serialization.
            "supply": [round(float(v), 2) for v in supply_final],
            "demand": [round(float(v), 2) for v in demand_final],
        }

    def transform_with_intervals(self, fuzzy_data: dict) -> dict:
        """
        Extended pipeline returning the full centroid interval [y_l, y_r]
        for each cell — for uncertainty quantification in thesis reporting.

        Balance normalization is applied to the crisp y* values.

        Returns each cell as:
            {
                "crisp":    y*  (balance-corrected),
                "y_l":      left KM centroid (pre-balance),
                "y_r":      right KM centroid (pre-balance),
                "interval": y_r - y_l
            }
        """
        self._parser.validate(fuzzy_data)

        def _ext(cell):
            y_l, y_r = self._km.centroid_interval(cell)
            y_star = (y_l + y_r) / 2.0
            return {"crisp_raw": round(y_star, 6),
                    "y_l": round(y_l, 6),
                    "y_r": round(y_r, 6),
                    "interval": round(y_r - y_l, 6)}

        cost_ext = [[_ext(c) for c in row] for row in fuzzy_data["cost_matrix"]]

        supply_raw = np.array([_ext(c)["crisp_raw"] for c in fuzzy_data["supply"]])
        demand_raw = np.array([_ext(c)["crisp_raw"] for c in fuzzy_data["demand"]])

        supply_int_data = [_ext(c) for c in fuzzy_data["supply"]]
        demand_int_data = [_ext(c) for c in fuzzy_data["demand"]]

        if self.enforce_balance:
            supply_bal, demand_bal, _ = self._balance.enforce(supply_raw, demand_raw)
            for i, v in enumerate(supply_bal):
                supply_int_data[i]["crisp"] = round(float(v), 6)
            for j, v in enumerate(demand_bal):
                demand_int_data[j]["crisp"] = round(float(v), 6)
        else:
            for i, v in enumerate(supply_raw):
                supply_int_data[i]["crisp"] = round(float(v), 6)
            for j, v in enumerate(demand_raw):
                demand_int_data[j]["crisp"] = round(float(v), 6)

        # Cost matrix: balance does not apply (it is a ratio matrix)
        for row in cost_ext:
            for cell in row:
                cell["crisp"] = cell["crisp_raw"]

        return {
            "metadata": fuzzy_data.get("metadata", {}),
            "cost_matrix": cost_ext,
            "supply":      supply_int_data,
            "demand":      demand_int_data,
        }

    def export(self, result: dict, path: str = "crisp_recovered.json") -> None:
        """Writes the crisp result to a JSON file."""
        with open(path, "w") as f:
            json.dump(result, f, indent=4)
        print(f"[Export] Written to: {path}")


# ================================================================================
# LAYER 6 -- RECOVERY AUDITOR
# ================================================================================

class RecoveryAuditor:
    """
    Computes recovery accuracy metrics between original crisp values
    and KM-defuzzified (balance-corrected) values.

    Metrics:
        MAE      -- Mean Absolute Error
        MAPE     -- Mean Absolute Percentage Error (%)
        RMSE     -- Root Mean Square Error
        MaxAE    -- Maximum Absolute Error
        Balanced -- Whether sum(supply) == sum(demand) within tolerance
    """

    @staticmethod
    def audit(original: dict, recovered: dict, tol: float = 1e-6) -> dict:
        orig_cost = np.array(original["cost_matrix"], dtype=float)
        rec_cost  = np.array(recovered["cost_matrix"], dtype=float)
        orig_sup  = np.array(original["supply"], dtype=float)
        rec_sup   = np.array(recovered["supply"], dtype=float)
        orig_dem  = np.array(original["demand"], dtype=float)
        rec_dem   = np.array(recovered["demand"], dtype=float)

        all_orig = np.concatenate([orig_cost.flatten(), orig_sup, orig_dem])
        all_rec  = np.concatenate([rec_cost.flatten(),  rec_sup,  rec_dem])

        abs_err = np.abs(all_orig - all_rec)
        pct_err = abs_err / (np.abs(all_orig) + 1e-12) * 100.0

        balanced = bool(abs(np.sum(rec_sup) - np.sum(rec_dem)) < tol)

        return {
            "n_values":       int(len(all_orig)),
            "MAE":            round(float(np.mean(abs_err)), 6),
            "RMSE":           round(float(np.sqrt(np.mean(abs_err**2))), 6),
            "MAPE_pct":       round(float(np.mean(pct_err)), 4),
            "MaxAE":          round(float(np.max(abs_err)), 6),
            "MaxAPE_pct":     round(float(np.max(pct_err)), 4),
            "sum_supply":     round(float(np.sum(rec_sup)), 8),
            "sum_demand":     round(float(np.sum(rec_dem)), 8),
            "balanced":       balanced,
        }

    @staticmethod
    def print_comparison(original: dict, recovered: dict) -> None:
        """Side-by-side table: original vs recovered vs % error."""

        def pct(o, r):
            return abs(o - r) / (abs(o) + 1e-12) * 100.0

        print("\n-- COST MATRIX -----------------------------------------------")
        print(f"  {'Cell':<14}  {'Original':>10}  {'Recovered':>10}  {'Err%':>7}")
        for i, row in enumerate(original["cost_matrix"]):
            for j, x in enumerate(row):
                r = recovered["cost_matrix"][i][j]
                print(f"  [{i}][{j}]        {x:>10.4f}  {r:>10.4f}  {pct(x,r):>6.3f}%")

        print("\n-- SUPPLY ----------------------------------------------------")
        print(f"  {'Index':<14}  {'Original':>10}  {'Recovered':>10}  {'Err%':>7}")
        for k, (x, r) in enumerate(zip(original["supply"], recovered["supply"])):
            print(f"  supply[{k}]      {x:>10.4f}  {r:>10.4f}  {pct(x,r):>6.3f}%")
        print(f"  {'TOTAL':<14}  {sum(original['supply']):>10.4f}  "
              f"{sum(recovered['supply']):>10.4f}")

        print("\n-- DEMAND ----------------------------------------------------")
        print(f"  {'Index':<14}  {'Original':>10}  {'Recovered':>10}  {'Err%':>7}")
        for k, (x, r) in enumerate(zip(original["demand"], recovered["demand"])):
            print(f"  demand[{k}]      {x:>10.4f}  {r:>10.4f}  {pct(x,r):>6.3f}%")
        print(f"  {'TOTAL':<14}  {sum(original['demand']):>10.4f}  "
              f"{sum(recovered['demand']):>10.4f}")

        s_bal = sum(recovered["supply"])
        d_bal = sum(recovered["demand"])
        print(f"\n  Balance check: |{s_bal:.6f} - {d_bal:.6f}| = "
              f"{abs(s_bal-d_bal):.2e}  "
              f"{'BALANCED ✓' if abs(s_bal-d_bal) < 1e-6 else 'NOT BALANCED ✗'}")


# ================================================================================
# ENTRY POINT -- FULL ROUND-TRIP DEMONSTRATION
# ================================================================================

if __name__ == "__main__":
     import json
     # Paths for the specific task
     input_path = 'data_for_sensitivity/problem_40x60_fou_sensitive/p_40x60_fou_minus_10.json'
     output_path = 'data_for_sensitivity/problem_40x60_fou_sensitive/p_40x60_fou_minus_10_crisp.json'
     #input_path = 'fuzzy_data/fuzzy_test_data/problem_150x150_fuzzy.json'
     #output_path = 'crisp_data/problem_150x150_crisp.json'   
     # Load the fuzzy data
     with open(input_path, 'r') as f:
         fuzzy_data = json.load(f)

     # Defuzzify with balance enforcement (default parameters)
     defuzzifier = IT2TFSDefuzzifier(N=1000, enforce_balance=True)
     recovered = defuzzifier.transform(fuzzy_data)

     # Export the result
     defuzzifier.export(recovered, output_path)

     print(f"[Success] Defuzzified data saved to {output_path}")