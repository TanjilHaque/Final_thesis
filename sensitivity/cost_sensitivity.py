"""
cost_sensitivity.py
--------------------
Cost Magnitude Sensitivity Analysis for
Interval Type-2 Trapezoidal Fuzzy Transportation Problems (IT2-TrFTP).

Purpose:
    Systematically perturb ONLY the trapezoidal numeric points of the
    cost_matrix in a fuzzy transportation dataset, generating four
    independent perturbed datasets:
        - 20%, -10%, +10%, +20%

    Supply, demand, metadata, and all height values (h_u, h_l) are
    left strictly unchanged.

Usage:
    python cost_sensitivity.py <input_json_path> [output_folder]

    Example:
        python cost_sensitivity.py dataset.json generated_datasets/

Author : (your name / research group)
Version: 1.0.0
"""

import json
import copy
import os
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Each perturbation scenario: (label_suffix, scaling_factor)
PERTURBATION_SCENARIOS: list[tuple[str, float]] = [
    ("minus_20", 0.80),
    ("minus_10", 0.90),
    ("plus_10",  1.10),
    ("plus_20",  1.20),
]

# Index of the height element inside a UMF / LMF array  [a1, a2, a3, a4, h]
HEIGHT_INDEX: int = 4

# Minimum required length for a UMF / LMF array
MIN_ARRAY_LENGTH: int = 5


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------

def load_dataset(filepath: str | Path) -> dict:
    """
    Load and return the fuzzy transportation dataset from a JSON file.

    Parameters
    ----------
    filepath : str or Path
        Path to the input JSON file.

    Returns
    -------
    dict
        Parsed dataset dictionary.

    Raises
    ------
    FileNotFoundError
        If the specified file does not exist.
    ValueError
        If the file is not valid JSON.
    """
    filepath = Path(filepath)

    if not filepath.exists():
        raise FileNotFoundError(f"Input file not found: {filepath}")

    print(f"[LOAD]  Reading dataset from '{filepath}' ...")

    with filepath.open("r", encoding="utf-8") as fh:
        try:
            dataset = json.load(fh)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON in '{filepath}': {exc}") from exc

    print(f"[LOAD]  Dataset loaded successfully.")
    return dataset


def save_dataset(dataset: dict, filepath: str | Path) -> None:
    """
    Save a dataset dictionary to a JSON file with 4-space indentation.

    Parameters
    ----------
    dataset : dict
        The dataset to serialise.
    filepath : str or Path
        Destination file path.
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with filepath.open("w", encoding="utf-8") as fh:
        json.dump(dataset, fh, indent=4, ensure_ascii=False)

    print(f"[SAVE]  Written → '{filepath}'")


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_fuzzy_array(array: list, label: str) -> None:
    """
    Verify that a UMF or LMF array contains at least MIN_ARRAY_LENGTH
    elements, preventing accidental truncation of height values.

    Parameters
    ----------
    array : list
        The UMF or LMF numeric array.
    label : str
        Human-readable label used in error messages (e.g. "row 0, col 1, UMF").

    Raises
    ------
    ValueError
        If the array is shorter than MIN_ARRAY_LENGTH.
    """
    if len(array) < MIN_ARRAY_LENGTH:
        raise ValueError(
            f"Array too short at {label}: "
            f"expected at least {MIN_ARRAY_LENGTH} elements, "
            f"got {len(array)}. Array contents: {array}"
        )


def validate_cost_matrix(cost_matrix: list) -> None:
    """
    Walk every cell of the cost_matrix and validate all UMF / LMF arrays.

    Parameters
    ----------
    cost_matrix : list of list of dict
        The nested cost matrix from the dataset.

    Raises
    ------
    ValueError
        If any cell contains a malformed UMF or LMF array.
    """
    for row_idx, row in enumerate(cost_matrix):
        for col_idx, cell in enumerate(row):
            for mf_key in ("umf", "lmf"):
                if mf_key not in cell:
                    raise ValueError(
                        f"Missing '{mf_key}' key at cost_matrix"
                        f"[{row_idx}][{col_idx}]."
                    )
                label = f"cost_matrix[{row_idx}][{col_idx}].{mf_key}"
                validate_fuzzy_array(cell[mf_key], label)


# ---------------------------------------------------------------------------
# Core perturbation logic
# ---------------------------------------------------------------------------

def scale_trapezoidal_points(array: list[float], factor: float) -> list[float]:
    """
    Return a new array where the first four trapezoidal numeric points
    (a1, a2, a3, a4) are scaled by *factor*, while the height value
    at index HEIGHT_INDEX is preserved exactly.

    Parameters
    ----------
    array : list of float
        Original UMF or LMF array  [a1, a2, a3, a4, h, ...].
    factor : float
        Multiplicative scaling factor (e.g. 0.80, 1.10).

    Returns
    -------
    list of float
        New array with scaled trapezoidal points and original height.
    """
    scaled = list(array)  # shallow copy sufficient here (list of numbers)

    # Scale only the four trapezoidal vertices
    for idx in range(HEIGHT_INDEX):           # indices 0, 1, 2, 3
        scaled[idx] = array[idx] * factor

    # Height at HEIGHT_INDEX is intentionally NOT touched.
    # Elements beyond index 4 (if any) are also left unchanged.

    return scaled


def perturb_cost_matrix(cost_matrix: list, factor: float) -> list:
    """
    Return a deep-copied cost_matrix in which every UMF and LMF
    trapezoidal point has been scaled by *factor*.

    Supply, demand, and heights remain untouched because this function
    operates exclusively on the cost_matrix structure.

    Parameters
    ----------
    cost_matrix : list of list of dict
        Original cost matrix (will not be mutated).
    factor : float
        Scaling factor to apply to trapezoidal points.

    Returns
    -------
    list of list of dict
        New perturbed cost matrix.
    """
    # Deep copy guarantees the original dataset is never modified
    perturbed_matrix = copy.deepcopy(cost_matrix)

    for row in perturbed_matrix:
        for cell in row:
            cell["umf"] = scale_trapezoidal_points(cell["umf"], factor)
            cell["lmf"] = scale_trapezoidal_points(cell["lmf"], factor)

    return perturbed_matrix


def generate_perturbed_dataset(original: dict, factor: float) -> dict:
    """
    Create a fully independent perturbed dataset from the original.

    Only cost_matrix trapezoidal points are scaled.
    All other keys (supply, demand, metadata, etc.) are deep-copied
    without modification.

    Parameters
    ----------
    original : dict
        The original fuzzy transportation dataset.
    factor : float
        Scaling factor for the cost perturbation.

    Returns
    -------
    dict
        New dataset with perturbed cost_matrix.
    """
    # Start with a complete deep copy to carry over all unchanged fields
    perturbed = copy.deepcopy(original)

    # Replace only the cost_matrix with the perturbed version
    perturbed["cost_matrix"] = perturb_cost_matrix(original["cost_matrix"], factor)

    return perturbed


# ---------------------------------------------------------------------------
# Pipeline orchestration
# ---------------------------------------------------------------------------

def run_sensitivity_analysis(input_path: str | Path,
                              output_folder: str | Path = "generated_datasets") -> None:
    """
    Full sensitivity analysis pipeline:
        1. Load the original dataset.
        2. Validate the cost_matrix structure.
        3. For each perturbation scenario, generate and save a dataset.

    Parameters
    ----------
    input_path : str or Path
        Path to the original JSON dataset.
    output_folder : str or Path
        Directory in which the perturbed datasets will be saved.
        Created automatically if it does not exist.
    """
    output_folder = Path(output_folder)

    # ------------------------------------------------------------------
    # Step 1 — Load
    # ------------------------------------------------------------------
    dataset = load_dataset(input_path)

    # ------------------------------------------------------------------
    # Step 2 — Validate cost_matrix
    # ------------------------------------------------------------------
    if "cost_matrix" not in dataset:
        raise KeyError("Key 'cost_matrix' is missing from the dataset.")

    print("[VALID] Validating cost_matrix structure ...")
    validate_cost_matrix(dataset["cost_matrix"])
    print("[VALID] Validation passed — all UMF/LMF arrays are well-formed.")

    # ------------------------------------------------------------------
    # Step 3 — Generate perturbed datasets
    # ------------------------------------------------------------------
    print(f"\n[INFO]  Output folder: '{output_folder.resolve()}'")
    print(f"[INFO]  Generating {len(PERTURBATION_SCENARIOS)} perturbed datasets ...\n")

    for label, factor in PERTURBATION_SCENARIOS:
        print(f"[GEN]   Scenario '{label}' (factor = {factor:.2f}) ...")

        perturbed = generate_perturbed_dataset(dataset, factor)

        filename   = f"cost_{label}.json"
        output_path = output_folder / filename

        save_dataset(perturbed, output_path)

    # ------------------------------------------------------------------
    # Done
    # ------------------------------------------------------------------
    print(f"\n[DONE]  All {len(PERTURBATION_SCENARIOS)} perturbed datasets "
          f"saved to '{output_folder.resolve()}'.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """
    Command-line entry point.

    Usage
    -----
        python cost_sensitivity.py <input_json> [output_folder]
    """
    if len(sys.argv) < 2:
        print("Usage: python cost_sensitivity.py <input_json_path> [output_folder]")
        print("Example: python cost_sensitivity.py dataset.json generated_datasets/")
        sys.exit(1)

    input_path    = sys.argv[1]
    output_folder = sys.argv[2] if len(sys.argv) > 2 else "generated_datasets"

    run_sensitivity_analysis(input_path, output_folder)


if __name__ == "__main__":
    main()