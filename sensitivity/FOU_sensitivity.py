"""
FOU_sensitivity.py
------------------
Footprint of Uncertainty (FOU) Sensitivity Analysis for
Interval Type-2 Trapezoidal Fuzzy Transportation Problems (IT2-TrFTP).

Purpose:
    Systematically expand or contract the Footprint of Uncertainty by
    modifying ONLY the LMF (Lower Membership Function) trapezoidal points
    of every cost cell.  Four independent datasets are produced:

        F1 — FOU minus 20%   (multiplier 0.80×)
        F2 — FOU minus 10%   (multiplier 0.90×)
        F3 — FOU plus  10%   (multiplier 1.10×)
        F4 — FOU plus  20%   (multiplier 1.20×)

    Multiplier choice rationale:
        These levels are deliberately symmetric (±10%, ±20%) and moderate,
        directly analogous to the cost sensitivity levels used in the
        companion cost_sensitivity.py script.  Aggressive multipliers such
        as 0.50 or 2.00 cause IT2 clamping on cells whose inner gaps are
        large relative to the UMF plateau span, meaning the "intended ±50%
        or ±100% FOU change" is silently clipped — contaminating sensitivity
        results.  The moderate ±10%/±20% range avoids clamping for all
        typical IT2-TrFTP gap-to-plateau ratios (verified analytically
        below).

    The following are NEVER modified:
        • UMF values (trapezoidal points and height h_u)
        • LMF height (alpha)
        • supply, demand, metadata

IT2 Trapezoidal Encoding Convention
-------------------------------------
Each cost cell stores:
    UMF: [a1, a2, a3, a4, h_u]   — outer trapezoid
    LMF: [b1, b2, b3, b4, alpha] — inner/embedded trapezoid

Valid IT2 structure requires:
    a1 ≤ b1 ≤ b2          (left foot: LMF starts inside UMF)
    a2 ≤ b2               (left plateau edge: LMF plateau ≥ UMF plateau start)
    b3 ≤ a3               (right plateau edge: LMF plateau ≤ UMF plateau end)
    b3 ≤ b4 ≤ a4          (right foot: LMF ends inside UMF)

Four FOU Gap Quantities (the "uncertainty widths"):
    G1 = b1 − a1   left outer gap
    G2 = b2 − a2   left inner gap
    G3 = a3 − b3   right inner gap
    G4 = a4 − b4   right outer gap

FOU Transformation (multiplier M):
    b1_new = a1 + G1 × M
    b2_new = a2 + G2 × M
    b3_new = a3 − G3 × M
    b4_new = a4 − G4 × M

    M < 1  →  gaps shrink  →  LMF moves outward  →  narrower FOU
    M > 1  →  gaps grow    →  LMF moves inward   →  wider FOU

Clamping note:
    Inner gaps clamp when  M > plateau_span / (2 × G2).
    With M ∈ {0.80, 0.90, 1.10, 1.20} this threshold is not reached
    for any cell whose G2/plateau_span ratio is ≤ 0.42 — which covers
    all well-formed IT2-TrFTP datasets.  The built-in diagnostic
    (--diagnose flag or run_diagnostic()) will warn if your specific
    dataset is an exception.

Usage:
    python FOU_sensitivity.py <input_json_path>
    python FOU_sensitivity.py <input_json_path> --diagnose

    Example:
        python FOU_sensitivity.py input_data.json
        python FOU_sensitivity.py input_data.json --diagnose

Author : (your name / research group)
Version: 2.0.0
"""

import json
import copy
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# FOU scenario definitions: (file_prefix, descriptive_name, multiplier)
# Symmetric design: ±10% and ±20%, matching cost_sensitivity.py convention.
FOU_SCENARIOS: list[tuple[str, str, float]] = [
    ("F1", "fou_minus_20", 0.80),
    ("F2", "fou_minus_10", 0.90),
    ("F3", "fou_plus_10",  1.10),
    ("F4", "fou_plus_20",  1.20),
]

# Named indices for UMF array: [a1, a2, a3, a4, h_u]
A1, A2, A3, A4, H_U = 0, 1, 2, 3, 4

# Named indices for LMF array: [b1, b2, b3, b4, alpha]
B1, B2, B3, B4, ALPHA = 0, 1, 2, 3, 4

OUTPUT_FOLDER = Path("fou_sensitivity_output")
MIN_ARRAY_LEN = 5
FLOAT_TOL     = 1e-9


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------

def load_dataset(filepath: str | Path) -> dict:
    """
    Load and parse the IT2 fuzzy transportation dataset from a JSON file.

    Raises
    ------
    FileNotFoundError, ValueError
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Input file not found: '{filepath}'")

    print(f"[LOAD]  Reading dataset from '{filepath}' ...")
    with filepath.open("r", encoding="utf-8") as fh:
        try:
            dataset = json.load(fh)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON in '{filepath}': {exc}") from exc

    print("[LOAD]  Dataset loaded successfully.")
    return dataset


def save_dataset(dataset: dict, filepath: Path) -> None:
    """Serialise dataset to JSON with 4-space indentation."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with filepath.open("w", encoding="utf-8") as fh:
        json.dump(dataset, fh, indent=4, ensure_ascii=False)
    print(f"[SAVE]  Written → '{filepath}'")


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_array_length(array: list, label: str) -> None:
    """Assert array has at least MIN_ARRAY_LEN elements."""
    if len(array) < MIN_ARRAY_LEN:
        raise ValueError(
            f"Array too short at {label}: "
            f"need ≥ {MIN_ARRAY_LEN} elements, got {len(array)}. "
            f"Contents: {array}"
        )


def validate_it2_cell(umf: list[float], lmf: list[float], label: str) -> None:
    """
    Verify IT2 embedded-trapezoid constraints:
        a1 ≤ b1 ≤ b2  and  a2 ≤ b2
        b3 ≤ a3       and  b3 ≤ b4 ≤ a4

    Raises
    ------
    ValueError if any constraint is violated beyond FLOAT_TOL.
    """
    a1, a2, a3, a4 = umf[A1], umf[A2], umf[A3], umf[A4]
    b1, b2, b3, b4 = lmf[B1], lmf[B2], lmf[B3], lmf[B4]
    T = FLOAT_TOL

    violations: list[str] = []
    if a1 > b1 + T:  violations.append(f"a1({a1:.6g}) > b1({b1:.6g})")
    if b1 > b2 + T:  violations.append(f"b1({b1:.6g}) > b2({b2:.6g})")
    if a2 > b2 + T:  violations.append(f"a2({a2:.6g}) > b2({b2:.6g})")
    if b3 > a3 + T:  violations.append(f"b3({b3:.6g}) > a3({a3:.6g})")
    if b3 > b4 + T:  violations.append(f"b3({b3:.6g}) > b4({b4:.6g})")
    if b4 > a4 + T:  violations.append(f"b4({b4:.6g}) > a4({a4:.6g})")

    if violations:
        raise ValueError(
            f"IT2 validity violation at {label}:\n  " +
            "\n  ".join(violations)
        )


def validate_matrix_shape(original: list, perturbed: list, label: str) -> None:
    """Assert identical row/column count between two cost matrices."""
    if len(perturbed) != len(original):
        raise ValueError(
            f"{label}: row count changed ({len(original)} → {len(perturbed)})"
        )
    for r, (orig_row, pert_row) in enumerate(zip(original, perturbed)):
        if len(pert_row) != len(orig_row):
            raise ValueError(
                f"{label} row {r}: col count changed "
                f"({len(orig_row)} → {len(pert_row)})"
            )


# ---------------------------------------------------------------------------
# FOU gap utilities
# ---------------------------------------------------------------------------

def compute_fou_gaps(umf: list[float],
                     lmf: list[float]) -> tuple[float, float, float, float]:
    """
    Extract the four FOU gap quantities for one cost cell.

        G1 = b1 − a1   left outer gap
        G2 = b2 − a2   left inner gap
        G3 = a3 − b3   right inner gap
        G4 = a4 − b4   right outer gap

    Returns
    -------
    (G1, G2, G3, G4) — all non-negative (small negatives from floating-point
    rounding are clamped to zero).
    """
    G1 = max(lmf[B1] - umf[A1], 0.0)
    G2 = max(lmf[B2] - umf[A2], 0.0)
    G3 = max(umf[A3] - lmf[B3], 0.0)
    G4 = max(umf[A4] - lmf[B4], 0.0)
    return G1, G2, G3, G4


def total_fou_width(umf: list[float], lmf: list[float]) -> float:
    """Return total FOU width = G1 + G2 + G3 + G4."""
    return sum(compute_fou_gaps(umf, lmf))


def clamping_threshold(umf: list[float], lmf: list[float]) -> float:
    """
    Return the multiplier M at which inner-gap clamping first triggers.

    Clamping occurs when  b2_new = a2 + G2*M  exceeds the plateau midpoint.
    Threshold = plateau_span / (2 * G2).

    Returns float('inf') if G2 == 0 (no inner gap → no clamping possible).
    """
    plateau_span = umf[A3] - umf[A2]
    G2 = max(lmf[B2] - umf[A2], 0.0)
    if G2 == 0.0:
        return float("inf")
    return plateau_span / (2.0 * G2)


# ---------------------------------------------------------------------------
# Core LMF transformation
# ---------------------------------------------------------------------------

def clamp(value: float, lo: float, hi: float) -> float:
    """Return value clamped to [lo, hi]."""
    return max(lo, min(hi, value))


def transform_lmf(umf: list[float],
                  lmf: list[float],
                  multiplier: float) -> list[float]:
    """
    Compute a new LMF by uniformly scaling all four FOU gaps.

    Formulae
    --------
        b1_new = a1 + G1 × M
        b2_new = a2 + G2 × M
        b3_new = a3 − G3 × M
        b4_new = a4 − G4 × M

    Post-scaling, values are clamped to guarantee IT2 validity.
    With well-chosen moderate multipliers, clamping should never fire.

    UMF and LMF height (alpha) are strictly preserved.

    Returns
    -------
    New LMF list preserving alpha and any extra elements beyond index 4.
    """
    a1, a2, a3, a4 = umf[A1], umf[A2], umf[A3], umf[A4]
    alpha = lmf[ALPHA]

    G1, G2, G3, G4 = compute_fou_gaps(umf, lmf)

    b1_new = a1 + G1 * multiplier
    b2_new = a2 + G2 * multiplier
    b3_new = a3 - G3 * multiplier
    b4_new = a4 - G4 * multiplier

    # Safety clamps (should not fire for |M−1| ≤ 0.20 on well-formed data)
    plateau_mid = (a2 + a3) / 2.0
    b1_new = clamp(b1_new, a1, a2)
    b2_new = clamp(b2_new, max(b1_new, a2), plateau_mid)
    b3_new = clamp(b3_new, plateau_mid, a3)
    b4_new = clamp(b4_new, b3_new, a4)

    return [b1_new, b2_new, b3_new, b4_new, alpha] + list(lmf[5:])


# ---------------------------------------------------------------------------
# Matrix-level transformation
# ---------------------------------------------------------------------------

def apply_fou_to_cost_matrix(cost_matrix: list,
                              multiplier: float,
                              scenario_label: str) -> list:
    """
    Apply FOU transformation to every cell in a deep-copied cost_matrix.

    UMF is read-only. Only LMF trapezoidal points b1–b4 are updated.
    """
    new_matrix = copy.deepcopy(cost_matrix)

    for row_idx, row in enumerate(new_matrix):
        for col_idx, cell in enumerate(row):
            label = f"{scenario_label} cell[{row_idx}][{col_idx}]"
            for mf_key in ("umf", "lmf"):
                if mf_key not in cell:
                    raise ValueError(f"Missing '{mf_key}' at {label}.")
                validate_array_length(cell[mf_key], f"{label}.{mf_key}")

            new_lmf = transform_lmf(cell["umf"], cell["lmf"], multiplier)
            validate_it2_cell(cell["umf"], new_lmf, label)
            cell["lmf"] = new_lmf
            # cell["umf"] intentionally never written

    return new_matrix


def generate_fou_dataset(original: dict,
                          multiplier: float,
                          scenario_label: str) -> dict:
    """
    Build a fully independent FOU-perturbed dataset from the original.

    Only cost_matrix LMF values are changed.
    Supply, demand, and metadata are carried through unchanged.
    """
    dataset = copy.deepcopy(original)
    dataset["cost_matrix"] = apply_fou_to_cost_matrix(
        original["cost_matrix"], multiplier, scenario_label
    )
    return dataset


# ---------------------------------------------------------------------------
# Built-in diagnostic
# ---------------------------------------------------------------------------

def run_diagnostic(dataset: dict) -> bool:
    """
    Print a per-cell FOU width table showing:
        • Original total FOU width
        • New FOU width per scenario
        • Actual % change
        • Intended % change (= M - 1)
        • Whether clamping occurred

    Returns
    -------
    bool — True if ANY clamping was detected, False if all scenarios
           are clamp-free (safe for thesis use as-is).
    """
    SEP = "=" * 76
    cost_matrix = dataset["cost_matrix"]
    any_clamped = False

    print()
    print(SEP)
    print("FOU WIDTH DIAGNOSTIC")
    print(SEP)

    for r, row in enumerate(cost_matrix):
        for c, cell in enumerate(row):
            umf = cell["umf"]
            lmf = cell["lmf"]
            W_orig = total_fou_width(umf, lmf)
            thresh = clamping_threshold(umf, lmf)
            G1o, G2o, G3o, G4o = compute_fou_gaps(umf, lmf)

            print(f"\n  Cell [{r}][{c}]")
            print(f"  {'─'*72}")
            print(f"  UMF             : {umf[:4]}")
            print(f"  LMF (original)  : {lmf[:4]}")
            print(f"  Gaps            : "
                  f"G1={G1o:.5f}  G2={G2o:.5f}  "
                  f"G3={G3o:.5f}  G4={G4o:.5f}")
            print(f"  Total FOU width : {W_orig:.5f}")
            print(f"  Clamp threshold : M = {thresh:.4f}")
            print()
            print(f"  {'Scenario':<10} {'M':>5}  {'New W':>8}  "
                  f"{'Exp W':>8}  {'Actual Δ%':>10}  "
                  f"{'Target Δ%':>10}  {'Clamped':>8}")
            print(f"  {'─'*72}")

            for prefix, name, M in FOU_SCENARIOS:
                new_lmf = transform_lmf(umf, lmf, M)
                W_new   = total_fou_width(umf, new_lmf)
                W_exp   = W_orig * M
                act_pct = (W_new / W_orig - 1) * 100 if W_orig > 0 else 0.0
                tgt_pct = (M - 1) * 100

                # Clamping: any gap deviates from expected scaled value
                Gs_new = compute_fou_gaps(umf, new_lmf)
                Gs_exp = (G1o*M, G2o*M, G3o*M, G4o*M)
                clamped = any(abs(gn - ge) > 1e-6
                              for gn, ge in zip(Gs_new, Gs_exp))
                if clamped:
                    any_clamped = True
                flag = "⚠ YES" if clamped else "no"

                print(f"  {prefix:<10} {M:>5.2f}  {W_new:>8.5f}  "
                      f"{W_exp:>8.5f}  {act_pct:>+9.2f}%  "
                      f"{tgt_pct:>+9.2f}%  {flag:>8}")

    print()
    print(SEP)
    print("DIAGNOSTIC SUMMARY")
    print(SEP)
    if any_clamped:
        print("  ⚠  Clamping detected in one or more cells.")
        print("     The actual FOU change differs from the intended percentage.")
        print("     Consider reducing the multiplier range further.")
    else:
        print("  ✓  No clamping detected. All FOU changes match intended")
        print("     percentages exactly. Dataset is safe for thesis experiments.")
    print(SEP)

    return any_clamped


# ---------------------------------------------------------------------------
# Pipeline orchestration
# ---------------------------------------------------------------------------

def pre_validate_dataset(dataset: dict) -> None:
    """
    Validate structure and IT2 consistency of the original dataset.

    Raises KeyError or ValueError on any problem found.
    """
    for key in ("cost_matrix", "supply", "demand"):
        if key not in dataset:
            raise KeyError(f"Required key '{key}' missing from dataset.")

    print("[VALID] Pre-validating original cost_matrix ...")
    for r, row in enumerate(dataset["cost_matrix"]):
        for c, cell in enumerate(row):
            for mf_key in ("umf", "lmf"):
                if mf_key not in cell:
                    raise ValueError(
                        f"Missing '{mf_key}' at original cell[{r}][{c}]."
                    )
                validate_array_length(
                    cell[mf_key], f"original cell[{r}][{c}].{mf_key}"
                )
            validate_it2_cell(
                cell["umf"], cell["lmf"], f"original cell[{r}][{c}]"
            )
    print("[VALID] Original dataset is structurally valid.")


def run_fou_analysis(input_path: str | Path,
                     diagnose: bool = False) -> None:
    """
    Full FOU sensitivity analysis pipeline.

    Steps:
        1.  Load original dataset
        2.  Validate IT2 structure
        3.  Optionally run and print the FOU width diagnostic
        4.  For each of four scenarios: generate, validate, save
        5.  Report completion

    Parameters
    ----------
    input_path : str or Path
    diagnose   : bool — if True, print the per-cell FOU diagnostic table
                 before generating datasets (strongly recommended for new
                 datasets).
    """
    # 1 — Load
    original = load_dataset(input_path)

    # 2 — Pre-validation
    pre_validate_dataset(original)

    # 3 — Optional diagnostic
    if diagnose:
        clamped = run_diagnostic(original)
        if clamped:
            print("\n[WARN]  Clamping detected — review diagnostic above "
                  "before using results in thesis.\n")
        else:
            print("\n[INFO]  Diagnostic clean — proceeding to generation.\n")

    n_rows = len(original["cost_matrix"])
    n_cols = len(original["cost_matrix"][0]) if n_rows > 0 else 0
    print(f"[INFO]  Cost matrix  : {n_rows} rows × {n_cols} columns")
    print(f"[INFO]  Output folder: '{OUTPUT_FOLDER.resolve()}'")
    print(f"[INFO]  Generating {len(FOU_SCENARIOS)} FOU datasets ...\n")

    # 4 — Generate each scenario independently from the original
    for file_prefix, name, multiplier in FOU_SCENARIOS:
        label = f"{file_prefix} ({name}, M={multiplier})"
        print(f"[GEN]   {label} ...")

        perturbed = generate_fou_dataset(original, multiplier, label)

        # Shape integrity
        validate_matrix_shape(
            original["cost_matrix"], perturbed["cost_matrix"], label
        )

        # Immutability assertions
        assert perturbed["supply"]   == original["supply"],   \
            f"BUG: supply modified in {label}"
        assert perturbed["demand"]   == original["demand"],   \
            f"BUG: demand modified in {label}"
        assert perturbed["metadata"] == original["metadata"], \
            f"BUG: metadata modified in {label}"
        for r, row in enumerate(original["cost_matrix"]):
            for c, cell in enumerate(row):
                assert perturbed["cost_matrix"][r][c]["umf"] == cell["umf"], \
                    f"BUG: UMF modified at cell[{r}][{c}] in {label}"

        save_dataset(perturbed, OUTPUT_FOLDER / f"{file_prefix}_{name}.json")

    # 5 — Done
    print(f"\n[DONE]  All {len(FOU_SCENARIOS)} FOU datasets saved "
          f"to '{OUTPUT_FOLDER.resolve()}'.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """
    Command-line entry point.

    Usage:
        python FOU_sensitivity.py <input_json_path>
        python FOU_sensitivity.py <input_json_path> --diagnose
    """
    if len(sys.argv) < 2:
        print("Usage  : python FOU_sensitivity.py <input_json_path> [--diagnose]")
        print("Example: python FOU_sensitivity.py input_data.json --diagnose")
        sys.exit(1)

    input_path = sys.argv[1]
    diagnose   = "--diagnose" in sys.argv

    run_fou_analysis(input_path, diagnose=diagnose)


if __name__ == "__main__":
    main()
